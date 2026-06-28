"""Data fetching module - yfinance primary, Twelve Data fallback."""

import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf
import requests

from config import TWELVEDATA_API_KEY

logger = logging.getLogger(__name__)

# Thread-safe rate limiting
_YF_LOCK = threading.Lock()
_YF_LAST_CALL = 0.0
_YF_MIN_INTERVAL = 0.5  # seconds between Yahoo Finance calls


def _rate_limit():
    """Ensure we don't exceed rate limits. Thread-safe."""
    global _YF_LAST_CALL
    with _YF_LOCK:
        elapsed = time.time() - _YF_LAST_CALL
        if elapsed < _YF_MIN_INTERVAL:
            time.sleep(_YF_MIN_INTERVAL - elapsed)
        _YF_LAST_CALL = time.time()


def fetch_historical(
    ticker: str,
    period: str = "6mo",
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    """Fetch historical price data for a ticker using yfinance.

    Args:
        ticker: Stock ticker symbol.
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max).
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 1d, 5d, 1wk, 1mo).

    Returns:
        DataFrame with OHLCV data, or None if fetch fails.
    """
    _rate_limit()
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, interval=interval)

        if df.empty:
            logger.warning(f"No data returned for {ticker}")
            return None

        # Clean column names (yfinance returns capitalized names)
        df.columns = [c.lower() for c in df.columns]
        df.index.name = "date"

        # Ensure we have all required columns
        required = ["open", "high", "low", "close", "volume"]
        if not all(c in df.columns for c in required):
            logger.warning(f"{ticker} missing required columns")
            return None

        return df

    except Exception as e:
        logger.error(f"Error fetching {ticker}: {e}")
        return None


def fetch_fundamentals(ticker: str) -> Optional[dict]:
    """Fetch fundamental data for a ticker.

    Returns:
        Dict with market_cap, pe_ratio, etc., or None.
    """
    _rate_limit()
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "eps": info.get("trailingEps"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "short_ratio": info.get("shortRatio"),
            "avg_volume": info.get("averageVolume"),
        }
    except Exception as e:
        logger.debug(f"Error fetching fundamentals for {ticker}: {e}")
        return None


def fetch_multiple_timeframes(
    ticker: str,
) -> dict[str, Optional[pd.DataFrame]]:
    """Fetch data across multiple timeframes for analysis.

    Returns:
        Dict with keys 'daily', 'weekly', '4h' mapped to DataFrames.
    """
    result = {}

    # Daily data (longer period for trend analysis)
    result["daily"] = fetch_historical(ticker, period="1y", interval="1d")

    # Weekly data
    result["weekly"] = fetch_historical(ticker, period="2y", interval="1wk")

    # 4-hour data (for entry timing) - need last 3 months
    result["4h"] = fetch_historical(ticker, period="3mo", interval="60m")

    # Extra spacing between multi-TF calls (rate limiter handles 0.5s, add a bit more)
    time.sleep(0.3)

    return result


def fetch_options_chain(ticker: str, days_ahead: int = 30) -> Optional[pd.DataFrame]:
    """Fetch options chain to calculate expected move.

    Args:
        ticker: Stock ticker symbol.
        days_ahead: Look for expiration approximately this many days out.

    Returns:
        DataFrame with options data, or None.
    """
    _rate_limit()
    try:
        stock = yf.Ticker(ticker)
        expirations = stock.options

        if not expirations:
            return None

        # Find closest expiration to target
        target_date = datetime.now().date() + timedelta(days=days_ahead)
        best_exp = min(
            expirations,
            key=lambda d: abs(
                datetime.strptime(d, "%Y-%m-%d").date() - target_date
            ),
        )

        opt = stock.option_chain(best_exp)
        calls = opt.calls
        puts = opt.puts

        # Find ATM strike - fetch current price safely
        hist = stock.history(period="1d")
        if hist.empty:
            logger.debug(f"No price data for options chain on {ticker}")
            return None
        current_price = hist["Close"].iloc[-1]

        calls["type"] = "call"
        puts["type"] = "put"
        chain = pd.concat([calls, puts])
        chain["strike_diff"] = abs(chain["strike"] - current_price)
        atm_options = chain.nsmallest(2, "strike_diff")

        return atm_options

    except Exception as e:
        logger.debug(f"Error fetching options for {ticker}: {e}")
        return None


def twelvedata_fallback(ticker: str) -> Optional[pd.DataFrame]:
    """Fallback data source using Twelve Data API."""
    if not TWELVEDATA_API_KEY:
        return None

    try:
        url = (
            f"https://api.twelvedata.com/time_series"
            f"?symbol={ticker}"
            f"&interval=1day"
            f"&outputsize=365"
            f"&apikey={TWELVEDATA_API_KEY}"
            f"&format=JSON"
        )
        resp = requests.get(url, timeout=10)
        data = resp.json()

        if "values" not in data:
            return None

        values = data["values"]
        records = []
        for v in values:
            records.append(
                {
                    "date": v["datetime"],
                    "open": float(v["open"]),
                    "high": float(v["high"]),
                    "low": float(v["low"]),
                    "close": float(v["close"]),
                    "volume": int(v["volume"]),
                }
            )

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)
        df.sort_index(inplace=True)
        return df

    except Exception as e:
        logger.debug(f"Twelve Data fallback failed for {ticker}: {e}")
        return None


def fetch_with_fallback(ticker: str, **kwargs) -> Optional[pd.DataFrame]:
    """Fetch data with automatic fallback."""
    df = fetch_historical(ticker, **kwargs)
    if df is None or len(df) < 20:
        logger.info(f"yfinance failed for {ticker}, trying Twelve Data fallback...")
        df = twelvedata_fallback(ticker)
    return df
