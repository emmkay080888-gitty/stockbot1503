"""Stock screening and filtering module."""

import logging
from typing import Optional
import pandas as pd
from config import SCREENING
from data.fetcher import fetch_fundamentals

logger = logging.getLogger(__name__)


def screen_by_liquidity(df: pd.DataFrame, info: Optional[dict] = None) -> tuple[bool, str]:
    """Screen a stock for basic liquidity requirements.

    Checks: minimum price, minimum volume, minimum market cap.
    """
    if df is None or len(df) < 20:
        return False, "Insufficient price data"

    close = df["close"].iloc[-1]
    avg_volume = df["volume"].tail(20).mean()

    # Price filter
    if close < SCREENING["min_price"]:
        return False, f"Price ${close:.2f} below minimum ${SCREENING['min_price']}"

    # Volume filter
    if avg_volume < SCREENING["min_volume"]:
        vol_str = f"{avg_volume:,.0f}"
        min_str = f"{SCREENING['min_volume']:,}"
        return False, f"Avg volume {vol_str} below minimum {min_str}"

    # Market cap filter
    if info and info.get("market_cap"):
        mc = info["market_cap"]
        if mc < SCREENING["min_market_cap"]:
            mc_str = f"${mc:,.0f}"
            min_str = f"${SCREENING['min_market_cap']:,}"
            return False, f"Market cap {mc_str} below {min_str}"

    return True, "Passes screening"


def screen_by_volatility(df: pd.DataFrame) -> tuple[bool, str]:
    """Screen for appropriate volatility (not too low, not too high).

    Uses ATR as percentage of price.
    """
    if df is None or len(df) < 20:
        return False, "Insufficient data"

    atr_col = "atr_percent" if "atr_percent" in df.columns else None
    if atr_col is None:
        return True, "No ATR data available"

    current_atr = df[atr_col].iloc[-1]
    avg_atr = df[atr_col].tail(20).mean()

    if avg_atr < SCREENING["min_atr_percent"]:
        return False, f"ATR {avg_atr:.1f}% too low for swing trading"

    if avg_atr > SCREENING["max_atr_percent"]:
        return False, f"ATR {avg_atr:.1f}% too high (excessive volatility)"

    return True, f"ATR {avg_atr:.1f}% within acceptable range"


def calculate_target_price(df: pd.DataFrame, signal_type: str) -> dict:
    """Calculate target price and stop loss based on volatility.

    Uses ATR-based targets: 2x ATR for target, 1x ATR for stop.
    Also considers recent support/resistance levels.
    """
    result = {"target": None, "stop_loss": None, "risk_reward": 0}

    if df is None or len(df) < 20:
        return result

    close = df["close"].iloc[-1]
    atr = df["atr"].iloc[-1] if "atr" in df.columns else close * 0.03

    # Find recent support/resistance
    recent_20 = df.tail(20)
    recent_high = recent_20["high"].max()
    recent_low = recent_20["low"].min()

    if signal_type == "buy":
        # Target: 2-3x ATR above entry
        target = close + (atr * 2.5)
        # Also consider recent resistance
        if target > recent_high:
            target = max(target, recent_high + atr)

        stop_loss = close - (atr * 1.5)
        # Don't stop below recent support
        stop_loss = max(stop_loss, recent_low - (atr * 0.5))

        risk = close - stop_loss
        reward = target - close
        risk_reward = reward / risk if risk > 0 else 0

        result["target"] = round(target, 2)
        result["stop_loss"] = round(stop_loss, 2)
        result["risk_reward"] = round(risk_reward, 2)

    elif signal_type == "sell":
        target = close - (atr * 2.5)
        if target < recent_low:
            target = min(target, recent_low - atr)

        stop_loss = close + (atr * 1.5)
        stop_loss = min(stop_loss, recent_high + (atr * 0.5))

        risk = stop_loss - close
        reward = close - target
        risk_reward = reward / risk if risk > 0 else 0

        result["target"] = round(target, 2)
        result["stop_loss"] = round(stop_loss, 2)
        result["risk_reward"] = round(risk_reward, 2)

    return result


def estimate_potential_return(target_price: float, current_price: float) -> float:
    """Estimate potential return percentage."""
    if current_price <= 0:
        return 0
    return round(((target_price - current_price) / current_price) * 100, 2)


def screen_stock(
    ticker: str, df: pd.DataFrame, info: Optional[dict] = None
) -> Optional[dict]:
    """Run all screening checks on a stock.

    Returns dict with pass/fail results, or None if critical data missing.
    """
    liquidity_pass, liquidity_msg = screen_by_liquidity(df, info)
    if not liquidity_pass:
        logger.debug(f"{ticker}: {liquidity_msg}")
        return None

    vol_pass, vol_msg = screen_by_volatility(df)
    if not vol_pass:
        logger.debug(f"{ticker}: {vol_msg}")
        return None

    return {
        "ticker": ticker,
        "price": round(df["close"].iloc[-1], 2),
        "screening": {
            "passed": True,
            "liquidity": liquidity_msg,
            "volatility": vol_msg,
        },
    }
