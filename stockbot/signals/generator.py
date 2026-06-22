"""Signal generator - runs strategies and compiles raw signals."""

import logging
from typing import Optional
import pandas as pd
from config import STRATEGY_WEIGHTS, MIN_SIGNAL_SCORE
from data.fetcher import fetch_historical, fetch_multiple_timeframes, fetch_fundamentals
from analysis.indicators import add_all_indicators
from analysis.strategies import run_all_strategies
from analysis.screener import (
    screen_stock,
    calculate_target_price,
    estimate_potential_return,
)

logger = logging.getLogger(__name__)


def analyze_ticker(ticker: str) -> Optional[dict]:
    """Run full analysis on a single ticker.

    Fetches data, computes indicators, runs all strategies,
    and compiles a consolidated signal.

    Returns:
        Dict with full analysis results, or None if analysis fails.
    """
    try:
        # Fetch data across timeframes
        tf_data = fetch_multiple_timeframes(ticker)
        daily_df = tf_data.get("daily")

        if daily_df is None or len(daily_df) < 50:
            logger.debug(f"{ticker}: insufficient daily data ({len(daily_df) if daily_df is not None else 0} rows)")
            return None

        # Add indicators to daily data
        daily_df = add_all_indicators(daily_df)

        if daily_df is None or len(daily_df) < 50:
            return None

        # Fetch fundamentals for screening
        info = fetch_fundamentals(ticker)

        # Screen the stock
        screened = screen_stock(ticker, daily_df, info)
        if screened is None:
            return None

        # Prepare additional timeframes for multi-TF analysis
        weekly_df = tf_data.get("weekly")
        four_h_df = tf_data.get("4h")

        if weekly_df is not None and len(weekly_df) >= 10:
            weekly_df = add_all_indicators(weekly_df)
        if four_h_df is not None and len(four_h_df) >= 20:
            four_h_df = add_all_indicators(four_h_df)

        # Run all strategies
        raw_signals = run_all_strategies(
            daily_df,
            weekly_df=weekly_df,
            four_h_df=four_h_df,
        )

        # Filter to non-neutral signals and add weights
        weighted_signals = []
        for s in raw_signals:
            if s["signal"] != "neutral" and s["confidence"] > 0:
                weight = STRATEGY_WEIGHTS.get(s["strategy"], 1.0)
                weighted_signals.append({
                    **s,
                    "weight": weight,
                    "weighted_confidence": s["confidence"] * weight,
                })

        if not weighted_signals:
            return None

        # Calculate weighted consensus
        total_weight = sum(s["weight"] for s in weighted_signals if s["signal"] == "buy" or s["signal"] == "sell")
        total_weighted_buy = sum(
            s["weighted_confidence"] for s in weighted_signals if s["signal"] == "buy"
        )
        total_weighted_sell = sum(
            s["weighted_confidence"] for s in weighted_signals if s["signal"] == "sell"
        )

        # Determine overall signal
        if total_weighted_buy > total_weighted_sell:
            overall_signal = "buy"
            consensus_score = min(
                100,
                int((total_weighted_buy / total_weight) * 100) if total_weight > 0 else 50,
            )
        elif total_weighted_sell > total_weighted_buy:
            overall_signal = "sell"
            consensus_score = min(
                100,
                int((total_weighted_sell / total_weight) * 100) if total_weight > 0 else 50,
            )
        else:
            return None

        # Calculate target and stop loss
        current_price = daily_df["close"].iloc[-1]
        price_targets = calculate_target_price(daily_df, overall_signal)
        potential_return = estimate_potential_return(
            price_targets["target"], current_price
        ) if price_targets["target"] else 0

        # Build result
        result = {
            "ticker": ticker,
            "price": round(current_price, 2),
            "signal": overall_signal,
            "consensus_score": consensus_score,
            "target_price": price_targets["target"],
            "stop_loss": price_targets["stop_loss"],
            "risk_reward": price_targets["risk_reward"],
            "potential_return": potential_return,
            "active_strategies": len(weighted_signals),
            "strategy_detail": weighted_signals,
            "screening": screened["screening"],
            "market_cap": info.get("market_cap", "N/A") if info else "N/A",
            "sector": info.get("sector", "N/A") if info else "N/A",
        }

        # Add ATR and trend info
        if "atr_percent" in daily_df.columns:
            result["atr_percent"] = round(daily_df["atr_percent"].iloc[-1], 2)
        else:
            result["atr_percent"] = 0

        # Trend info
        if "ema_50" in daily_df.columns:
            result["above_50ema"] = current_price > daily_df["ema_50"].iloc[-1]
        if "ema_200" in daily_df.columns:
            result["above_200ema"] = current_price > daily_df["ema_200"].iloc[-1]

        return result

    except Exception as e:
        logger.error(f"Error analyzing {ticker}: {e}")
        return None
