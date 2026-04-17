from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WatchlistCreate(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    threshold_pct: float = Field(gt=0)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()


class WatchlistItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    symbol: str
    threshold_pct: float
    baseline_price: float
    baseline_at: datetime
    last_price: float | None = None
    last_updated_at: datetime | None = None
    pct_change_from_baseline: float | None = None


class PriceSnapshot(BaseModel):
    symbol: str
    price: float
    timestamp: datetime


class AlertItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    symbol: str
    direction: str
    pct_change: float
    current_price: float
    baseline_price: float
    triggered_at: datetime


class RefreshResult(BaseModel):
    refreshed: int
    alerts_created: int
    watchlist: list[WatchlistItem]


class DevForceBreachRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=10)
    direction: str = Field(default="UP")
    pct_change: float = Field(default=5.0, gt=0)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("direction")
    @classmethod
    def normalize_direction(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in {"UP", "DOWN"}:
            raise ValueError("direction must be UP or DOWN")
        return normalized


class DevResetRequest(BaseModel):
    scope: str = Field(default="all")
    symbol: str | None = Field(default=None, min_length=1, max_length=10)

    @field_validator("scope")
    @classmethod
    def normalize_scope(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"all", "alerts", "symbol"}:
            raise ValueError("scope must be all, alerts, or symbol")
        return normalized

    @field_validator("symbol")
    @classmethod
    def normalize_optional_symbol(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()


class DevActionResult(BaseModel):
    message: str
    watchlist_count: int
    alert_count: int
