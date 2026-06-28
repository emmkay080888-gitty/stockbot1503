"""Multi-source data fetcher with automatic failover.

Supported providers:
1. Yahoo Finance (yfinance) - Current fallback, slow but free
2. Alpha Vantage - Free tier: 25 calls/day, 5 calls/min
3. NSE Official API - For Indian stocks, more reliable than scraping
4. Twelve Data - Fallback if configured

Features:
- Automatic failover between providers
- Smart caching to reduce API calls
- Rate limiting per provider
- Data validation and cleaning
"""

import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path
import json

import pandas as pd
import requests

from config import TWELVEDATA_API_KEY

logger = logging.getLogger(__name__)

# Cache directory
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


class DataProvider:
    """Base class for data providers."""
    
    name: str = "base"
    priority: int = 0  # Lower number = higher priority
    rate_limit_delay: float = 1.0  # Seconds between calls
    
    def __init__(self):
        self._last_call = 0.0
        self._call_count = 0
        self._call_reset_time = time.time()
    
    def _rate_limit(self):
        """Enforce rate limiting."""
        now = time.time()
        # Reset counter every minute
        if now - self._call_reset_time > 60:
            self._call_count = 0
            self._call_reset_time = now
        
        elapsed = now - self._last_call
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        
        self._last_call = time.time()
        self._call_count += 1
    
    def fetch_historical(self, ticker: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        """Fetch historical data. Override in subclass."""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        return True


class YahooFinanceProvider(DataProvider):
    """Yahoo Finance provider (current implementation)."""
    
    name = "yahoo"
    priority = 10  # Lowest priority - use as last resort
    rate_limit_delay = 0.5
    
    def fetch_historical(self, ticker: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        self._rate_limit()
        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                logger.warning(f"[Yahoo] No data for {ticker}")
                return None
            
            # Standardize column names
            df.columns = [c.lower() for c in df.columns]
            df.index.name = "date"
            
            required = ["open", "high", "low", "close", "volume"]
            if not all(c in df.columns for c in required):
                logger.warning(f"[Yahoo] {ticker} missing required columns")
                return None
            
            return df
            
        except Exception as e:
            logger.error(f"[Yahoo] Error fetching {ticker}: {e}")
            return None


class AlphaVantageProvider(DataProvider):
    """Alpha Vantage provider - free tier: 25 calls/day, 5 calls/min."""
    
    name = "alphavantage"
    priority = 1  # High priority - reliable and free
    rate_limit_delay = 12.0  # 5 calls per minute = 12s between calls
    
    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key or os.getenv("ALPHAVANTAGE_API_KEY", "")
        self.base_url = "https://www.alphavantage.co/query"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def fetch_historical(self, ticker: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        if not self.is_available():
            return None
        
        self._rate_limit()
        
        # Map period to Alpha Vantage parameters
        av_function = "TIME_SERIES_DAILY"
        av_interval = None
        outputsize = "full"
        
        if interval in ["1m", "5m", "15m", "30m", "60m"]:
            av_function = "TIME_SERIES_INTRADAY"
            av_interval = interval
            outputsize = "full"
        elif period in ["1mo", "3mo"]:
            outputsize = "compact"
        
        # Clean ticker for Alpha Vantage (remove .NS suffix for Indian stocks)
        av_ticker = ticker.replace(".NS", "")
        
        params = {
            "function": av_function,
            "symbol": av_ticker,
            "apikey": self.api_key,
            "outputsize": outputsize,
        }
        
        if av_interval:
            params["interval"] = av_interval
        
        try:
            resp = requests.get(self.base_url, params=params, timeout=15)
            data = resp.json()
            
            # Check for API errors
            if "Error Message" in data:
                logger.warning(f"[AlphaVantage] API error for {ticker}: {data['Error Message']}")
                return None
            
            if "Note" in data:
                logger.warning(f"[AlphaVantage] Rate limit hit: {data['Note']}")
                return None
            
            # Extract time series data
            time_series_key = None
            for key in data.keys():
                if "Time Series" in key:
                    time_series_key = key
                    break
            
            if not time_series_key:
                logger.warning(f"[AlphaVantage] No time series data for {ticker}")
                return None
            
            time_series = data[time_series_key]
            
            # Convert to DataFrame
            records = []
            for date_str, values in time_series.items():
                records.append({
                    "date": pd.to_datetime(date_str),
                    "open": float(values.get("1. open", 0)),
                    "high": float(values.get("2. high", 0)),
                    "low": float(values.get("3. low", 0)),
                    "close": float(values.get("4. close", 0)),
                    "volume": int(float(values.get("5. volume", 0))),
                })
            
            df = pd.DataFrame(records)
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)
            
            # Filter by period
            if period == "1mo":
                cutoff = datetime.now() - timedelta(days=30)
            elif period == "3mo":
                cutoff = datetime.now() - timedelta(days=90)
            elif period == "6mo":
                cutoff = datetime.now() - timedelta(days=180)
            elif period == "1y":
                cutoff = datetime.now() - timedelta(days=365)
            else:
                cutoff = datetime.now() - timedelta(days=180)
            
            df = df[df.index >= cutoff]
            
            if df.empty:
                return None
            
            logger.info(f"[AlphaVantage] Fetched {len(df)} rows for {ticker}")
            return df
            
        except Exception as e:
            logger.error(f"[AlphaVantage] Error fetching {ticker}: {e}")
            return None


class NSEOfficialProvider(DataProvider):
    """NSE Official API provider for Indian stocks."""
    
    name = "nse"
    priority = 2  # High priority for Indian stocks
    rate_limit_delay = 2.0  # Be respectful to NSE servers
    
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/",
        })
        self._session_established = False
    
    def _establish_session(self):
        """Establish NSE session with cookies."""
        if self._session_established:
            return
        
        try:
            resp = self.session.get("https://www.nseindia.com/", timeout=15)
            if resp.status_code == 200:
                time.sleep(1)
                self._session_established = True
                logger.info("[NSE] Session established")
        except Exception as e:
            logger.debug(f"[NSE] Session establishment failed: {e}")
    
    def is_available(self) -> bool:
        return True  # Always try for Indian stocks
    
    def _is_indian_stock(self, ticker: str) -> bool:
        """Check if ticker is an Indian stock."""
        return ticker.endswith(".NS") or ticker.endswith(".BO")
    
    def fetch_historical(self, ticker: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        if not self._is_indian_stock(ticker):
            return None
        
        self._establish_session()
        self._rate_limit()
        
        # NSE API for historical data
        symbol = ticker.replace(".NS", "")
        
        # Map period to NSE parameters
        period_map = {
            "1mo": "1M",
            "3mo": "3M",
            "6mo": "6M",
            "1y": "1Y",
        }
        
        nse_period = period_map.get(period, "6M")
        
        url = f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}&series=[%22EQ%22]&from={datetime.now() - timedelta(days=180)}&to={datetime.now()}"
        
        try:
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code != 200:
                logger.debug(f"[NSE] HTTP {resp.status_code} for {ticker}")
                return None
            
            data = resp.json()
            
            if "data" not in data or not data["data"]:
                logger.debug(f"[NSE] No data for {ticker}")
                return None
            
            # Parse NSE data format
            records = []
            for item in data["data"]:
                records.append({
                    "date": pd.to_datetime(item.get("date", "")),
                    "open": float(item.get("open", 0)),
                    "high": float(item.get("high", 0)),
                    "low": float(item.get("low", 0)),
                    "close": float(item.get("close", 0)),
                    "volume": int(item.get("totalTradedVolume", 0)),
                })
            
            df = pd.DataFrame(records)
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)
            
            if df.empty:
                return None
            
            logger.info(f"[NSE] Fetched {len(df)} rows for {ticker}")
            return df
            
        except Exception as e:
            logger.debug(f"[NSE] Error fetching {ticker}: {e}")
            return None


