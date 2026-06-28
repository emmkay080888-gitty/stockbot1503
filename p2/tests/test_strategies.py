"""Tests for trading strategy implementations."""

import sys
sys.path.insert(0, "stockbot")

import numpy as np
import pandas as pd
import pytest

from analysis.strategies import (
    ma_crossover_strategy,
    rsi_mean_reversion_strategy,
    macd_divergence_strategy,
    bollinger_squeeze_strategy,
    volume_surge_strategy,
    multi_tf_confluence_strategy,
    atr_breakout_strategy,
    run_all_strategies,
)


class TestMACrossover:
    def test_returns_dict_with_expected_keys(self, sample_df):
        result = ma_crossover_strategy(sample_df)
        assert "signal" in result and "confidence" in result
        assert "reason" in result and "strategy" in result
        assert result["signal"] in ("buy", "sell", "neutral")

    def test_neutral_for_short_data(self):
        short = pd.DataFrame({"close": [100, 101], "ema_9": [100, 101], "ema_21": [99, 100], "ema_50": [98, 99]})
        result = ma_crossover_strategy(short)
        assert result["signal"] == "neutral"

    def test_buy_on_bullish_crossover(self, sample_df):
        df = sample_df.tail(30).copy()
        df.loc[df.index[-1], "ema_9"] = df["ema_21"].iloc[-1] + 5
        df.loc[df.index[-1], "close"] = df["ema_50"].iloc[-1] + 10
        result = ma_crossover_strategy(df)
        assert result["signal"] in ("buy", "neutral")

    def test_confidence_bounded(self, sample_df):
        result = ma_crossover_strategy(sample_df)
        assert 0 <= result["confidence"] <= 100


class TestRSIMeanReversion:
    def test_returns_dict_with_expected_keys(self, sample_df):
        result = rsi_mean_reversion_strategy(sample_df)
        assert "signal" in result

    def test_neutral_without_rsi(self):
        df = pd.DataFrame({"close": [100] * 30})
        result = rsi_mean_reversion_strategy(df)
        assert result["signal"] == "neutral"

    def test_buy_on_oversold(self, sample_df):
        df = sample_df.tail(30).copy()
        df["rsi"] = 25.0  # Oversold for all rows
        result = rsi_mean_reversion_strategy(df)
        assert result["signal"] == "buy"

    def test_sell_on_overbought(self, sample_df):
        df = sample_df.tail(30).copy()
        df["rsi"] = 75.0  # Overbought for all rows
        result = rsi_mean_reversion_strategy(df)
        assert result["signal"] == "sell"


class TestMACDDivergence:
    def test_returns_dict(self, sample_df):
        result = macd_divergence_strategy(sample_df)
        assert "signal" in result

    def test_neutral_without_macd(self):
        df = pd.DataFrame({"close": [100] * 40})
        result = macd_divergence_strategy(df)
        assert result["signal"] == "neutral"


class TestBollingerSqueeze:
    def test_returns_dict(self, sample_df):
        result = bollinger_squeeze_strategy(sample_df)
        assert "signal" in result

    def test_neutral_without_bb(self):
        df = pd.DataFrame({"close": [100] * 30})
        result = bollinger_squeeze_strategy(df)
        assert result["signal"] == "neutral"


class TestVolumeSurge:
    def test_returns_dict(self, sample_df):
        result = volume_surge_strategy(sample_df)
        assert "signal" in result

    def test_neutral_without_volume_ratio(self):
        df = pd.DataFrame({"close": [100] * 30})
        result = volume_surge_strategy(df)
        assert result["signal"] == "neutral"


class TestATRBreakout:
    def test_returns_dict(self, sample_df):
        result = atr_breakout_strategy(sample_df)
        assert "signal" in result

    def test_neutral_without_atr(self):
        df = pd.DataFrame({"close": [100] * 25})
        result = atr_breakout_strategy(df)
        assert result["signal"] == "neutral"


class TestMultiTFConfluence:
    def test_returns_dict(self, sample_df):
        result = multi_tf_confluence_strategy(sample_df)
        assert "signal" in result

    def test_short_df_returns_neutral(self):
        short = pd.DataFrame({"close": [100] * 50})
        result = multi_tf_confluence_strategy(short)
        assert result["signal"] == "neutral"

    def test_accepts_weekly_and_4h(self, sample_df, sample_weekly_df, sample_4h_df):
        result = multi_tf_confluence_strategy(
            sample_df, weekly_df=sample_weekly_df, four_h_df=sample_4h_df
        )
        assert "signal" in result
        assert 0 <= result["confidence"] <= 100


class TestRunAllStrategies:
    def test_returns_list(self, sample_df):
        results = run_all_strategies(sample_df)
        assert isinstance(results, list)

    def test_all_strategies_represented(self, sample_df):
        results = run_all_strategies(sample_df)
        strategies_found = {r["strategy"] for r in results}
        expected = {
            "ma_crossover", "rsi_mean_reversion", "macd_divergence",
            "bollinger_squeeze", "volume_surge", "atr_breakout",
            "multi_tf_confluence",
        }
        assert strategies_found == expected

    def test_all_have_required_keys(self, sample_df):
        results = run_all_strategies(sample_df)
        for r in results:
            assert "signal" in r
            assert "confidence" in r
            assert "reason" in r
            assert "strategy" in r

    def test_confidence_bounded(self, sample_df):
        results = run_all_strategies(sample_df)
        for r in results:
            assert 0 <= r["confidence"] <= 100

    def test_passes_weekly_4h_data(self, sample_df, sample_weekly_df, sample_4h_df):
        results = run_all_strategies(
            sample_df, weekly_df=sample_weekly_df, four_h_df=sample_4h_df
        )
        assert len(results) == 7
