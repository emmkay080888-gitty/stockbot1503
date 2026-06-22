"""Shared test fixtures for Stock Signal Bot tests."""

import numpy as np
import pandas as pd
import pytest


def make_synthetic_df(days: int = 252, start_price: float = 150.0, vol: float = 0.02, trend: float = 0.0005) -> pd.DataFrame:
    """Generate a synthetic OHLCV DataFrame for testing.
    
    Creates realistic-ish daily price data with configurable volatility and trend.
    """
    np.random.seed(42)
    returns = np.random.randn(days) * vol + trend
    prices = start_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({
        "open": prices * (1 + np.random.randn(days) * 0.005),
        "high": prices * (1 + np.abs(np.random.randn(days)) * 0.01),
        "low": prices * (1 - np.abs(np.random.randn(days)) * 0.01),
        "close": prices,
        "volume": np.random.randint(500000, 5000000, days),
    }, index=pd.date_range("2023-01-01", periods=days, freq="D"))
    
    # Ensure high >= open, close, low and low <= open, close, high
    for i in range(len(df)):
        row = df.iloc[i]
        df.iloc[i, df.columns.get_loc("high")] = max(row["open"], row["close"], row["high"])
        df.iloc[i, df.columns.get_loc("low")] = min(row["open"], row["close"], row["low"])
    
    df.index.name = "date"
    return df


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """A standard 252-day synthetic dataframe with indicators added."""
    import sys
    sys.path.insert(0, "stockbot")
    from analysis.indicators import add_all_indicators
    df = make_synthetic_df()
    return add_all_indicators(df)


@pytest.fixture
def sample_weekly_df() -> pd.DataFrame:
    """Synthetic weekly dataframe."""
    return make_synthetic_df(days=104, start_price=148.0, vol=0.015, trend=0.0003)


@pytest.fixture
def sample_4h_df() -> pd.DataFrame:
    """Synthetic 4-hour dataframe."""
    return make_synthetic_df(days=90, start_price=149.0, vol=0.008, trend=0.0002)


@pytest.fixture
def sample_analysis_result() -> dict:
    """A sample signal result dict as produced by generator.analyze_ticker()."""
    return {
        "ticker": "AAPL",
        "price": 175.50,
        "signal": "buy",
        "consensus_score": 75,
        "target_price": 192.00,
        "stop_loss": 165.00,
        "risk_reward": 2.8,
        "potential_return": 9.4,
        "active_strategies": 4,
        "atr_percent": 2.1,
        "sector": "Technology",
        "market_cap": 2500000000000,
        "above_50ema": True,
        "above_200ema": True,
        "screening": {
            "passed": True,
            "liquidity": "Passes liquidity check",
            "volatility": "ATR 2.1% within range",
        },
        "strategy_detail": [
            {"strategy": "ma_crossover", "signal": "buy", "confidence": 70, "weight": 1.0,
             "weighted_confidence": 70, "reason": "Bullish MA crossover"},
            {"strategy": "rsi_mean_reversion", "signal": "buy", "confidence": 60, "weight": 0.8,
             "weighted_confidence": 48, "reason": "RSI bounce"},
            {"strategy": "volume_surge", "signal": "neutral", "confidence": 0, "weight": 0.8,
             "weighted_confidence": 0, "reason": "Normal volume"},
            {"strategy": "atr_breakout", "signal": "buy", "confidence": 55, "weight": 0.9,
             "weighted_confidence": 49.5, "reason": "ATR expansion"},
        ],
    }
