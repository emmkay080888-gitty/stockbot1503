#!/usr/bin/env python3
"""Test script for the new multi-source data fetcher."""

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.multi_source_fetcher import get_fetcher
from config import ALPHAVANTAGE_API_KEY

def test_fetcher():
    """Test the multi-source fetcher with various tickers."""
    fetcher = get_fetcher()
    
    print("=" * 60)
    print("Testing Multi-Source Data Fetcher")
    print("=" * 60)
    
    # Show available providers
    providers = fetcher.get_available_providers()
    print(f"\n✓ Available providers: {', '.join(providers)}")
    
    if not providers:
        print("\n⚠ WARNING: No data providers are configured!")
        print("Please add at least one API key to your .env file:")
        print("  - ALPHAVANTAGE_API_KEY (recommended)")
        print("  - TWELVEDATA_API_KEY")
        return
    
    # Test with Indian stock (NSE)
    test_tickers = [
        ("RELIANCE.NS", "Reliance Industries (NSE)"),
        ("TCS.NS", "Tata Consultancy Services (NSE)"),
        ("INFY.NS", "Infosys (NSE)"),
    ]
    
    print("\n" + "=" * 60)
    print("Testing Data Fetch:")
    print("=" * 60)
    
    for ticker, name in test_tickers:
        print(f"\n📊 Fetching {name} ({ticker})...")
        df = fetcher.fetch_historical(ticker, period="1mo", interval="1d")
        
        if df is not None and not df.empty:
            print(f"  ✓ Success! Fetched {len(df)} rows")
            print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")
            print(f"  Latest close: ₹{df['close'].iloc[-1]:.2f}")
            print(f"  Volume: {df['volume'].iloc[-1]:,.0f}")
        else:
            print(f"  ✗ Failed to fetch data")
    
    # Test cache
    print("\n" + "=" * 60)
    print("Testing Cache:")
    print("=" * 60)
    
    print("\n📦 Fetching RELIANCE.NS again (should use cache)...")
    df_cached = fetcher.fetch_historical("RELIANCE.NS", period="1mo", interval="1d")
    
    if df_cached is not None and not df_cached.empty:
        print(f"  ✓ Cache hit! Fetched {len(df_cached)} rows")
    
    # Show cache stats
    cache_dir = Path(__file__).parent / "data" / "cache"
    if cache_dir.exists():
        cache_files = list(cache_dir.glob("*.parquet"))
        print(f"  📁 Cache contains {len(cache_files)} files")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    print("\n💡 Tips:")
    print("  1. Add ALPHAVANTAGE_API_KEY to .env for best results")
    print("  2. Cache files are stored in stockbot/data/cache/")
    print("  3. Clear cache with: fetcher.clear_cache()")
    print("  4. Indian stocks (.NS) use NSE API automatically")


if __name__ == "__main__":
    test_fetcher()