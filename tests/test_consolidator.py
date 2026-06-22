"""Tests for the signal consolidator module."""

import sys
sys.path.insert(0, "stockbot")

import pytest

from signals.consolidator import (
    consolidate_signals,
    generate_recommendations,
    calculate_portfolio_plan,
)


class TestConsolidateSignals:
    def test_empty_list_returns_empty(self):
        assert consolidate_signals([]) == []

    def test_all_none_returns_empty(self):
        assert consolidate_signals([None, None]) == []

    def test_filters_zero_score(self):
        results = [{"ticker": "TEST", "signal": "buy", "consensus_score": 0}]
        assert consolidate_signals(results) == []

    def test_returns_buy_then_sell_sorted(self):
        results = [
            {"ticker": "A", "signal": "sell", "consensus_score": 60, "price": 100,
             "target_price": 95, "stop_loss": 105, "risk_reward": 1.5},
            {"ticker": "B", "signal": "buy", "consensus_score": 80, "price": 100,
             "target_price": 110, "stop_loss": 95, "risk_reward": 2.0},
        ]
        consolidated = consolidate_signals(results)
        assert len(consolidated) == 2
        # Buys should come first, sorted by score
        assert consolidated[0]["ticker"] == "B"
        assert consolidated[1]["ticker"] == "A"

    def test_score_boost_for_good_rr(self):
        results = [
            {"ticker": "A", "signal": "buy", "consensus_score": 60, "price": 100,
             "target_price": 120, "stop_loss": 95, "risk_reward": 3.5},
        ]
        consolidated = consolidate_signals(results)
        assert consolidated[0]["consensus_score"] >= 70  # Should get +10 boost for RR >= 3

    def test_low_signals_filtered(self):
        results = [
            {"ticker": "A", "signal": "buy", "consensus_score": 15, "price": 100,
             "target_price": 110, "stop_loss": 95, "risk_reward": 1.0},
        ]
        consolidated = consolidate_signals(results)
        assert len(consolidated) == 0


class TestGenerateRecommendations:
    def test_empty_list_returns_empty(self):
        assert generate_recommendations([]) == []

    def test_returns_top_10_max(self, sample_analysis_result):
        signals = [sample_analysis_result] * 20
        recs = generate_recommendations(signals)
        assert len(recs) <= 10

    def test_recommendation_structure(self, sample_analysis_result):
        recs = generate_recommendations([sample_analysis_result])
        rec = recs[0]
        assert "ticker" in rec
        assert "action" in rec
        assert "entry_price" in rec
        assert "target_price" in rec
        assert "stop_loss" in rec
        assert "position_size" in rec
        assert "confidence" in rec
        assert rec["action"] == "BUY"

    def test_high_confidence_position_sizing(self, sample_analysis_result):
        result = dict(sample_analysis_result)
        result["consensus_score"] = 85
        result["risk_reward"] = 3.0
        recs = generate_recommendations([result])
        assert "High conviction" in recs[0]["position_size"]

    def test_low_confidence_position_sizing(self, sample_analysis_result):
        result = dict(sample_analysis_result)
        result["consensus_score"] = 35
        result["risk_reward"] = 0.5
        recs = generate_recommendations([result])
        assert "Higher risk" in recs[0]["position_size"]


class TestCalculatePortfolioPlan:
    def test_no_buy_signals(self):
        recs = [{"action": "SELL", "potential_return": 5, "confidence": 50, "risk_reward": 1.5}]
        plan = calculate_portfolio_plan(recs)
        assert "No actionable buy signals" in plan["summary"]

    def test_returns_summary_with_buy_signals(self, sample_analysis_result):
        rec = {
            "action": "BUY",
            "potential_return": 9.4,
            "confidence": 75,
            "risk_reward": 2.8,
        }
        recs = [rec] * 3
        plan = calculate_portfolio_plan(recs)
        assert "summary" in plan
        assert plan["num_trades"] > 0
        assert plan["avg_confidence"] > 0
        assert plan["avg_risk_reward"] > 0
