from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Watchlist
from app.schemas import WatchlistCreate, WatchlistItem
from app.services.alerts import build_watchlist_response
from app.services.price_provider import (
    PriceProviderError,
    StooqPriceProvider,
    get_price_provider,
)

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.post("", response_model=WatchlistItem, status_code=status.HTTP_201_CREATED)
def create_watchlist_item(
    payload: WatchlistCreate,
    db: Session = Depends(get_db),
    price_provider: StooqPriceProvider = Depends(get_price_provider),
):
    existing = db.get(Watchlist, payload.symbol)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{payload.symbol} is already in the watchlist.",
        )

    try:
        quote = price_provider.get_quote(payload.symbol)
    except PriceProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    item = Watchlist(
        symbol=quote.symbol,
        threshold_pct=payload.threshold_pct,
        baseline_price=quote.price,
        baseline_at=quote.timestamp,
        last_price=quote.price,
        last_updated_at=quote.timestamp,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return build_watchlist_response(item)


@router.get("", response_model=list[WatchlistItem])
def list_watchlist(db: Session = Depends(get_db)):
    items = db.query(Watchlist).order_by(Watchlist.symbol.asc()).all()
    return [build_watchlist_response(item) for item in items]


@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def delete_watchlist_item(symbol: str, db: Session = Depends(get_db)):
    normalized_symbol = symbol.strip().upper()
    item = db.get(Watchlist, normalized_symbol)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{normalized_symbol} is not in the watchlist.",
        )

    db.delete(item)
    db.commit()
