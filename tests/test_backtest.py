"""Tests for the backtesting module."""

import sys
sys.path.insert(0, "stockbot")

import numpy as np
import pandas as pd
import pytest

from analysis.backtest import (
    simulate_trade,
    backtest_ticker,
    run_backtest,
    print_backtest_report,
)


class TestSimulateTrade:
    def test_buy_trade_returns_dict(self, sample_df):
        result = simulate_trade(sample_df, 50, "buy")
        assert isinstance(result, dict)
        assert "result" in result
        assert "return_pct" in result
        assert "entry_price" in result
        assert "exit_price" in result
        assert "holding_days" in result

    def test_error_on_last_index(self, sample_df):
        result = simulate_trade(sample_df, len(sample_df) - 1, "buy")
        assert result["result"] == "error"

    def test_result_is_win_or_loss(self, sample_df):
        result = simulate_trade(sample_df, 100, "buy", holding_period=5)
        assert result["result"] in ("win", "loss")

    def test_entry_price_matches_df(self, sample_df):
        result = simulate_trade(sample_df, 50, "buy")
        assert result["entry_price"] == round(sample_df.iloc[50]["close"], 2)

    def test_sell_trade_returns_result(self, sample_df):
        result = simulate_trade(sample_df, 50, "sell")
        assert result["result"] in ("win", "loss")

    def test_holding_days_positive(self, sample_df):
        result = simulate_trade(sample_df, 50, "buy", holding_period=10)
        assert result["holding_days"] > 0

    def test_stop_loss_hit_triggers_early_exit(self, sample_df):
        result = simulate_trade(sample_df, 50, "buy", holding_period=20, stop_loss_pct=0.5)
        # Very tight stop should be hit early
        holding = result.get("holding_days", 0)
        assert holding <= 5  # Should exit very early


class TestBacktestTicker:
    def test_returns_list(self, sample_df, monkeypatch):
        import analysis.backtest as bt_mod
        monkeypatch.setattr(bt_mod, "fetch_historical", lambda *args, **kwargs: sample_df)
        trades = backtest_ticker("TEST", lookback_months=12, signal_interval_days=20)
        assert isinstance(trades, list)

    def test_insufficient_data_returns_empty(self, monkeypatch):
        import analysis.backtest as bt_mod
        monkeypatch.setattr(bt_mod, "fetch_historical", lambda *args, **kwargs: None)
        trades = backtest_ticker("TEST", lookback_months=12)
        assert trades == []


class TestRunBacktest:
    def test_returns_dict_with_keys(self):
        result = run_backtest([], lookback_months=12)
        assert "total_trades" in result
        assert "win_rate" in result
        assert "avg_return" in result
        assert "trades" in result
        assert "summary" in result

    def test_empty_tickers_returns_zero_trades(self):
        result = run_backtest([], lookback_months=12)
        assert result["total_trades"] == 0


class TestPrintBacktestReport:
    def test_runs_without_error(self):
        results = {
            "total_trades": 0,
            "win_rate": 0,
            "avg_return": 0,
            "trades_over_10pct": 0,
            "trades": [],
            "summary": "No trades",
        }
        # Should not raise
        print_backtest_report(results)

    def test_runs_with_trades(self):
        results = {
            "total_trades": 10,
            "win_rate": 60.0,
            "avg_return": 5.2,
            "avg_win": 12.0,
            "avg_loss": -5.0,
            "profitable_trades": 6,
            "trades_over_10pct": 3,
            "best_trade": 25.0,
            "worst_trade": -8.0,
            "avg_holding_days": 7.5,
            "tickers_with_signals": 5,
            "summary": "Test summary",
            "trades": [
                {"ticker": "AAPL", "return_pct": 15.0, "holding_days": 10,
                 "signal_date": "2023-06-01", "signal_type": "buy",
                 "signal_score": 75, "strategies_triggered": 4},
            ],
        }
        print_backtest_report(results)
