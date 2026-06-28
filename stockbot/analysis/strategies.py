"""Individual trading strategy implementations.

Each strategy analyzes a dataframe and returns a signal dict:
    {
        "signal": "buy" | "sell" | "neutral",
        "confidence": 0-100,
        "reason": str,
        "strategy": str
    }
"""

import pandas as pd
import numpy as np
from config import TA_PARAMS
from analysis.indicators import (
    detect_divergence,
    detect_bollinger_squeeze,
    detect_volume_surge,
    detect_atr_breakout,
)


def _safe(val, default=0.0):
    """Return a safe numeric value, replacing NaN/None with default."""
    if val is None:
        return default
    if hasattr(val, 'item'):
        val = val.item()
    try:
        import math
        if math.isnan(val):
            return default
    except (TypeError, ValueError):
        return default
    return val


def ma_crossover_strategy(df: pd.DataFrame) -> dict:
    """Moving Average Crossover Strategy.

    Bullish: Fast EMA crosses above slow EMA.
    Bearish: Fast EMA crosses below slow EMA.
    Trend filter: Price above 50 EMA for bullish bias.
    """
    result = {"signal": "neutral", "confidence": 0, "reason": "", "strategy": "ma_crossover"}

    if df is None or len(df) < 30:
        return result

    recent = df.tail(5)

    # Check for recent crossover
    prev_fast = _safe(recent["ema_9"].iloc[-3]) if len(recent) >= 3 else _safe(recent["ema_9"].iloc[0])
    prev_slow = _safe(recent["ema_21"].iloc[-3]) if len(recent) >= 3 else _safe(recent["ema_21"].iloc[0])
    curr_fast = _safe(recent["ema_9"].iloc[-1])
    curr_slow = _safe(recent["ema_21"].iloc[-1])

    price = float(recent["close"].iloc[-1])
    ema_50 = _safe(recent["ema_50"].iloc[-1])

    # Bullish crossover
    if prev_fast <= prev_slow and curr_fast > curr_slow:
        confidence = 60
        reason = "Bullish MA crossover (9 EMA crossed above 21 EMA)"

        # Bonus confidence if above 50 EMA (trend alignment)
        if price > ema_50:
            confidence += 20
            reason += " with trend confirmation (price above 50 EMA)"

        result["signal"] = "buy"
        result["confidence"] = min(100, confidence)
        result["reason"] = reason

    # Bearish crossover
    elif prev_fast >= prev_slow and curr_fast < curr_slow:
        confidence = 60
        reason = "Bearish MA crossover (9 EMA crossed below 21 EMA)"

        if price < ema_50:
            confidence += 20
            reason += " with trend confirmation (price below 50 EMA)"

        result["signal"] = "sell"
        result["confidence"] = min(100, confidence)
        result["reason"] = reason

    # Check for alignment (only if no crossover was detected)
    if result["signal"] == "neutral":
        if curr_fast > curr_slow and price > ema_50:
            # Bullish alignment
            gap_pct = ((curr_fast - curr_slow) / curr_slow) * 100
            if gap_pct > 0.5:
                result["signal"] = "buy"
                result["confidence"] = min(60, gap_pct * 20)
                result["reason"] = f"Bullish MA alignment (9 EMA {gap_pct:.1f}% above 21 EMA, above 50 EMA)"

        elif curr_fast < curr_slow and price < ema_50:
            gap_pct = ((curr_slow - curr_fast) / curr_slow) * 100
            if gap_pct > 0.5:
                result["signal"] = "sell"
                result["confidence"] = min(60, gap_pct * 20)
                result["reason"] = f"Bearish MA alignment (9 EMA {gap_pct:.1f}% below 21 EMA, below 50 EMA)"

    return result


