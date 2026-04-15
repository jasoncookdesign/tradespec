import httpx
import pytest

from app.domain.market_data.errors import InvalidTickerError, ProviderUnavailableError
from app.domain.market_data.yahoo_adapter import YahooFinanceMarketDataProvider


def test_yahoo_adapter_parses_raw_provider_response() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "chart": {
                    "result": [
                        {
                            "meta": {
                                "currency": "USD",
                                "exchangeName": "NASDAQ",
                                "instrumentType": "EQUITY",
                                "regularMarketPrice": 123.45,
                                "previousClose": 122.0,
                            },
                            "timestamp": [1704067200, 1704153600],
                            "indicators": {
                                "quote": [
                                    {
                                        "open": [121.0, 122.0],
                                        "high": [124.0, 125.0],
                                        "low": [120.0, 121.0],
                                        "close": [122.5, 123.45],
                                        "volume": [1000000, 1200000],
                                    }
                                ]
                            },
                        }
                    ],
                    "error": None,
                }
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = YahooFinanceMarketDataProvider(client=client)

    data = provider.fetch_security_data("MSFT")

    assert data.symbol == "MSFT"
    assert data.latest_price == 123.45
    assert len(data.history) == 2


def test_yahoo_adapter_maps_invalid_ticker_errors() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "chart": {
                    "result": None,
                    "error": {"description": "No data found, symbol may be delisted"},
                }
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = YahooFinanceMarketDataProvider(client=client)

    with pytest.raises(InvalidTickerError):
        provider.fetch_security_data("BAD")


def test_yahoo_adapter_maps_network_failures() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("network down", request=request)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = YahooFinanceMarketDataProvider(client=client)

    with pytest.raises(ProviderUnavailableError):
        provider.fetch_security_data("MSFT")
