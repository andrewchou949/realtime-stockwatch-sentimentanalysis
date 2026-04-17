from __future__ import annotations

from datetime import datetime, UTC

from app.models import Alert, Watchlist
from app.services.price_provider import PriceQuote


def pct_change_from_baseline(baseline_price: float, current_price: float) -> float:
    return round(((current_price - baseline_price) / baseline_price) * 100, 4)


def build_watchlist_response(item: Watchlist) -> dict:
    pct_change = None
    if item.last_price is not None:
        pct_change = pct_change_from_baseline(item.baseline_price, item.last_price)

    return {
        "symbol": item.symbol,
        "threshold_pct": item.threshold_pct,
        "baseline_price": item.baseline_price,
        "baseline_at": item.baseline_at,
        "last_price": item.last_price,
        "last_updated_at": item.last_updated_at,
        "pct_change_from_baseline": pct_change,
    }


def apply_quote_to_watchlist(item: Watchlist, quote: PriceQuote) -> tuple[Watchlist, Alert | None]:
    previous_price = item.last_price if item.last_price is not None else item.baseline_price
    previous_pct = pct_change_from_baseline(item.baseline_price, previous_price)
    current_pct = pct_change_from_baseline(item.baseline_price, quote.price)

    item.last_price = quote.price
    item.last_updated_at = quote.timestamp

    crossed_threshold = abs(previous_pct) < item.threshold_pct <= abs(current_pct)
    if not crossed_threshold:
        return item, None

    direction = "UP" if current_pct >= 0 else "DOWN"
    alert = Alert(
        symbol=item.symbol,
        direction=direction,
        pct_change=current_pct,
        current_price=quote.price,
        baseline_price=item.baseline_price,
        triggered_at=quote.timestamp if quote.timestamp.tzinfo else datetime.now(UTC),
    )
    return item, alert