def rsi_mean_reversion_strategy(df: pd.DataFrame) -> dict:
    """RSI Mean Reversion Strategy.

    Bullish: RSI oversold (<30) suggesting bounce.
    Bearish: RSI overbought (>70) suggesting pullback.
    Enhanced: Look for RSI turning back from extreme levels.
    """
    result = {"signal": "neutral", "confidence": 0, "reason": "", "strategy": "rsi_mean_reversion"}

    if df is None or len(df) < 20 or "rsi" not in df.columns:
        return result

    recent = df.tail(5)
    current_rsi = recent["rsi"].iloc[-1]
    prev_rsi = recent["rsi"].iloc[-2] if len(recent) >= 2 else current_rsi

    current_rsi = _safe(current_rsi, default=50.0)
    prev_rsi = _safe(prev_rsi, default=50.0)

    # Bullish: RSI turning up from oversold
    if current_rsi < TA_PARAMS["rsi_oversold"]:
        if current_rsi > prev_rsi:
            # RSI is bouncing from oversold
            confidence = min(
                100,
                70 + (TA_PARAMS["rsi_oversold"] - current_rsi) * 2,
            )
            result["signal"] = "buy"
            result["confidence"] = confidence
            result["reason"] = (
                f"Bullish RSI bounce at {current_rsi:.1f} "
                f"(turning up from oversold)"
            )
        else:
            result["signal"] = "buy"
            result["confidence"] = 50
            result["reason"] = f"RSI oversold at {current_rsi:.1f} (potential bounce)"

    # Bearish: RSI turning down from overbought
    elif current_rsi > TA_PARAMS["rsi_overbought"]:
        if current_rsi < prev_rsi:
            confidence = min(
                100,
                70 + (current_rsi - TA_PARAMS["rsi_overbought"]) * 2,
            )
            result["signal"] = "sell"
            result["confidence"] = confidence
            result["reason"] = (
                f"Bearish RSI rollover at {current_rsi:.1f} "
                f"(turning down from overbought)"
            )
        else:
            result["signal"] = "sell"
            result["confidence"] = 50
            result["reason"] = f"RSI overbought at {current_rsi:.1f} (potential pullback)"

    # Moderate signal: RSI crossing the 50 midline
    elif current_rsi > 50 and prev_rsi <= 50:
        result["signal"] = "buy"
        result["confidence"] = 40
        result["reason"] = f"RSI crossed above 50 (bullish momentum)"

    elif current_rsi < 50 and prev_rsi >= 50:
        result["signal"] = "sell"
        result["confidence"] = 40
        result["reason"] = f"RSI crossed below 50 (bearish momentum)"

    return result


def macd_divergence_strategy(df: pd.DataFrame) -> dict:
    """MACD Divergence Strategy.

    Looks for bullish/bearish divergence between price and MACD.
    Also checks MACD line crossovers relative to signal line.
    """
    result = {"signal": "neutral", "confidence": 0, "reason": "", "strategy": "macd_divergence"}

    if df is None or len(df) < 30 or "macd" not in df.columns:
        return result

    recent = df.tail(5)

    # Check for divergence
    divergence = detect_divergence(df)

    if divergence["bullish"]:
        result["signal"] = "buy"
        result["confidence"] = min(100, divergence["strength"] + 50)
        result["reason"] = f"Bullish MACD divergence detected (strength: {divergence['strength']:.0f})"

    elif divergence["bearish"]:
        result["signal"] = "sell"
        result["confidence"] = min(100, divergence["strength"] + 50)
        result["reason"] = f"Bearish MACD divergence detected (strength: {divergence['strength']:.0f})"

    # Check for MACD line crossover
    if "macd" in recent.columns and "macd_signal" in recent.columns:
        curr_macd = recent["macd"].iloc[-1]
        curr_signal = recent["macd_signal"].iloc[-1]
        prev_macd = recent["macd"].iloc[-2] if len(recent) >= 2 else curr_macd
        prev_signal = recent["macd_signal"].iloc[-2] if len(recent) >= 2 else curr_signal

        # Only report crossover if we don't already have a divergence signal
        if result["signal"] == "neutral":
            if prev_macd <= prev_signal and curr_macd > curr_signal:
                result["signal"] = "buy"
                result["confidence"] = 55
                result["reason"] = "Bullish MACD crossover (MACD line crossed above signal line)"

            elif prev_macd >= prev_signal and curr_macd < curr_signal:
                result["signal"] = "sell"
                result["confidence"] = 55
                result["reason"] = "Bearish MACD crossover (MACD line crossed below signal line)"

        # Check if MACD histogram is growing (momentum)
        if "macd_hist" in recent.columns:
            curr_hist = recent["macd_hist"].iloc[-1]
            prev_hist = recent["macd_hist"].iloc[-2] if len(recent) >= 2 else curr_hist

            if curr_hist > 0 and curr_hist > prev_hist and result["signal"] in ("neutral", "buy"):
                result["signal"] = "buy"
                result["confidence"] = max(result["confidence"], 45)
                result["reason"] = (
                    "Bullish MACD momentum "
                    + ("(divergence + histogram building)" if result["signal"] == "buy" else "")
                )

    return result


