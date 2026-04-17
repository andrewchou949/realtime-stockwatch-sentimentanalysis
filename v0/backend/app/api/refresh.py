from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Watchlist
from app.schemas import RefreshResult
from app.services.alerts import apply_quote_to_watchlist, build_watchlist_response
from app.services.price_provider import (
    PriceProviderError,
    StooqPriceProvider,
    get_price_provider,
)

router = APIRouter(tags=["refresh"])


@router.post("/refresh", response_model=RefreshResult)
def refresh_watchlist(
    db: Session = Depends(get_db),
    price_provider: StooqPriceProvider = Depends(get_price_provider),
):
    watchlist_items = db.query(Watchlist).order_by(Watchlist.symbol.asc()).all()

    alerts_created = 0
    for item in watchlist_items:
        try:
            quote = price_provider.get_quote(item.symbol)
        except PriceProviderError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        _, alert = apply_quote_to_watchlist(item, quote)
        if alert is not None:
            db.add(alert)
            alerts_created += 1

    db.commit()

    refreshed_items = db.query(Watchlist).order_by(Watchlist.symbol.asc()).all()
    return RefreshResult(
        refreshed=len(refreshed_items),
        alerts_created=alerts_created,
        watchlist=[build_watchlist_response(item) for item in refreshed_items],
    )
