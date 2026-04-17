from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, UTC
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


class PriceProviderError(Exception):
    pass


@dataclass
class PriceQuote:
    symbol: str
    price: float
    timestamp: datetime


class StooqPriceProvider:
    def get_quote(self, symbol: str) -> PriceQuote:
        normalized_symbol = symbol.strip().upper()
        stooq_symbol = f"{normalized_symbol.lower()}.us"
        url = f"https://stooq.com/q/l/?s={stooq_symbol}&i=d"
        try:
            with urlopen(url, timeout=10) as response:
                payload = response.read().decode("utf-8").strip()
        except (HTTPError, URLError, TimeoutError) as exc:
            raise PriceProviderError(f"Unable to fetch price for {normalized_symbol}.") from exc

        try:
            fields = payload.split(",")
            if len(fields) < 8:
                raise ValueError("Incomplete quote data")
            symbol_value, trade_date, trade_time, _open, _high, _low, close, _volume = fields[:8]
            if symbol_value == "N/D" or close == "N/D":
                raise ValueError("No quote data available")
            price = float(close)
            timestamp = datetime.strptime(
                f"{trade_date}{trade_time}",
                "%Y%m%d%H%M%S",
            ).replace(tzinfo=UTC)
        except (TypeError, ValueError) as exc:
            raise PriceProviderError(f"Invalid price payload for {normalized_symbol}.") from exc

        return PriceQuote(symbol=normalized_symbol, price=price, timestamp=timestamp)


def get_price_provider() -> StooqPriceProvider:
    return StooqPriceProvider()
