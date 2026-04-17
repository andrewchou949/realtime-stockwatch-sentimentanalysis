from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Alert, Watchlist
from app.schemas import DevActionResult, DevForceBreachRequest, DevResetRequest
from app.services.alerts import pct_change_from_baseline

router = APIRouter(prefix="/dev", tags=["dev"])


def ensure_dev_tools_enabled() -> None:
    from os import getenv

    enabled = getenv("STOCK_WATCH_ENABLE_DEV_TOOLS", "true").strip().lower()
    if enabled not in {"1", "true", "yes", "on"}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dev tools are disabled for this environment.",
        )


def build_dev_action_result(message: str, db: Session) -> DevActionResult:
    return DevActionResult(
        message=message,
        watchlist_count=db.query(Watchlist).count(),
        alert_count=db.query(Alert).count(),
    )


@router.post("/force-breach", response_model=DevActionResult)
def force_breach(
    payload: DevForceBreachRequest,
    db: Session = Depends(get_db),
):
    ensure_dev_tools_enabled()

    item = db.get(Watchlist, payload.symbol)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{payload.symbol} is not in the watchlist.",
        )

    sign = 1 if payload.direction == "UP" else -1
    simulated_price = round(item.baseline_price * (1 + (sign * payload.pct_change / 100)), 4)
    simulated_timestamp = datetime.now(UTC)

    item.last_price = simulated_price
    item.last_updated_at = simulated_timestamp

    db.add(
        Alert(
            symbol=item.symbol,
            direction=payload.direction,
            pct_change=pct_change_from_baseline(item.baseline_price, simulated_price),
            current_price=simulated_price,
            baseline_price=item.baseline_price,
            triggered_at=simulated_timestamp,
        )
    )
    db.commit()

    return build_dev_action_result(
        f"Forced a {payload.direction} breach for {item.symbol} at {payload.pct_change:.2f}%.",
        db,
    )


@router.post("/reset", response_model=DevActionResult)
def reset_demo_state(
    payload: DevResetRequest,
    db: Session = Depends(get_db),
):
    ensure_dev_tools_enabled()

    if payload.scope == "alerts":
        db.execute(delete(Alert))
        db.commit()
        return build_dev_action_result("Cleared all alerts.", db)

    if payload.scope == "symbol":
        if not payload.symbol:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="symbol is required when scope is set to symbol.",
            )
        db.execute(delete(Alert).where(Alert.symbol == payload.symbol))
        deleted = db.get(Watchlist, payload.symbol)
        if deleted is not None:
            db.delete(deleted)
        db.commit()
        return build_dev_action_result(f"Removed demo state for {payload.symbol}.", db)

    db.execute(delete(Alert))
    db.execute(delete(Watchlist))
    db.commit()
    return build_dev_action_result("Cleared watchlist and alerts.", db)