def bollinger_squeeze_strategy(df: pd.DataFrame) -> dict:
    """Bollinger Band Squeeze/Breakout Strategy.

    Bullish: Band squeeze followed by price breaking above upper band.
    Bearish: Band squeeze followed by price breaking below lower band.
    Mean reversion: Price touching extreme bands.
    """
    result = {"signal": "neutral", "confidence": 0, "reason": "", "strategy": "bollinger_squeeze"}

    if df is None or len(df) < 25 or "bb_upper" not in df.columns:
        return result

    squeeze = detect_bollinger_squeeze(df)
    recent = df.tail(3)
    close = recent["close"].iloc[-1]
    bb_upper = recent["bb_upper"].iloc[-1]
    bb_lower = recent["bb_lower"].iloc[-1]
    bb_mid = recent["bb_middle"].iloc[-1]

    # Squeeze detected - watch for breakout
    if squeeze["squeeze"]:
        result["signal"] = squeeze["direction"]
        result["confidence"] = squeeze["strength"]
        result["reason"] = (
            f"Bollinger squeeze detected (strength: {squeeze['strength']:.0f}) "
            f"- anticipating {squeeze['direction']} breakout"
        )

    # Check for breakout from squeeze
    elif close > bb_upper:
        # Check if this follows a squeeze period
        if any(df["bb_width"].tail(10) < df["bb_width"].tail(20).mean()):
            result["signal"] = "buy"
            result["confidence"] = 70
            result["reason"] = "Bullish BB breakout above upper band following squeeze"
        else:
            result["signal"] = "buy"
            result["confidence"] = 45
            result["reason"] = "Price broke above upper Bollinger Band"

    elif close < bb_lower:
        if any(df["bb_width"].tail(10) < df["bb_width"].tail(20).mean()):
            result["signal"] = "sell"
            result["confidence"] = 70
            result["reason"] = "Bearish BB breakdown below lower band following squeeze"
        else:
            result["signal"] = "sell"
            result["confidence"] = 45
            result["reason"] = "Price broke below lower Bollinger Band"

    # Mean reversion (extreme bands)
    elif close > bb_upper * 0.98:
        result["signal"] = "neutral"
        result["confidence"] = 30
        result["reason"] = "Price near upper Bollinger Band - potential resistance"

    elif close < bb_lower * 1.02:
        result["signal"] = "neutral"
        result["confidence"] = 30
        result["reason"] = "Price near lower Bollinger Band - potential support"

    return result


