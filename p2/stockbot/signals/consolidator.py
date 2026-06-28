"""Signal consolidator - ranks and filters signals for reporting."""

import logging
from typing import Optional
from config import MIN_SIGNAL_SCORE

logger = logging.getLogger(__name__)


def consolidate_signals(results: list[Optional[dict]]) -> list[dict]:
    """Consolidate and rank all analyzed signals.

    Takes raw analysis results, filters out weak signals,
    sorts by consensus score, and formats for output.

    Args:
        results: List of analysis results (some may be None for failed tickers).

    Returns:
        Ranked list of consolidated signal dicts sorted by score.
    """
    # Filter out failed analyses
    valid = [r for r in results if r is not None and r.get("consensus_score", 0) > 0]

    if not valid:
        return []

    # Separate buy and sell signals
    buy_signals = [r for r in valid if r["signal"] == "buy"]
    sell_signals = [r for r in valid if r["signal"] == "sell"]

    # Score boost for strong risk/reward
    for s in buy_signals + sell_signals:
        rr = s.get("risk_reward", 0)
        if rr >= 3.0:
            s["consensus_score"] = min(100, s["consensus_score"] + 10)
        elif rr >= 2.0:
            s["consensus_score"] = min(100, s["consensus_score"] + 5)

    # Filter by minimum score
    buy_signals = [s for s in buy_signals if s["consensus_score"] >= MIN_SIGNAL_SCORE]
    sell_signals = [s for s in sell_signals if s["consensus_score"] >= MIN_SIGNAL_SCORE]

    # Sort by score descending
    buy_signals.sort(key=lambda x: x["consensus_score"], reverse=True)
    sell_signals.sort(key=lambda x: x["consensus_score"], reverse=True)

    # Limit to top signals
    consolidated = buy_signals + sell_signals

    return consolidated


def generate_recommendations(consolidated: list[dict]) -> list[dict]:
    """Generate actionable recommendations from consolidated signals.

    Adds position sizing suggestions (as percentage of portfolio).

    Returns:
        List of recommendation dicts with trade plan details.
    """
    recommendations = []

    for signal in consolidated[:10]:  # Top 10 signals
        rec = {
            "ticker": signal["ticker"],
            "action": signal["signal"].upper(),
            "entry_price": signal["price"],
            "target_price": signal["target_price"],
            "stop_loss": signal["stop_loss"],
            "potential_return": signal["potential_return"],
            "risk_reward": signal["risk_reward"],
            "confidence": signal["consensus_score"],
            "active_strategies": signal.get("active_strategies", 0),
            "strategy_breakdown": signal.get("strategy_detail", []),
        }

        # Suggest position size based on confidence
        confidence = signal["consensus_score"]
        rr = signal.get("risk_reward", 0)

        if confidence >= 80 and rr >= 2.5:
            rec["position_size"] = "10-15% (High conviction)"
        elif confidence >= 65 and rr >= 2.0:
            rec["position_size"] = "5-10% (Moderate conviction)"
        elif confidence >= 50:
            rec["position_size"] = "2-5% (Speculative)"
        else:
            rec["position_size"] = "1-2% (Higher risk)"

        # Expected time horizon
        rec["time_horizon"] = "5-15 trading days (swing trade)"

        recommendations.append(rec)

    return recommendations


def calculate_portfolio_plan(recommendations: list[dict]) -> dict:
    """Calculate a mock portfolio plan based on recommendations.

    This helps show the potential of the signal system.
    """
    buy_recs = [r for r in recommendations if r["action"] == "BUY"]

    if not buy_recs:
        return {
            "summary": "No actionable buy signals found",
            "potential_profit": 0,
            "high_conviction_trades": 0,
        }

    # Take top 5 buy signals for the portfolio plan
    top_recs = buy_recs[:5]

    total_potential = sum(r.get("potential_return", 0) for r in top_recs)
    avg_confidence = sum(r.get("confidence", 0) for r in top_recs) / len(top_recs)
    avg_rr = sum(r.get("risk_reward", 0) for r in top_recs) / len(top_recs)

    # Simulate even allocation across top 5
    position_size = min(20, 100 / len(top_recs))

    return {
        "summary": f"Top {len(top_recs)} trade signals identified",
        "num_trades": len(top_recs),
        "avg_confidence": round(avg_confidence, 1),
        "avg_risk_reward": round(avg_rr, 2),
        "avg_potential_return": round(total_potential / len(top_recs), 2),
        "suggested_allocation": f"{position_size:.0f}% per trade",
        "potential_profit": round(total_potential, 2),
        "high_conviction_trades": sum(
            1 for r in top_recs if r.get("risk_reward", 0) >= 2.5
        ),
    }
