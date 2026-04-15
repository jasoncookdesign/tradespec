from datetime import UTC, datetime

import httpx

from app.domain.market_data.config import DEFAULT_LOOKBACK_DAYS
from app.domain.market_data.errors import (
    InsufficientDataError,
    InvalidTickerError,
    ProviderUnavailableError,
)
from app.domain.market_data.models import ProviderSecurityData, RawPriceBar


class YahooFinanceMarketDataProvider:
    """Lightweight Yahoo Finance adapter using the chart endpoint."""

    base_url = "https://query1.finance.yahoo.com/v8/finance/chart"

    def __init__(self, client: httpx.Client | None = None):
        self._client = client or httpx.Client(
            timeout=10.0,
            headers={"User-Agent": "TradeSpec/0.1"},
        )

    def fetch_security_data(
        self,
        symbol: str,
        lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> ProviderSecurityData:
        cleaned = symbol.strip().upper()
        if not cleaned:
            raise InvalidTickerError("Ticker symbol cannot be empty.")

        range_param = "3mo" if lookback_days <= 90 else "6mo"

        try:
            response = self._client.get(
                f"{self.base_url}/{cleaned}",
                params={
                    "interval": "1d",
                    "range": range_param,
                    "includePrePost": "false",
                    "events": "div,splits",
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise InvalidTickerError(f"Ticker {cleaned} was not found.") from exc
            raise ProviderUnavailableError("Yahoo Finance returned an unexpected error.") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("Yahoo Finance request failed.") from exc

        payload = response.json().get("chart", {})
        error = payload.get("error")
        if error:
            description = error.get("description", "Ticker data is unavailable.")
            lowered = description.lower()
            if "not found" in lowered or "no data" in lowered or "symbol" in lowered:
                raise InvalidTickerError(description)
            raise ProviderUnavailableError(description)

        results = payload.get("result") or []
        if not results:
            raise InvalidTickerError(f"Ticker {cleaned} was not found.")

        result = results[0]
        meta = result.get("meta", {})
        quote = result.get("indicators", {}).get("quote", [{}])[0]
        timestamps = result.get("timestamp") or []

        bars: list[RawPriceBar] = []
        for ts, open_price, high, low, close, volume in zip(
            timestamps,
            quote.get("open", []),
            quote.get("high", []),
            quote.get("low", []),
            quote.get("close", []),
            quote.get("volume", []),
            strict=False,
        ):
            if None in (open_price, high, low, close, volume):
                continue
            bars.append(
                RawPriceBar(
                    timestamp=datetime.fromtimestamp(ts, tz=UTC),
                    open=float(open_price),
                    high=float(high),
                    low=float(low),
                    close=float(close),
                    volume=int(volume),
                )
            )

        if not bars:
            raise InsufficientDataError(
                f"Yahoo Finance returned no usable price history for {cleaned}."
            )

        instrument_type = str(meta.get("instrumentType", "")).upper()
        if "ETF" in instrument_type:
            asset_type = "etf"
        elif instrument_type:
            asset_type = "stock"
        else:
            asset_type = "unknown"

        latest_price = float(meta.get("regularMarketPrice") or bars[-1].close)
        previous_close = float(
            meta.get("previousClose") or (bars[-2].close if len(bars) > 1 else bars[-1].close)
        )

        return ProviderSecurityData(
            symbol=cleaned,
            asset_type=asset_type,
            currency=str(meta.get("currency", "USD")),
            exchange=str(meta.get("exchangeName", "UNKNOWN")),
            latest_price=latest_price,
            previous_close=previous_close,
            history=bars,
            source="yahoo-finance",
        )
