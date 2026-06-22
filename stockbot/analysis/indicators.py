"""Technical indicator calculations using pandas-ta."""

import pandas as pd
import pandas_ta as ta
import numpy as np
from config import TA_PARAMS


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add all technical indicators to the dataframe.

    Adds: EMA (fast, slow, trend), RSI, MACD, Bollinger Bands, ATR, Volume MA.
    """
    if df is None or len(df) < 50:
        return df

    df = df.copy()

    # Exponential Moving Averages
    df["ema_9"] = ta.ema(df["close"], length=TA_PARAMS["ema_fast"])
    df["ema_21"] = ta.ema(df["close"], length=TA_PARAMS["ema_slow"])
    df["ema_50"] = ta.ema(df["close"], length=TA_PARAMS["ema_trend"])
    df["ema_200"] = ta.ema(df["close"], length=TA_PARAMS["ema_long_trend"])

    # RSI
    df["rsi"] = ta.rsi(df["close"], length=TA_PARAMS["rsi_period"])

    # MACD
    macd = ta.macd(
        df["close"],
        fast=TA_PARAMS["macd_fast"],
        slow=TA_PARAMS["macd_slow"],
        signal=TA_PARAMS["macd_signal"],
    )
    if macd is not None:
        df["macd"] = macd.iloc[:, 0]
        df["macd_signal"] = macd.iloc[:, 1]
        df["macd_hist"] = macd.iloc[:, 2]

    # Bollinger Bands
    bb = ta.bbands(
        df["close"],
        length=TA_PARAMS["bb_period"],
        std=TA_PARAMS["bb_std"],
    )
    if bb is not None:
        # pandas_ta.bbands returns columns: BBL (lower), BBM (middle), BBU (upper), BBB (bandwidth), BBP (percent)
        df["bb_upper"] = bb.iloc[:, 2]  # BBU
        df["bb_middle"] = bb.iloc[:, 1]  # BBM
        df["bb_lower"] = bb.iloc[:, 0]  # BBL
        df["bb_width"] = (bb.iloc[:, 2] - bb.iloc[:, 0]) / bb.iloc[:, 1]
        df["bb_percent"] = (df["close"] - bb.iloc[:, 0]) / (bb.iloc[:, 2] - bb.iloc[:, 0])

    # ATR (Average True Range)
    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=TA_PARAMS["atr_period"])
    df["atr_percent"] = (df["atr"] / df["close"]) * 100

    # Volume Indicators
    df["volume_ma"] = df["volume"].rolling(window=TA_PARAMS["volume_ma_period"]).mean()
    df["volume_ratio"] = df["volume"] / df["volume_ma"]
    df["obv"] = ta.obv(df["close"], df["volume"])

    # Price position relative to MAs
    df["pct_from_ema9"] = ((df["close"] - df["ema_9"]) / df["ema_9"]) * 100
    df["pct_from_ema21"] = ((df["close"] - df["ema_21"]) / df["ema_21"]) * 100
    df["pct_from_ema50"] = ((df["close"] - df["ema_50"]) / df["ema_50"]) * 100

    return df


def detect_divergence(
    df: pd.DataFrame, lookback: int = 20
) -> dict:
    """Detect bullish/bearish MACD divergence.

    Bullish divergence: price makes lower low, MACD makes higher low.
    Bearish divergence: price makes higher high, MACD makes lower high.
    """
    result = {"bullish": False, "bearish": False, "strength": 0}

    if df is None or len(df) < lookback + 5:
        return result

    recent = df.tail(lookback)
    if "macd" not in recent.columns:
        return result

    # Find local minima and maxima
    price_lows = (
        (recent["close"].shift(1) > recent["close"])
        & (recent["close"] < recent["close"].shift(-1))
    )
    price_highs = (
        (recent["close"].shift(1) < recent["close"])
        & (recent["close"] > recent["close"].shift(-1))
    )

    macd_lows = (
        (recent["macd"].shift(1) > recent["macd"])
        & (recent["macd"] < recent["macd"].shift(-1))
    )
    macd_highs = (
        (recent["macd"].shift(1) < recent["macd"])
        & (recent["macd"] > recent["macd"].shift(-1))
    )

    # Check for bullish divergence
    price_low_idx = recent.index[price_lows][-2:] if price_lows.any() else []
    macd_low_idx = recent.index[macd_lows][-2:] if macd_lows.any() else []

    if len(price_low_idx) >= 2 and len(macd_low_idx) >= 1:
        p_low1 = recent.loc[price_low_idx[0], "close"]
        p_low2 = recent.loc[price_low_idx[-1], "close"]

        if p_low2 < p_low1:  # Price made lower low
            # Check if MACD made higher low
            for midx in macd_low_idx:
                if midx > price_low_idx[0] and midx <= price_low_idx[-1]:
                    m_val1 = recent.loc[price_low_idx[0], "macd"]
                    m_val2 = recent.loc[midx, "macd"]
                    if m_val2 > m_val1:
                        result["bullish"] = True
                        result["strength"] = min(
                            100, abs((p_low2 - p_low1) / p_low1 * 200)
                        )
                        break

    # Check for bearish divergence
    price_high_idx = recent.index[price_highs][-2:] if price_highs.any() else []
    macd_high_idx = recent.index[macd_highs][-2:] if macd_highs.any() else []

    if len(price_high_idx) >= 2 and len(macd_high_idx) >= 1:
        p_high1 = recent.loc[price_high_idx[0], "close"]
        p_high2 = recent.loc[price_high_idx[-1], "close"]

        if p_high2 > p_high1:  # Price made higher high
            for midx in macd_high_idx:
                if midx > price_high_idx[0] and midx <= price_high_idx[-1]:
                    m_val1 = recent.loc[price_high_idx[0], "macd"]
                    m_val2 = recent.loc[midx, "macd"]
                    if m_val2 < m_val1:
                        result["bearish"] = True
                        result["strength"] = min(
                            100, abs((p_high2 - p_high1) / p_high1 * 200)
                        )
                        break

    return result


def detect_bollinger_squeeze(df: pd.DataFrame, lookback: int = 20) -> dict:
    """Detect Bollinger Band squeezes (low volatility setups)."""
    result = {"squeeze": False, "direction": "neutral", "strength": 0}

    if df is None or len(df) < lookback + 5 or "bb_width" not in df.columns:
        return result

    recent = df.tail(lookback)
    current_width = recent["bb_width"].iloc[-1]
    avg_width = recent["bb_width"].iloc[:-1].mean()
    width_ratio = current_width / avg_width if avg_width > 0 else 1

    # Squeeze detected when bandwidth is below average
    if width_ratio < 0.85:
        result["squeeze"] = True
        result["strength"] = max(0, min(100, (1 - width_ratio) * 100))

        # Determine direction from recent price action
        last_3 = recent.tail(3)
        if last_3["close"].iloc[-1] > last_3["bb_middle"].iloc[-1]:
            result["direction"] = "bullish"
        else:
            result["direction"] = "bearish"

    return result


def detect_volume_surge(df: pd.DataFrame) -> dict:
    """Detect abnormal volume surges with price confirmation."""
    result = {"surge": False, "direction": "neutral", "strength": 0}

    if df is None or len(df) < 25 or "volume_ratio" not in df.columns:
        return result

    recent = df.tail(5)
    latest_ratio = recent["volume_ratio"].iloc[-1]
    avg_ratio = recent["volume_ratio"].iloc[:-1].mean()

    if latest_ratio >= 1.5 and latest_ratio >= avg_ratio:
        result["surge"] = True
        result["strength"] = min(100, (latest_ratio - 1) * 50)

        # Direction from price
        price_change = recent["close"].iloc[-1] - recent["close"].iloc[-2]
        if price_change > 0:
            result["direction"] = "bullish"
        elif price_change < 0:
            result["direction"] = "bearish"

    return result


def detect_atr_breakout(df: pd.DataFrame) -> dict:
    """Detect breakouts confirmed by ATR expansion."""
    result = {"breakout": False, "direction": "neutral", "strength": 0}

    if df is None or len(df) < 20 or "atr" not in df.columns:
        return result

    recent = df.tail(10)
    current_atr_pct = recent["atr_percent"].iloc[-1]
    avg_atr_pct = recent["atr_percent"].iloc[:-5].mean() if len(recent) > 5 else recent["atr_percent"].mean()

    if current_atr_pct > avg_atr_pct * 1.3:
        result["breakout"] = True
        result["strength"] = min(100, (current_atr_pct / avg_atr_pct - 1) * 50)

        # Price direction
        price_change_5d = (
            (recent["close"].iloc[-1] - recent["close"].iloc[-5])
            / recent["close"].iloc[-5]
            * 100
        )
        if price_change_5d > 2:
            result["direction"] = "bullish"
        elif price_change_5d < -2:
            result["direction"] = "bearish"

    return result
