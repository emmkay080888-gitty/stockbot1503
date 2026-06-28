# Data Sources & Fetching Architecture

## Overview

The Stock Signal Bot now uses a **multi-source data fetching architecture** that provides:
- ✅ **Automatic failover** between multiple data providers
- ✅ **Smart caching** to reduce API calls and improve speed
- ✅ **Data validation** to ensure quality and consistency
- ✅ **Real-time data** from multiple reliable sources
- ✅ **Indian market support** via NSE official API

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           Multi-Source Data Fetcher                     │
├─────────────────────────────────────────────────────────┤
│  1. Check Cache (1 hour TTL)                           │
│     ↓ Cache miss                                         │
│  2. Try Alpha Vantage (Priority 1)                      │
│     ↓ Failed/Unavailable                                │
│  3. Try NSE Official API (Priority 2)                   │
│     ↓ Failed/Unavailable                                │
│  4. Try Twelve Data (Priority 3)                        │
│     ↓ Failed/Unavailable                                │
│  5. Try Yahoo Finance (Priority 4 - Fallback)           │
│     ↓ All failed                                         │
│  6. Return None (no data available)                     │
└─────────────────────────────────────────────────────────┘
```

## Data Providers

### 1. Alpha Vantage (Priority 1) ⭐ Recommended
- **Free tier**: 25 calls/day, 5 calls/minute
- **Coverage**: Global stocks (US, India, etc.)
- **Quality**: Excellent, real-time data
- **Setup**: Get free API key at https://www.alphavantage.co/support/#api-key
- **Usage**: Add to `.env` file:
  ```bash
  ALPHAVANTAGE_API_KEY=your_key_here
  ```

### 2. NSE Official API (Priority 2) 🇮🇳 Indian Markets
- **Free**: No API key required
- **Coverage**: NSE stocks (.NS suffix)
- **Quality**: Official NSE data, very reliable
- **Features**: Automatic session management, respects rate limits
- **Usage**: Works automatically for Indian stocks

### 3. Twelve Data (Priority 3)
- **Free tier**: Limited calls/day
- **Coverage**: Global stocks
- **Quality**: Good, real-time data
- **Setup**: Get API key at https://twelvedata.com/apikey
- **Usage**: Add to `.env` file:
  ```bash
  TWELVEDATA_API_KEY=your_key_here
  ```

### 4. Yahoo Finance (Priority 4 - Fallback)
- **Free**: No API key required
- **Coverage**: Global stocks
- **Quality**: Variable, often delayed (15-20 min)
- **Limitations**: Rate limiting, inconsistent responses
- **Usage**: Works automatically as last resort

## Caching System

### Cache Location
```
stockbot/data/cache/
```

### Cache Format
- **Format**: Parquet (efficient, compressed)
- **Naming**: `{ticker}_{period}_{interval}.parquet`
- **TTL**: 1 hour (configurable via `max_age_hours`)

### Cache Benefits
- ⚡ **Speed**: Instant data retrieval from cache
- 💰 **Cost**: Reduces API calls (saves on paid tiers)
- 🚀 **Reliability**: Works offline for cached data
- 📊 **Consistency**: Same data during session

### Cache Management
```python
from data.multi_source_fetcher import get_fetcher

fetcher = get_fetcher()

# Clear specific ticker cache
fetcher.clear_cache("RELIANCE.NS")

# Clear all cache
fetcher.clear_cache()

# Check available providers
print(fetcher.get_available_providers())
# Output: ['nse', 'alphavantage', 'yahoo']
```

## Data Validation

All fetched data undergoes strict validation:

### Required Checks
- ✅ All OHLCV columns present
- ✅ Minimum 5 data points
- ✅ No null values
- ✅ No negative prices
- ✅ Price consistency (high ≥ low, high ≥ close, etc.)

### Validation Benefits
- **Prevents bad signals**: Invalid data won't generate false signals
- **Ensures consistency**: All providers return standardized format
- **Early failure**: Detects issues before analysis

## Usage

### Basic Usage (Drop-in Replacement)
```python
from data.fetcher import fetch_historical

# Old code still works!
df = fetch_historical("RELIANCE.NS", period="6mo", interval="1d")
```

### Advanced Usage
```python
from data.multi_source_fetcher import get_fetcher

fetcher = get_fetcher()

# Fetch with specific options
df = fetcher.fetch_historical(
    ticker="TCS.NS",
    period="1y",
    interval="1d",
    use_cache=True  # Enable/disable cache
)