def volume_surge_strategy(df: pd.DataFrame) -> dict:
    """Volume Surge Strategy.

    Bullish: Price up on heavy volume (institutional buying).
    Bearish: Price down on heavy volume (institutional selling).
    Climax: Extreme volume after a long move (potential reversal).
    """
    result = {"signal": "neutral", "confidence": 0, "reason": "", "strategy": "volume_surge"}

    if df is None or len(df) < 25:
        return result

    surge = detect_volume_surge(df)

    if surge["surge"]:
        if surge["direction"] == "bullish":
            result["signal"] = "buy"
            result["confidence"] = surge["strength"]
            result["reason"] = (
                f"Bullish volume surge ({surge['strength']:.0f}% above average) "
                f"with price up - institutional accumulation"
            )
        elif surge["direction"] == "bearish":
            result["signal"] = "sell"
            result["confidence"] = surge["strength"]
            result["reason"] = (
                f"Bearish volume surge ({surge['strength']:.0f}% above average) "
                f"with price down - institutional distribution"
            )

    # Check for volume confirmation of trend
    if result["signal"] == "neutral" and "volume_ratio" in df.columns:
        recent = df.tail(3)
        avg_ratio = recent["volume_ratio"].mean()
        price_change_pct = (
            (recent["close"].iloc[-1] - recent["close"].iloc[-3])
            / recent["close"].iloc[-3]
            * 100
        )

        if avg_ratio > 1.2 and abs(price_change_pct) > 1:
            if price_change_pct > 0:
                result["signal"] = "buy"
                result["confidence"] = 35
                result["reason"] = "Above-average volume confirming bullish price action"
            else:
                result["signal"] = "sell"
                result["confidence"] = 35
                result["reason"] = "Above-average volume confirming bearish price action"

    return result


def multi_tf_confluence_strategy(
    daily_df: pd.DataFrame,
    weekly_df: pd.DataFrame = None,
    four_h_df: pd.DataFrame = None,
) -> dict:
    """Multi-Timeframe Confluence Strategy.

    Checks alignment across daily, weekly, and 4-hour timeframes.
    A high-conviction signal requires trend alignment across timeframes.
    """
    result = {"signal": "neutral", "confidence": 0, "reason": "", "strategy": "multi_tf_confluence"}

    if daily_df is None or len(daily_df) < 100:
        return result

    signals = []

    # Daily timeframe trend
    daily_recent = daily_df.tail(5)
    d_price = float(daily_recent["close"].iloc[-1])
    d_ema50 = _safe(daily_recent["ema_50"].iloc[-1]) if "ema_50" in daily_recent.columns else d_price
    d_ema200 = _safe(daily_recent["ema_200"].iloc[-1]) if "ema_200" in daily_recent.columns else d_price
    d_ema9 = _safe(daily_recent["ema_9"].iloc[-1]) if "ema_9" in daily_recent.columns else 0
    d_ema21 = _safe(daily_recent["ema_21"].iloc[-1]) if "ema_21" in daily_recent.columns else 0

    d_trend = 0
    if d_price > d_ema50:
        d_trend += 1
    if d_price > d_ema200:
        d_trend += 1
    if d_ema9 > d_ema21:
        d_trend += 1

    if d_trend >= 2:
        signals.append("bullish")
    elif d_trend <= -2:
        signals.append("bearish")
    else:
        signals.append("neutral")

    # Weekly timeframe trend
    if weekly_df is not None and len(weekly_df) >= 10:
        weekly_recent = weekly_df.tail(3)
        w_price = float(weekly_recent["close"].iloc[-1])
        w_ema20 = float(weekly_recent["close"].rolling(20).mean().iloc[-1]) if len(weekly_recent) >= 20 else float(weekly_recent["close"].mean())

        w_trend = 0
        if w_price > _safe(w_ema20):
            w_trend += 1
        if len(weekly_recent) >= 2:
            w_change = (
                (float(weekly_recent["close"].iloc[-1]) - float(weekly_recent["close"].iloc[-2]))
                / float(weekly_recent["close"].iloc[-2])
                * 100
            )
            if _safe(w_change) > 0:
                w_trend += 1
            elif _safe(w_change) < 0:
                w_trend -= 1

        if w_trend >= 1:
            signals.append("bullish")
        elif w_trend <= -1:
            signals.append("bearish")
        else:
            signals.append("neutral")
    else:
        # Infer weekly trend from recent daily price performance
        week_ago_price = daily_df["close"].iloc[-5]
        if daily_df["close"].iloc[-1] > week_ago_price:
            signals.append("bullish")
        else:
            signals.append("bearish")

    # 4-hour timeframe (entry timing)
    if four_h_df is not None and len(four_h_df) >= 10:
        four_h_recent = four_h_df.tail(5)
        f_price = float(four_h_recent["close"].iloc[-1])
        f_ema20 = float(four_h_recent["close"].rolling(20).mean().iloc[-1])

        if f_price > _safe(f_ema20):
            signals.append("bullish")
        else:
            signals.append("bearish")

    # Count signals
    bullish_count = signals.count("bullish")
    bearish_count = signals.count("bearish")

    if bullish_count >= 2 and bullish_count > bearish_count:
        result["signal"] = "buy"
        result["confidence"] = min(100, 50 + bullish_count * 17)
        result["reason"] = (
            f"Strong bullish confluence across "
            f"{bullish_count}/{len(signals)} timeframes"
        )
    elif bearish_count >= 2 and bearish_count > bullish_count:
        result["signal"] = "sell"
        result["confidence"] = min(100, 50 + bearish_count * 17)
        result["reason"] = (
            f"Strong bearish confluence across "
            f"{bearish_count}/{len(signals)} timeframes"
        )
    elif bullish_count >= 2:
        result["signal"] = "buy"
        result["confidence"] = 40
        result["reason"] = "Mild bullish confluence across timeframes"
    elif bearish_count >= 2:
        result["signal"] = "sell"
        result["confidence"] = 40
        result["reason"] = "Mild bearish confluence across timeframes"

    return result


