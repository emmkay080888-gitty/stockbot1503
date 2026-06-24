"""Smart ticker search with autocomplete from multiple sources.

Features:
- Search by company name, ticker symbol, or short form
- Multiple data sources (NSE constituents, Yahoo Finance, Alpha Vantage)
- Cached results for fast autocomplete
- Indian stock market (.NS) and US stock support
"""

import logging
import time
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import json
import re

logger = logging.getLogger(__name__)

# Cache for search results
SEARCH_CACHE_FILE = Path(__file__).parent.parent / "data" / "cache" / "ticker_search_cache.json"
SEARCH_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

# Popular Indian stocks for quick suggestions
POPULAR_INDIAN_STOCKS = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries Ltd", "exchange": "NSE"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services Ltd", "exchange": "NSE"},
    {"symbol": "INFY.NS", "name": "Infosys Ltd", "exchange": "NSE"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank Ltd", "exchange": "NSE"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank Ltd", "exchange": "NSE"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever Ltd", "exchange": "NSE"},
    {"symbol": "SBIN.NS", "name": "State Bank of India", "exchange": "NSE"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel Ltd", "exchange": "NSE"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank Ltd", "exchange": "NSE"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance Ltd", "exchange": "NSE"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro Ltd", "exchange": "NSE"},
    {"symbol": "WIPRO.NS", "name": "Wipro Ltd", "exchange": "NSE"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank Ltd", "exchange": "NSE"},
    {"symbol": "TITAN.NS", "name": "Titan Company Ltd", "exchange": "NSE"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki India Ltd", "exchange": "NSE"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharmaceutical Industries Ltd", "exchange": "NSE"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement Ltd", "exchange": "NSE"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies Ltd", "exchange": "NSE"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints Ltd", "exchange": "NSE"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra Ltd", "exchange": "NSE"},
    {"symbol": "NTPC.NS", "name": "NTPC Ltd", "exchange": "NSE"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation of India Ltd", "exchange": "NSE"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv Ltd", "exchange": "NSE"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors Ltd", "exchange": "NSE"},
    {"symbol": "ONGC.NS", "name": "Oil and Natural Gas Corporation Ltd", "exchange": "NSE"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports and Special Economic Zone Ltd", "exchange": "NSE"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel Ltd", "exchange": "NSE"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel Ltd", "exchange": "NSE"},
    {"symbol": "COALINDIA.NS", "name": "Coal India Ltd", "exchange": "NSE"},
    {"symbol": "GRASIM.NS", "name": "Grasim Industries Ltd", "exchange": "NSE"},
]

# Popular US stocks
POPULAR_US_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
    {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
    {"symbol": "AMZN", "name": "Amazon.com Inc.", "exchange": "NASDAQ"},
    {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
    {"symbol": "META", "name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "exchange": "NASDAQ"},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
    {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE"},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE"},
]


class TickerSearchEngine:
    """Smart ticker search with multiple data sources."""
    
    def __init__(self):
        self._cache = self._load_cache()
        self._nse_universe = None
        self._last_nse_refresh = 0
    
    def _load_cache(self) -> dict:
        """Load search cache from file."""
        try:
            if SEARCH_CACHE_FILE.exists():
                with open(SEARCH_CACHE_FILE) as f:
                    return json.load(f)
        except Exception as e:
            logger.debug(f"Failed to load search cache: {e}")
        return {}
    
    def _save_cache(self):
        """Save search cache to file."""
        try:
            with open(SEARCH_CACHE_FILE, "w") as f:
                json.dump(self._cache, f, indent=2)
        except Exception as e:
            logger.debug(f"Failed to save search cache: {e}")
    
    def _get_nse_universe(self) -> List[dict]:
        """Get NSE stock universe with caching."""
        current_time = time.time()
        
        # Refresh NSE universe every 24 hours
        if self._nse_universe and (current_time - self._last_nse_refresh) < 86400:
            return self._nse_universe
        
        try:
            from data.nse_sources import get_nse_constituents
            constituents = get_nse_constituents()
            
            # Convert to searchable format
            universe = []
            for index_name, tickers in constituents.items():
                for ticker in tickers:
                    # Extract company name from ticker (remove .NS)
                    symbol = ticker.replace(".NS", "")
                    universe.append({
                        "symbol": ticker,
                        "name": self._ticker_to_name(symbol),
                        "exchange": "NSE",
                        "index": index_name,
                    })
            
            self._nse_universe = universe
            self._last_nse_refresh = current_time
            return universe
            
        except Exception as e:
            logger.debug(f"Failed to load NSE universe: {e}")
            return []
    
    def _ticker_to_name(self, ticker: str) -> str:
        """Convert ticker symbol to readable company name."""
        # Simple mapping for common tickers
        name_map = {
            "RELIANCE": "Reliance Industries Ltd",
            "TCS": "Tata Consultancy Services Ltd",
            "INFY": "Infosys Ltd",
            "HDFCBANK": "HDFC Bank Ltd",
            "ICICIBANK": "ICICI Bank Ltd",
            "HINDUNILVR": "Hindustan Unilever Ltd",
            "SBIN": "State Bank of India",
            "BHARTIARTL": "Bharti Airtel Ltd",
            "KOTAKBANK": "Kotak Mahindra Bank Ltd",
            "BAJFINANCE": "Bajaj Finance Ltd",
            "LT": "Larsen & Toubro Ltd",
            "WIPRO": "Wipro Ltd",
            "AXISBANK": "Axis Bank Ltd",
            "TITAN": "Titan Company Ltd",
            "MARUTI": "Maruti Suzuki India Ltd",
        }
        return name_map.get(ticker, f"{ticker} Ltd")
    
    def search_yahoo_finance(self, query: str, limit: int = 10) -> List[dict]:
        """Search using Yahoo Finance."""
        try:
            import yfinance as yf
            results = []
            
            # Try direct ticker lookup first
            ticker = yf.Ticker(query.upper())
            try:
                info = ticker.info
                if info and "shortName" in info:
                    results.append({
                        "symbol": query.upper(),
                        "name": info.get("shortName", info.get("longName", query)),
                        "exchange": info.get("exchange", "Unknown"),
                        "source": "yahoo",
                    })
            except:
                pass
            
            # If query is short, try searching
            if len(query) >= 2:
                try:
                    # Use yfinance search (if available)
                    search_results = yf.search(query, max_results=limit)
                    if search_results and "quotes" in search_results:
                        for quote in search_results["quotes"][:limit]:
                            symbol = quote.get("symbol", "")
                            name = quote.get("shortname", quote.get("longname", ""))
                            exchange = quote.get("exchange", "")
                            
                            if symbol and name:
                                # Add .NS suffix for Indian stocks
                                if exchange in ["NSE", "NSI"]:
                                    symbol = f"{symbol}.NS"
                                results.append({
                                    "symbol": symbol,
                                    "name": name,
                                    "exchange": exchange,
                                    "source": "yahoo",
                                })
                except:
                    pass
            
            return results[:limit]
            
        except Exception as e:
            logger.debug(f"Yahoo Finance search failed: {e}")
            return []
    
    def search_alpha_vantage(self, query: str, limit: int = 10) -> List[dict]:
        """Search using Alpha Vantage API."""
        try:
            from config import ALPHAVANTAGE_API_KEY
            if not ALPHAVANTAGE_API_KEY:
                return []
            
            import requests
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": query,
                "apikey": ALPHAVANTAGE_API_KEY,
            }
            
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            
            if "bestMatches" not in data:
                return []
            
            results = []
            for match in data["bestMatches"][:limit]:
                symbol = match.get("1. symbol", "")
                name = match.get("2. name", "")
                exchange = match.get("4. region", "")
                
                if symbol and name:
                    # Add .NS suffix for Indian stocks
                    if "India" in match.get("8. currency", "") or "NSE" in exchange:
                        symbol = f"{symbol}.NS"
                    results.append({
                        "symbol": symbol,
                        "name": name,
                        "exchange": exchange,
                        "source": "alphavantage",
                    })
            
            return results
            
        except Exception as e:
            logger.debug(f"Alpha Vantage search failed: {e}")
            return []
    
    def search_local(self, query: str, limit: int = 20) -> List[dict]:
        """Search in local NSE universe."""
        query_lower = query.lower()
        results = []
        
        # Search in popular stocks first
        for stock in POPULAR_INDIAN_STOCKS + POPULAR_US_STOCKS:
            if (query_lower in stock["symbol"].lower() or 
                query_lower in stock["name"].lower()):
                results.append({**stock, "source": "local"})
        
        # Search in NSE universe
        nse_universe = self._get_nse_universe()
        for stock in nse_universe:
            if (query_lower in stock["symbol"].lower() or 
                query_lower in stock["name"].lower()):
                # Avoid duplicates
                if not any(r["symbol"] == stock["symbol"] for r in results):
                    results.append({**stock, "source": "nse"})
        
        return results[:limit]
    
    def search(self, query: str, limit: int = 10) -> List[dict]:
        """Search for tickers across all sources.
        
        Args:
            query: Search query (company name, ticker, or partial match)
            limit: Maximum number of results
        
        Returns:
            List of dicts with keys: symbol, name, exchange, source
        """
        if not query or len(query.strip()) < 1:
            return []
        
        query = query.strip()
        results = []
        
        # Check cache first
        cache_key = query.lower()
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            # Cache expires after 1 hour
            if time.time() - cached.get("timestamp", 0) < 3600:
                return cached.get("results", [])[:limit]
        
        # Search local database first (fastest)
        local_results = self.search_local(query, limit)
        results.extend(local_results)
        
        # If query looks like a ticker symbol (short, uppercase), try direct lookup
        if len(query) <= 5 and query.isupper():
            # Try with .NS suffix for Indian stocks
            if not query.endswith(".NS") and not query.endswith(".BO"):
                nse_ticker = f"{query}.NS"
                if not any(r["symbol"] == nse_ticker for r in results):
                    results.insert(0, {
                        "symbol": nse_ticker,
                        "name": self._ticker_to_name(query),
                        "exchange": "NSE",
                        "source": "guess",
                    })
        
        # Search Yahoo Finance (if we don't have enough results)
        if len(results) < limit:
            yahoo_results = self.search_yahoo_finance(query, limit - len(results))
            for r in yahoo_results:
                if not any(existing["symbol"] == r["symbol"] for existing in results):
                    results.append(r)
        
        # Search Alpha Vantage (if available and needed)
        if len(results) < limit:
            av_results = self.search_alpha_vantage(query, limit - len(results))
            for r in av_results:
                if not any(existing["symbol"] == r["symbol"] for existing in results):
                    results.append(r)
        
        # Deduplicate and limit
        seen = set()
        unique_results = []
        for r in results:
            if r["symbol"] not in seen:
                seen.add(r["symbol"])
                unique_results.append(r)
        
        # Save to cache
        self._cache[cache_key] = {
            "timestamp": time.time(),
            "results": unique_results[:limit],
        }
        self._save_cache()
        
        return unique_results[:limit]
    
    def get_popular_tickers(self, market: str = "NSE", limit: int = 20) -> List[dict]:
        """Get popular tickers for a market."""
        if market == "NSE":
            return POPULAR_INDIAN_STOCKS[:limit]
        elif market == "US":
            return POPULAR_US_STOCKS[:limit]
        else:
            return (POPULAR_INDIAN_STOCKS + POPULAR_US_STOCKS)[:limit]
    
    def clear_cache(self):
        """Clear search cache."""
        self._cache = {}
        try:
            if SEARCH_CACHE_FILE.exists():
                SEARCH_CACHE_FILE.unlink()
        except Exception as e:
            logger.debug(f"Failed to clear search cache: {e}")


# Global instance
_search_engine = None

def get_search_engine() -> TickerSearchEngine:
    """Get singleton search engine instance."""
    global _search_engine
    if _search_engine is None:
        _search_engine = TickerSearchEngine()
    return _search_engine


def search_tickers(query: str, limit: int = 10) -> List[dict]:
    """Convenience function to search for tickers."""
    return get_search_engine().search(query, limit)


def get_popular_tickers(market: str = "NSE", limit: int = 20) -> List[dict]:
    """Convenience function to get popular tickers."""
    return get_search_engine().get_popular_tickers(market, limit)