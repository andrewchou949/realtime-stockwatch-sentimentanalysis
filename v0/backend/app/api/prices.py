from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import PriceSnapshot
from app.services.price_provider import (
    PriceProviderError,
    StooqPriceProvider,
    get_price_provider,
)

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{symbol}", response_model=PriceSnapshot)
def get_price_snapshot(
    symbol: str,
    price_provider: StooqPriceProvider = Depends(get_price_provider),
):
    try:
        quote = price_provider.get_quote(symbol)
    except PriceProviderError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return PriceSnapshot(symbol=quote.symbol, price=quote.price, timestamp=quote.timestamp)