class TwelveDataProvider(DataProvider):
    """Twelve Data provider - fallback if API key is configured."""
    
    name = "twelvedata"
    priority = 5
    rate_limit_delay = 0.5
    
    def __init__(self, api_key: str = ""):
        super().__init__()
        self.api_key = api_key or TWELVEDATA_API_KEY
        self.base_url = "https://api.twelvedata.com"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def fetch_historical(self, ticker: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
        if not self.is_available():
            return None
        
        self._rate_limit()
        
        # Map interval to Twelve Data format
        interval_map = {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "30m": "30min",
            "60m": "1h",
            "1d": "1day",
            "1wk": "1week",
            "1mo": "1month",
        }
        
        td_interval = interval_map.get(interval, "1day")
        
        # Map period to outputsize
        outputsize_map = {
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365,
        }
        
        outputsize = outputsize_map.get(period, 180)
        
        params = {
            "symbol": ticker,
            "interval": td_interval,
            "outputsize": outputsize,
            "apikey": self.api_key,
            "format": "JSON",
        }
        
        try:
            resp = requests.get(f"{self.base_url}/time_series", params=params, timeout=15)
            data = resp.json()
            
            if "values" not in data:
                logger.debug(f"[TwelveData] No data for {ticker}")
                return None
            
            records = []
            for v in data["values"]:
                records.append({
                    "date": pd.to_datetime(v["datetime"]),
                    "open": float(v["open"]),
                    "high": float(v["high"]),
                    "low": float(v["low"]),
                    "close": float(v["close"]),
                    "volume": int(v["volume"]),
                })
            
            df = pd.DataFrame(records)
            df.set_index("date", inplace=True)
            df.sort_index(inplace=True)
            
            if df.empty:
                return None
            
            logger.info(f"[TwelveData] Fetched {len(df)} rows for {ticker}")
            return df
            
        except Exception as e:
            logger.debug(f"[TwelveData] Error fetching {ticker}: {e}")
            return None


class MultiSourceFetcher:
    """Main fetcher that tries multiple providers in priority order."""
    
    def __init__(self):
        self.providers: List[DataProvider] = []
        self._setup_providers()
    
    def _setup_providers(self):
        """Initialize all available providers."""
        # Add providers in priority order
        self.providers.append(AlphaVantageProvider())
        self.providers.append(NSEOfficialProvider())
        self.providers.append(TwelveDataProvider())
        self.providers.append(YahooFinanceProvider())
        
        # Sort by priority
        self.providers.sort(key=lambda p: p.priority)
        
        available = [p.name for p in self.providers if p.is_available()]
        logger.info(f"Data providers initialized: {', '.join(available)}")
    
    def fetch_historical(self, ticker: str, period: str = "6mo", interval: str = "1d", use_cache: bool = True) -> Optional[pd.DataFrame]:
        """Fetch historical data with automatic failover.
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1mo, 3mo, 6mo, 1y, etc.)
            interval: Data interval (1d, 1h, etc.)
            use_cache: Whether to use cached data
        
        Returns:
            DataFrame with OHLCV data or None
        """
        # Check cache first
        if use_cache:
            cached = self._get_from_cache(ticker, period, interval)
            if cached is not None:
                logger.debug(f"[Cache] Using cached data for {ticker}")
                return cached
        
        # Try each provider in priority order
        errors = []
        for provider in self.providers:
            if not provider.is_available():
                continue
            
            try:
                logger.debug(f"[{provider.name.upper()}] Trying {ticker}")
                df = provider.fetch_historical(ticker, period, interval)
                
                if df is not None and not df.empty:
                    # Validate data quality
                    if self._validate_data(df, ticker):
                        # Cache successful fetch
                        if use_cache:
                            self._save_to_cache(ticker, period, interval, df)
                        logger.info(f"[{provider.name.upper()}] Successfully fetched {ticker}")
                        return df
                    else:
                        logger.warning(f"[{provider.name.upper()}] Invalid data for {ticker}")
                        errors.append(f"{provider.name}: invalid data")
                else:
                    errors.append(f"{provider.name}: no data")
                    
            except Exception as e:
                errors.append(f"{provider.name}: {str(e)}")
                logger.debug(f"[{provider.name.upper()}] Failed for {ticker}: {e}")
        
        logger.error(f"All providers failed for {ticker}: {'; '.join(errors)}")
        return None
    
    def _validate_data(self, df: pd.DataFrame, ticker: str) -> bool:
        """Validate data quality."""
        if df is None or df.empty:
            return False
        
        # Check required columns
        required = ["open", "high", "low", "close", "volume"]
        if not all(c in df.columns for c in required):
            return False
        
        # Check for reasonable values
        if len(df) < 5:
            return False
        
        # Check for null values
        if df[required].isnull().any().any():
            return False
        
        # Check for negative prices
        if (df[["open", "high", "low", "close"]] <= 0).any().any():
            return False
        
        # Check price consistency (high >= low, etc.)
        if not (df["high"] >= df["low"]).all():
            return False
        if not (df["high"] >= df["close"]).all():
            return False
        if not (df["high"] >= df["open"]).all():
            return False
        if not (df["low"] <= df["close"]).all():
            return False
        if not (df["low"] <= df["open"]).all():
            return False
        
        return True
    
    def _get_cache_path(self, ticker: str, period: str, interval: str) -> Path:
        """Get cache file path for a query."""
        safe_ticker = ticker.replace("/", "_").replace(":", "_")
        filename = f"{safe_ticker}_{period}_{interval}.parquet"
        return CACHE_DIR / filename
    
    def _get_from_cache(self, ticker: str, period: str, interval: str, max_age_hours: int = 1) -> Optional[pd.DataFrame]:
        """Get data from cache if not too old."""
        cache_path = self._get_cache_path(ticker, period, interval)
        
        if not cache_path.exists():
            return None
        
        # Check age
        age = time.time() - cache_path.stat().st_mtime
        if age > max_age_hours * 3600:
            return None
        
        try:
            df = pd.read_parquet(cache_path)
            return df if not df.empty else None
        except Exception:
            return None
    
    def _save_to_cache(self, ticker: str, period: str, interval: str, df: pd.DataFrame):
        """Save data to cache."""
        try:
            cache_path = self._get_cache_path(ticker, period, interval)
            df.to_parquet(cache_path)
        except Exception as e:
            logger.debug(f"Failed to cache data: {e}")
    
    def clear_cache(self, ticker: str = None):
        """Clear cache for specific ticker or all."""
        if ticker:
            # Clear specific ticker
            for f in CACHE_DIR.glob(f"{ticker.replace('/', '_').replace(':', '_')}_*"):
                f.unlink()
        else:
            # Clear all
            for f in CACHE_DIR.glob("*.parquet"):
                f.unlink()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [p.name for p in self.providers if p.is_available()]
    
    def fetch_multiple_timeframes(self, ticker: str) -> Dict[str, Optional[pd.DataFrame]]:
        """Fetch data across multiple timeframes for analysis.
        
        Returns:
            Dict with keys 'daily', 'weekly', '4h' mapped to DataFrames.
        """
        result = {}
        result["daily"] = self.fetch_historical(ticker, period="1y", interval="1d")
        result["weekly"] = self.fetch_historical(ticker, period="2y", interval="1wk")
        result["4h"] = self.fetch_historical(ticker, period="3mo", interval="60m")
        time.sleep(0.3)
        return result
    
    def fetch_fundamentals(self, ticker: str) -> Optional[dict]:
        """Fetch fundamental data for a ticker.
        
        Returns:
            Dict with market_cap, pe_ratio, etc., or None.
        """
        # TODO: Add more fundamental data providers
        try:
            import yfinance as yf
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


# Global instance
_fetcher = None

def get_fetcher() -> MultiSourceFetcher:
    """Get singleton fetcher instance."""
    global _fetcher
    if _fetcher is None:
        _fetcher = MultiSourceFetcher()
    return _fetcher


# Convenience functions (drop-in replacement for old API)
def fetch_historical(ticker: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
    """Fetch historical data with automatic failover."""
    return get_fetcher().fetch_historical(ticker, period, interval)


def fetch_multiple_timeframes(ticker: str) -> dict[str, Optional[pd.DataFrame]]:
    """Fetch data across multiple timeframes."""
    result = {}
    result["daily"] = fetch_historical(ticker, period="1y", interval="1d")
    result["weekly"] = fetch_historical(ticker, period="2y", interval="1wk")
    result["4h"] = fetch_historical(ticker, period="3mo", interval="60m")
    time.sleep(0.3)
    return result


def fetch_fundamentals(ticker: str) -> Optional[dict]:
    """Fetch fundamental data (currently uses Yahoo Finance)."""
    # TODO: Add more fundamental data providers
    try:
        import yfinance as yf
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


