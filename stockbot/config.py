"""Configuration module for the Stock Signal Bot."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Paths ---
PROJECT_ROOT = Path(__file__).parent
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "reports"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- API Keys ---
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY", "")

# --- Scanning Settings ---
MAX_STOCKS_TO_SCAN = int(os.getenv("MAX_STOCKS_TO_SCAN", "100"))
MIN_SIGNAL_SCORE = int(os.getenv("MIN_SIGNAL_SCORE", "30"))

# --- Strategy Weights (how much each strategy contributes to final score) ---
# These are tuned for swing trading (5-20 day holding period)
STRATEGY_WEIGHTS = {
    "ma_crossover": 1.0,
    "rsi_mean_reversion": 0.8,
    "macd_divergence": 1.2,
    "bollinger_squeeze": 1.0,
    "volume_surge": 0.8,
    "multi_tf_confluence": 1.3,
    "atr_breakout": 0.9,
}

# --- Technical Analysis Parameters ---
TA_PARAMS = {
    "ema_fast": 9,
    "ema_slow": 21,
    "ema_trend": 50,
    "ema_long_trend": 200,
    "rsi_period": 14,
    "rsi_oversold": 30,
    "rsi_overbought": 70,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "bb_period": 20,
    "bb_std": 2.0,
    "atr_period": 14,
    "volume_ma_period": 20,
    "volume_surge_multiplier": 1.5,
}

# --- Screening Filters ---
SCREENING = {
    "min_price": 5.0,          # Minimum stock price
    "min_volume": 10_000,      # Minimum average daily volume (Indian market default)
    "min_market_cap": 50_000_000,  # Minimum market cap (₹5Cr — appropriate for NSE)
    "max_atr_percent": 15.0,   # Maximum ATR as % of price (avoid too volatile)
    "min_atr_percent": 1.0,    # Minimum ATR as % of price (needs room to move)
}

# --- Output Settings ---
OUTPUT_FORMATS = ["cli", "json", "csv"]