def atr_breakout_strategy(df: pd.DataFrame) -> dict:
    """ATR Breakout Strategy.

    Look for breakouts confirmed by expanding ATR (volatility expansion).
    Combines price action with volatility to identify strong moves.
    """
    result = {"signal": "neutral", "confidence": 0, "reason": "", "strategy": "atr_breakout"}

    if df is None or len(df) < 20:
        return result

    breakout = detect_atr_breakout(df)

    if breakout["breakout"]:
        result["signal"] = breakout["direction"] if breakout["direction"] in ("buy", "sell") else "buy" if breakout["direction"] == "bullish" else "sell"
        result["confidence"] = breakout["strength"]
        result["reason"] = (
            f"{'Bullish' if breakout['direction'] == 'bullish' else 'Bearish'} "
            f"ATR breakout detected (strength: {breakout['strength']:.0f})"
        )

    # Check for support/resistance breakout using price + ATR
    if result["signal"] == "neutral" and len(df) >= 30:
        recent = df.tail(20)
        recent_high = recent["high"].max()
        recent_low = recent["low"].min()
        current_atr = recent["atr"].iloc[-1] if "atr" in recent.columns else 0
        close = recent["close"].iloc[-1]

        # 20-day high breakout
        if close > recent_high * 0.995:
            result["signal"] = "buy"
            result["confidence"] = 50
            result["reason"] = f"Price near 20-day high - potential breakout (ATR: {current_atr:.2f})"

        elif close < recent_low * 1.005:
            result["signal"] = "sell"
            result["confidence"] = 50
            result["reason"] = f"Price near 20-day low - potential breakdown (ATR: {current_atr:.2f})"

    return result


def run_all_strategies(df: pd.DataFrame, **kwargs) -> list[dict]:
    """Run all available strategies on a dataframe.

    Args:
        df: Daily OHLCV dataframe with indicators.
        **kwargs: Additional dataframes (weekly_df, four_h_df) for multi-TF analysis.

    Returns:
        List of signal dicts from each strategy.
    """
    results = []

    results.append(ma_crossover_strategy(df))
    results.append(rsi_mean_reversion_strategy(df))
    results.append(macd_divergence_strategy(df))
    results.append(bollinger_squeeze_strategy(df))
    results.append(volume_surge_strategy(df))
    results.append(atr_breakout_strategy(df))

    # Multi-timeframe requires additional data
    results.append(
        multi_tf_confluence_strategy(
            daily_df=df,
            weekly_df=kwargs.get("weekly_df"),
            four_h_df=kwargs.get("four_h_df"),
        )
    )

    return results
