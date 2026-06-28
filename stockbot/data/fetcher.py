"""Data fetching module - Multi-source with automatic failover.

This module now uses the MultiSourceFetcher which provides:
- Automatic failover between multiple data providers
- Smart caching to reduce API calls
- Data validation and cleaning
- Support for Alpha Vantage, NSE, Twelve Data, and Yahoo Finance

For direct access to the fetcher, use:
    from data.multi_source_fetcher import get_fetcher
    fetcher = get_fetcher()
    df = fetcher.fetch_historical(ticker)
"""

import logging
from typing import Optional, Dict
import pandas as pd

from data.multi_source_fetcher import get_fetcher

logger = logging.getLogger(__name__)


def fetch_historical(
    ticker: str,
    period: str = "6mo",
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    """Fetch historical price data with automatic failover.

    This is a compatibility wrapper that uses the new MultiSourceFetcher.
    
    Args:
        ticker: Stock ticker symbol.
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max).
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 1d, 5d, 1wk, 1mo).

    Returns:
        DataFrame with OHLCV data, or None if fetch fails.
    """
    return get_fetcher().fetch_historical(ticker, period=period, interval=interval)


def fetch_fundamentals(ticker: str) -> Optional[dict]:
    """Fetch fundamental data for a ticker.

    Returns:
        Dict with market_cap, pe_ratio, etc., or None.
    """
    return get_fetcher().fetch_fundamentals(ticker)


def fetch_multiple_timeframes(
    ticker: str,
) -> Dict[str, Optional[pd.DataFrame]]:
    """Fetch data across multiple timeframes for analysis.

    Returns:
        Dict with keys 'daily', 'weekly', '4h' mapped to DataFrames.
    """
    return get_fetcher().fetch_multiple_timeframes(ticker) if hasattr(get_fetcher(), 'fetch_multiple_timeframes') else {
        "daily": fetch_historical(ticker, period="1y", interval="1d"),
        "weekly": fetch_historical(ticker, period="2y", interval="1wk"),
        "4h": fetch_historical(ticker, period="3mo", interval="60m"),
    }


# Note: Options chain functionality removed in multi-source version
# The new fetcher focuses on reliable historical data from multiple sources

def fetch_options_chain(ticker: str, days_ahead: int = 30):
    """Fetch options chain - not implemented in multi-source fetcher.
    
    This functionality can be added back if needed using a dedicated options provider.
    """
    logger.warning("Options chain fetching not available in multi-source fetcher")
    return None


def twelvedata_fallback(ticker: str):
    """Legacy fallback - now handled automatically by MultiSourceFetcher."""
    logger.debug("twelvedata_fallback is deprecated, use fetch_historical instead")
    return None


def fetch_with_fallback(ticker: str, **kwargs):
    """Legacy function - now handled automatically by MultiSourceFetcher."""
    logger.debug("fetch_with_fallback is deprecated, use fetch_historical instead")
    return fetch_historical(ticker, **kwargs)
