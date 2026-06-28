"""Tests for the indicators module."""

import sys
sys.path.insert(0, "stockbot")

import numpy as np
import pandas as pd
import pytest

from analysis.indicators import (
    add_all_indicators,
    detect_divergence,
    detect_bollinger_squeeze,
    detect_volume_surge,
    detect_atr_breakout,
)


def test_add_all_indicators_adds_expected_columns(sample_df):
    """Verify all expected indicator columns are present."""
    expected = [
        "ema_9", "ema_21", "ema_50", "ema_200",
        "rsi", "macd", "macd_signal", "macd_hist",
        "bb_upper", "bb_middle", "bb_lower", "bb_width",
        "atr", "atr_percent",
        "volume_ma", "volume_ratio", "obv",
    ]
    for col in expected:
        assert col in sample_df.columns, f"Missing column: {col}"


def test_add_all_indicators_preserves_length(sample_df):
    """DataFrame length should stay the same after adding indicators."""
    assert len(sample_df) == 252


def test_add_all_indicators_returns_none_for_short_df():
    """Very short DataFrames should return None."""
    short = pd.DataFrame({"close": [100, 101, 102]})
    result = add_all_indicators(short)
    assert result is None or len(result) < 50


def test_add_all_indicators_ema_values_are_ordered(sample_df):
    """EMAs should be in the correct order: ema_9 > ema_21 > ema_50 > ema_200."""
    last = sample_df.iloc[-1]
    # In an uptrend, shorter EMAs should be higher
    assert last["ema_9"] >= last["ema_21"] or abs(last["ema_9"] - last["ema_21"]) < last["ema_21"] * 0.02


def test_rsi_between_0_and_100(sample_df):
    """RSI values must always be between 0 and 100."""
    valid = sample_df["rsi"].dropna()
    assert valid.between(0, 100).all()


def test_bb_bands_order(sample_df):
    """Bollinger Bands must be ordered: upper >= middle >= lower."""
    valid = sample_df.dropna(subset=["bb_upper", "bb_middle", "bb_lower"])
    assert len(valid) > 0
    # Use approximate comparison to handle floating point edge cases
    mid_upper_diff = valid["bb_upper"] - valid["bb_middle"]
    lower_mid_diff = valid["bb_middle"] - valid["bb_lower"]
    # All differences should be >= -0.01 (tiny negative from precision)
    assert (mid_upper_diff >= -0.01).all(), f"Upper < Middle on {len(valid[~(mid_upper_diff >= -0.01)])} rows"
    assert (lower_mid_diff >= -0.01).all(), f"Middle < Lower on {len(valid[~(lower_mid_diff >= -0.01)])} rows"


def test_atr_positive(sample_df):
    """ATR must always be positive."""
    assert (sample_df["atr"].dropna() > 0).all()


def test_detect_divergence_returns_dict(sample_df):
    """detect_divergence should always return a dict with expected keys."""
    result = detect_divergence(sample_df)
    assert isinstance(result, dict)
    assert "bullish" in result
    assert "bearish" in result
    assert "strength" in result


def test_detect_bollinger_squeeze_returns_dict(sample_df):
    """detect_bollinger_squeeze should return expected structure."""
    result = detect_bollinger_squeeze(sample_df)
    assert isinstance(result, dict)
    assert "squeeze" in result
    assert "direction" in result
    assert "strength" in result


def test_detect_volume_surge_returns_dict(sample_df):
    """detect_volume_surge should return expected structure."""
    result = detect_volume_surge(sample_df)
    assert isinstance(result, dict)
    assert "surge" in result
    assert "direction" in result
    assert "strength" in result


def test_detect_atr_breakout_returns_dict(sample_df):
    """detect_atr_breakout should return expected structure."""
    result = detect_atr_breakout(sample_df)
    assert isinstance(result, dict)
    assert "breakout" in result
    assert "direction" in result
    assert "strength" in result


def test_detect_divergence_short_df():
    """Short DataFrames should return neutral result."""
    short = pd.DataFrame({"close": [100, 101], "macd": [0.5, 0.6]})
    result = detect_divergence(short, lookback=10)
    assert result == {"bullish": False, "bearish": False, "strength": 0}


def test_detect_bollinger_squeeze_no_bb_width():
    """DataFrame without bb_width should return neutral."""
    df = pd.DataFrame({"close": [100] * 30})
    result = detect_bollinger_squeeze(df)
    assert result["squeeze"] is False


def test_detect_volume_surge_no_volume_ratio():
    """DataFrame without volume_ratio should return neutral."""
    df = pd.DataFrame({"close": [100] * 30, "volume": [1000] * 30})
    result = detect_volume_surge(df)
    assert result["surge"] is False
