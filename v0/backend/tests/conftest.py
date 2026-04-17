from collections.abc import Generator
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base, get_db
from app.main import app
from app.services.price_provider import PriceProviderError, PriceQuote, get_price_provider


class StubPriceProvider:
    def __init__(self) -> None:
        self.quotes: dict[str, list[PriceQuote]] = {}
        self.fail_symbols: set[str] = set()

    def seed(self, symbol: str, *prices: float) -> None:
        normalized = symbol.upper()
        self.quotes[normalized] = [
            PriceQuote(
                symbol=normalized,
                price=price,
                timestamp=datetime(2026, 4, 17, 12, index, tzinfo=UTC),
            )
            for index, price in enumerate(prices, start=1)
        ]

    def get_quote(self, symbol: str) -> PriceQuote:
        normalized = symbol.upper()
        if normalized in self.fail_symbols:
            raise PriceProviderError(f"Unable to fetch price for {normalized}.")
        queue = self.quotes.get(normalized)
        if not queue:
            raise PriceProviderError(f"Unable to fetch price for {normalized}.")
        if len(queue) > 1:
            return queue.pop(0)
        return queue[0]


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test_stock_watch.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    provider = StubPriceProvider()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_price_provider() -> StubPriceProvider:
        return provider

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_price_provider] = override_get_price_provider

    with TestClient(app) as test_client:
        test_client.provider = provider
        yield test_client

    app.dependency_overrides.clear()
