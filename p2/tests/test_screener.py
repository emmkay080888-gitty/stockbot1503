"""Tests for the stock screening module."""

import sys
sys.path.insert(0, "stockbot")

import numpy as np
import pandas as pd
import pytest

from analysis.screener import (
    screen_by_liquidity,
    screen_by_volatility,
    calculate_target_price,
    estimate_potential_return,
    screen_stock,
)


class TestScreenByLiquidity:
    def test_insufficient_data(self):
        passed, reason = screen_by_liquidity(pd.DataFrame({"close": [100]}))
        assert not passed
        assert "Insufficient" in reason

    def test_price_below_minimum(self):
        df = pd.DataFrame({"close": [2.0] * 30, "volume": [1000000] * 30})
        passed, reason = screen_by_liquidity(df)
        assert not passed
        assert "below minimum" in reason

    def test_passes_with_good_data(self, sample_df):
        passed, reason = screen_by_liquidity(sample_df)
        assert passed

    def test_market_cap_filter_fails(self, sample_df):
        info = {"market_cap": 100_000}  # Too low
        passed, reason = screen_by_liquidity(sample_df, info)
        assert not passed
        assert "Market cap" in reason

    def test_market_cap_filter_passes(self, sample_df):
        info = {"market_cap": 1_000_000_000}
        passed, reason = screen_by_liquidity(sample_df, info)
        assert passed


class TestScreenByVolatility:
    def test_insufficient_data(self):
        passed, reason = screen_by_volatility(pd.DataFrame({"close": [100]}))
        assert not passed

    def test_returns_result(self, sample_df):
        passed, reason = screen_by_volatility(sample_df)
        # Should always return a result (True or False)
        assert isinstance(passed, bool)
        assert isinstance(reason, str)

    def test_missing_atr_column(self):
        df = pd.DataFrame({"close": [100] * 30})
        passed, reason = screen_by_volatility(df)
        assert passed
        assert "No ATR data" in reason


class TestCalculateTargetPrice:
    def test_returns_dict_with_keys(self, sample_df):
        result = calculate_target_price(sample_df, "buy")
        assert "target" in result
        assert "stop_loss" in result
        assert "risk_reward" in result

    def test_buy_target_higher_than_entry(self, sample_df):
        result = calculate_target_price(sample_df, "buy")
        close = sample_df["close"].iloc[-1]
        if result["target"]:
            assert result["target"] > close

    def test_sell_target_lower_than_entry(self, sample_df):
        result = calculate_target_price(sample_df, "sell")
        close = sample_df["close"].iloc[-1]
        if result["target"]:
            assert result["target"] < close

    def test_buy_stop_below_entry(self, sample_df):
        result = calculate_target_price(sample_df, "buy")
        close = sample_df["close"].iloc[-1]
        if result["stop_loss"]:
            assert result["stop_loss"] < close

    def test_sell_stop_above_entry(self, sample_df):
        result = calculate_target_price(sample_df, "sell")
        close = sample_df["close"].iloc[-1]
        if result["stop_loss"]:
            assert result["stop_loss"] > close

    def test_risk_reward_positive(self, sample_df):
        result = calculate_target_price(sample_df, "buy")
        assert result["risk_reward"] >= 0

    def test_short_df_returns_zeros(self):
        short = pd.DataFrame({"close": [100, 101]})
        result = calculate_target_price(short, "buy")
        assert result["target"] is None
        assert result["risk_reward"] == 0


class TestEstimatePotentialReturn:
    def test_positive_return(self):
        ret = estimate_potential_return(target_price=110, current_price=100)
        assert ret == 10.0

    def test_negative_return(self):
        ret = estimate_potential_return(target_price=90, current_price=100)
        assert ret == -10.0

    def test_zero_return(self):
        ret = estimate_potential_return(target_price=100, current_price=100)
        assert ret == 0.0

    def test_zero_price(self):
        ret = estimate_potential_return(target_price=100, current_price=0)
        assert ret == 0.0


class TestScreenStock:
    def test_returns_none_for_bad_data(self, sample_df):
        info = {"market_cap": 100}
        result = screen_stock("TEST", sample_df, info)
        assert result is None

    def test_passes_for_good_data(self, sample_df):
        info = {"market_cap": 10_000_000_000}
        result = screen_stock("TEST", sample_df, info)
        assert result is not None
        assert result["screening"]["passed"] is True
