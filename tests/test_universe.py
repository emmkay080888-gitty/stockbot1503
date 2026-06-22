"""Tests for the stock universe module."""

import sys
sys.path.insert(0, "stockbot")

import pytest
from data.universe import get_universe, SP500_TICKERS, NASDAQ100_TICKERS, DEFAULT_WATCHLIST


class TestGetUniverse:
    def test_sp500_returns_large_list(self):
        tickers = get_universe("sp500")
        assert len(tickers) > 200
        assert "AAPL" in tickers
        assert "MSFT" in tickers

    def test_nasdaq100_returns_about_100(self):
        tickers = get_universe("nasdaq100")
        assert len(tickers) >= 80
        assert "NVDA" in tickers

    def test_watchlist_returns_list(self):
        tickers = get_universe("watchlist")
        assert len(tickers) > 0
        assert "AAPL" in tickers

    def test_default_is_sp500(self):
        tickers = get_universe()
        assert len(tickers) > 200

    def test_case_insensitive(self):
        tickers = get_universe("SP500")
        assert len(tickers) > 200

    def test_invalid_name_returns_sp500(self):
        tickers = get_universe("invalid_name")
        assert len(tickers) > 200


class TestUniverseConstants:
    def test_sp500_tickers_unique(self):
        assert len(SP500_TICKERS) == len(set(SP500_TICKERS))

    def test_nasdaq100_tickers_unique(self):
        assert len(NASDAQ100_TICKERS) == len(set(NASDAQ100_TICKERS))

    def test_watchlist_tickers_unique(self):
        assert len(DEFAULT_WATCHLIST) == len(set(DEFAULT_WATCHLIST))

    def test_major_tickers_in_sp500(self):
        majors = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META"]
        for m in majors:
            assert m in SP500_TICKERS, f"{m} missing from SP500"

    def test_core_tickers_in_watchlist(self):
        core = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA"]
        for c in core:
            assert c in DEFAULT_WATCHLIST, f"{c} missing from watchlist"
