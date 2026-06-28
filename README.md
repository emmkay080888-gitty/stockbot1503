# Stock Signal Bot 1503

A multi-strategy stock signal consolidation system for swing trading (5-20 day holding period). This project includes multiple implementations and versions for different deployment scenarios.

## Project Structure

```
stockbot1503/
├── stockbot/           # Main Python application (primary version)
│   ├── analysis/       # Backtesting and strategy evaluation
│   ├── data/          # Multi-source data fetching (yfinance, NSE, etc.)
│   ├── output/        # Report generation (CLI, JSON, CSV exports)
│   ├── pages/         # Streamlit UI pages
│   ├── signals/       # Signal generation and consolidation
│   ├── sounds/        # Audio notifications
│   ├── utils/         # Auth, config helpers, market utilities
│   └── tests/         # Unit tests
│
├── p1/                # Next.js web application (v1)
├── p2/                # Docker-based deployment setup
├── p3/                # Node.js backend API
├── p4/                # Next.js web application (v2)
│
└── Sounds/            # Shared audio files
```

## Main Application (stockbot/)

The primary implementation is a Python-based stock signal bot with the following features:

### Features
- **Multi-Strategy Signal Generation**: 7 different trading strategies
  - MA Crossover
  - RSI Mean Reversion
  - MACD Divergence
  - Bollinger Squeeze
  - Volume Surge
  - Multi-Timeframe Confluence
  - ATR Breakout

- **Data Sources**: 
  - Yahoo Finance (yfinance)
  - NSE (National Stock Exchange of India)
  - Multi-source fetcher with caching

- **Output Formats**:
  - CLI reports
  - JSON export
  - CSV export

- **Backtesting**: Historical strategy validation

### Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Run the bot**:
   ```bash
   # Scan S&P 500 for signals
   python main.py scan --universe sp500 --max-stocks 50
   
   # Scan watchlist
   python main.py watchlist
   
   # Scan specific tickers
   python main.py tickers AAPL,MSFT,GOOGL
   
   # Backtest strategies
   python main.py backtest --universe watchlist --months 12
   ```

### Streamlit UI

Launch the interactive web interface:
```bash
streamlit run app.py
```

### Configuration

Key settings in `config.py`:
- `MAX_STOCKS_TO_SCAN`: Maximum stocks to analyze (default: 100)
- `MIN_SIGNAL_SCORE`: Minimum signal strength threshold (default: 30)
- `STRATEGY_WEIGHTS`: Strategy contribution weights
- `TA_PARAMS`: Technical analysis parameters
- `SCREENING`: Stock screening filters

### API Keys

Required environment variables:
- `TWELVEDATA_API_KEY`: For TwelveData API
- `ALPHAVANTAGE_API_KEY`: For Alpha Vantage API

## Web Versions

### p1/ - Next.js v1
- Next.js 14+ with TypeScript
- Prisma ORM
- Modern React UI

### p4/ - Next.js v2
- Updated Next.js implementation
- Enhanced features
- Prisma with seed scripts

### p3/ - Node.js Backend
- Express.js server
- RESTful API
- Middleware and routing

### p2/ - Docker Deployment
- Docker Compose setup
- Production-ready configuration
- Multi-service architecture

## Testing

Run the test suite:
```bash
# From stockbot/ directory
python -m pytest tests/

# Or using unittest
python -m unittest discover tests/
```

## Documentation

- `CPIS_INTEGRATION.md` - CPIS integration details (identity_project)
- `DEPLOY.md` - Deployment instructions
- `DATA_SOURCES.md` - Data source documentation
- `TICKER_SEARCH.md` - Ticker search functionality

## Requirements

- Python 3.11+ (3.12 recommended for Streamlit Cloud)
- PostgreSQL (for web versions)
- Node.js 18+ (for web versions)
- API keys for data sources

## License

[Add your license here]