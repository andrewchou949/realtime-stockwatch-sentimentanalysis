# for define the app project structure!
# sqlite doesn't know file structure

from sqlalchemy import String, Float, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column # for defining tables in python
from datetime import datetime
from app.db import Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    symbol: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    threshold_pct: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_price: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    last_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String, ForeignKey("watchlist.symbol"), nullable=False)

    direction: Mapped[str] = mapped_column(String, nullable=False)  # "UP" / "DOWN"
    pct_change: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[float] = mapped_column(Float, nullable=False)
    baseline_price: Mapped[float] = mapped_column(Float, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)