# Fetch multiple timeframes
timeframes = fetcher.fetch_multiple_timeframes("INFY.NS")
# Returns: {"daily": df, "weekly": df, "4h": df}

# Get available providers
providers = fetcher.get_available_providers()
```

### Fetch Fundamentals
```python
from data.fetcher import fetch_fundamentals

fundamentals = fetch_fundamentals("RELIANCE.NS")
# Returns: {
#   "market_cap": ...,
#   "pe_ratio": ...,
#   "sector": ...,
#   ...
# }
```

## Configuration

### Environment Variables
Add to your `.env` file:

```bash
# Primary data source (recommended)
ALPHAVANTAGE_API_KEY=your_alpha_vantage_key

# Fallback data source
TWELVEDATA_API_KEY=your_twelve_data_key

# Scanning settings
MAX_STOCKS_TO_SCAN=100
MIN_SIGNAL_SCORE=30
```

### Provider Priority
Customize provider order in `multi_source_fetcher.py`:

```python
def _setup_providers(self):
    # Add in priority order (lower number = higher priority)
    self.providers.append(AlphaVantageProvider())    # Priority 1
    self.providers.append(NSEOfficialProvider())     # Priority 2
    self.providers.append(TwelveDataProvider())      # Priority 5
    self.providers.append(YahooFinanceProvider())    # Priority 10
```

## Performance Tips

### 1. Use Caching
```python
# Enable cache (default)
df = fetcher.fetch_historical(ticker, use_cache=True)

# Disable cache for real-time data
df = fetcher.fetch_historical(ticker, use_cache=False)
```

### 2. Batch Requests
```python
# Fetch multiple tickers efficiently
tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
for ticker in tickers:
    df = fetcher.fetch_historical(ticker, period="1mo")
    # Process data...
```

### 3. Use Appropriate Timeframes
```python
# For screening: Use daily data
df = fetcher.fetch_historical(ticker, period="6mo", interval="1d")

# For day trading: Use hourly data
df = fetcher.fetch_historical(ticker, period="3mo", interval="60m")
```

## Troubleshooting

### No Providers Available
```
⚠ WARNING: No data providers are configured!
```
**Solution**: Add at least one API key to `.env` file

### Rate Limit Hit
```
[AlphaVantage] Rate limit hit: Note from API
```
**Solution**: Wait 1 minute or add more API keys

### NSE API Failing
```
[NSE] HTTP 403 for TCS.NS
```
**Solution**: NSE may be blocking. The fetcher will automatically fall back to Yahoo Finance.

### Cache Issues
```python
# Clear cache if data seems stale
fetcher.clear_cache()
```

## Migration from Old Fetcher

### Before (Old API)
```python
from data.fetcher import fetch_historical

df = fetch_historical("RELIANCE.NS")
```

### After (New API - Same Code!)
```python
from data.fetcher import fetch_historical

df = fetch_historical("RELIANCE.NS")  # Works exactly the same!
```

**No code changes required!** The old `fetcher.py` is now a compatibility wrapper.

## Testing

Run the test script:
```bash
cd stockbot
python test_data_fetcher.py
```

Expected output:
```
✓ Available providers: nse, yahoo
✓ Success! Fetched 23 rows
✓ Cache hit! Fetched 23 rows
```

## Future Improvements

### Planned Additions
- [ ] WebSocket support for real-time streaming
- [ ] Additional providers (Polygon.io, IEX Cloud)
- [ ] Options chain data provider
- [ ] Fundamental data from multiple sources
- [ ] News sentiment integration
- [ ] Historical data compression for long-term storage

### Contributing
To add a new data provider:
1. Create a new class inheriting from `DataProvider`
2. Implement `fetch_historical()` method
3. Set `priority` (lower = higher priority)
4. Add to `MultiSourceFetcher._setup_providers()`

## Support

For issues or questions:
1. Check this documentation
2. Run `test_data_fetcher.py` to diagnose
3. Check logs for provider-specific errors
4. Verify API keys in `.env` file

## Summary

| Feature | Old Fetcher | New Multi-Source Fetcher |
|---------|-------------|-------------------------|
| Data Sources | 1 (Yahoo) | 4+ (Alpha Vantage, NSE, Twelve Data, Yahoo) |
| Failover | ❌ No | ✅ Yes |
| Caching | ❌ No | ✅ Yes (Parquet, 1hr TTL) |
| Validation | ⚠️ Basic | ✅ Strict |
| Reliability | ⚠️ Variable | ✅ High |
| Speed | 🐌 Slow | ⚡ Fast (with cache) |
| Indian Stocks | ⚠️ Delayed | ✅ Real-time (NSE API) |