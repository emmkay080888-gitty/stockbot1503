"""Settings page - configure scan limits, strategy weights, screening parameters, and TA params.

All changes are stored in session state and propagate to scans/backtests.
Overrides persist for the current browser session and reset on app restart.
For permanent changes, edit config.py directly.
"""

import streamlit as st

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config_helpers import (
    get_min_score,
    get_max_stocks,
    get_strategy_weights,
    get_ta_params,
    get_screening,
    save_strategy_weights,
    save_ta_params,
    save_screening,
    save_min_score,
    save_max_stocks,
    reset_all,
)
from utils.markets import get_market_list, get_current_market_key, set_market, get_market_config

def show():
    st.markdown("<h1 class='main-header'>⚙️ Settings</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-header'>Configure all strategy parameters, screening filters, and scan limits</p>",
        unsafe_allow_html=True,
    )

    # ─── Scan Limits ───────────────────────────────────────────────
    st.markdown("### 🔢 Scan Limits")
    st.markdown(
        "<p style='color: #00ff88; font-size: 0.85rem;'>✅ Changes apply to new scans and backtests immediately</p>",
        unsafe_allow_html=True,
    )

    curr_min_score = get_min_score()
    curr_max_stocks = get_max_stocks()

    c1, c2 = st.columns(2)
    with c1:
        min_score = st.number_input(
            "Default Min Signal Score", min_value=10, max_value=100,
            value=curr_min_score, step=5, key="settings_min_score_input",
            help="Default minimum score for scans (can be overridden per scan)",
        )
    with c2:
        max_stocks = st.number_input(
            "Default Max Stocks", min_value=10, max_value=500,
            value=curr_max_stocks, step=10, key="settings_max_stocks_input",
            help="Default maximum stocks for scans (can be overridden per scan)",
        )

    if st.button("💾 Save Scan Limits", type="primary", use_container_width=True):
        save_min_score(min_score)
        save_max_stocks(max_stocks)
        st.success(f"✅ Scan limits saved! Min score: {min_score}, Max stocks: {max_stocks}")

    st.divider()

    # ─── Strategy Weights ──────────────────────────────────────────
    st.markdown("### 🎯 Strategy Weights")
    st.markdown(
        "<p style='color: #8892b0; font-size: 0.85rem;'>"
        "Set how much each strategy influences the consensus score. "
        "Higher weight = more influence. Changes apply to new scans.</p>",
        unsafe_allow_html=True,
    )

    strategy_names = {
        "ma_crossover": "MA Crossover",
        "rsi_mean_reversion": "RSI Mean Reversion",
        "macd_divergence": "MACD Divergence",
        "bollinger_squeeze": "Bollinger Squeeze",
        "volume_surge": "Volume Surge",
        "multi_tf_confluence": "Multi-TF Confluence",
        "atr_breakout": "ATR Breakout",
    }

    current_weights = get_strategy_weights()
    updated_weights = {}

    weight_cols = st.columns(2)
    for i, (key, label) in enumerate(strategy_names.items()):
        with weight_cols[i % 2]:
            current_val = current_weights.get(key, 1.0)
            w = st.number_input(
                f"{label}",
                min_value=0.0,
                max_value=5.0,
                value=float(current_val),
                step=0.1,
                key=f"weight_{key}",
                format="%.1f",
            )
            updated_weights[key] = w

    if st.button("💾 Save Strategy Weights", type="primary", use_container_width=True):
        save_strategy_weights(updated_weights)
        st.success("✅ Strategy weights saved and will apply to new scans!")

    st.divider()

    # ─── Screening Filters ─────────────────────────────────────────
    st.markdown("### 🔍 Screening Filters")
    st.markdown(
        "<p style='color: #8892b0; font-size: 0.85rem;'>"
        "Stocks that don't pass these filters are excluded from analysis. "
        "Changes apply to new scans.</p>",
        unsafe_allow_html=True,
    )

    current_screening = get_screening()

    scr1, scr2, scr3 = st.columns(3)
    with scr1:
        min_price = st.number_input(
            "Min Price ($)",
            min_value=0.5, max_value=200.0,
            value=float(current_screening.get("min_price", 5.0)),
            step=0.5,
            key="screening_min_price",
        )
        min_volume = st.number_input(
            "Min Avg Volume",
            min_value=10000, max_value=100_000_000,
            value=int(current_screening.get("min_volume", 500_000)),
            step=10000,
            format="%d",
            key="screening_min_volume",
        )
    with scr2:
        min_mcap = st.number_input(
            "Min Market Cap ($)",
            min_value=10_000_000, max_value=100_000_000_000,
            value=current_screening.get("min_market_cap", 300_000_000),
            step=10_000_000,
            format="%d",
            key="screening_min_mcap",
        )
        min_atr = st.number_input(
            "Min ATR (%)",
            min_value=0.0, max_value=10.0,
            value=float(current_screening.get("min_atr_percent", 1.0)),
            step=0.1,
            format="%.1f",
            key="screening_min_atr",
        )
    with scr3:
        max_atr = st.number_input(
            "Max ATR (%)",
            min_value=0.5, max_value=30.0,
            value=float(current_screening.get("max_atr_percent", 15.0)),
            step=0.5,
            format="%.1f",
            key="screening_max_atr",
        )

    if st.button("💾 Save Screening Filters", type="primary", use_container_width=True):
        save_screening({
            "min_price": min_price,
            "min_volume": min_volume,
            "min_market_cap": min_mcap,
            "min_atr_percent": min_atr,
            "max_atr_percent": max_atr,
        })
        st.success("✅ Screening filters saved and will apply to new scans!")

    st.divider()

    # ─── TA Parameters ─────────────────────────────────────────────
    st.markdown("### 📐 Technical Analysis Parameters")
    st.markdown(
        "<p style='color: #8892b0; font-size: 0.85rem;'>"
        "Core indicator settings used in all analysis. "
        "Changes apply to new scans.</p>",
        unsafe_allow_html=True,
    )

    current_ta = get_ta_params()

    ta1, ta2, ta3 = st.columns(3)
    with ta1:
        ema_fast = st.number_input("EMA Fast", 3, 50, value=current_ta.get("ema_fast", 9), key="ta_ema_fast")
        ema_slow = st.number_input("EMA Slow", 5, 100, value=current_ta.get("ema_slow", 21), key="ta_ema_slow")
        ema_trend = st.number_input("EMA Trend", 20, 200, value=current_ta.get("ema_trend", 50), key="ta_ema_trend")
        ema_long = st.number_input("EMA Long Trend", 50, 400, value=current_ta.get("ema_long_trend", 200), key="ta_ema_long")
    with ta2:
        rsi_period = st.number_input("RSI Period", 5, 50, value=current_ta.get("rsi_period", 14), key="ta_rsi_period")
        rsi_oversold = st.number_input("RSI Oversold", 10, 50, value=current_ta.get("rsi_oversold", 30), key="ta_rsi_oversold")
        rsi_overbought = st.number_input("RSI Overbought", 50, 90, value=current_ta.get("rsi_overbought", 70), key="ta_rsi_overbought")
        macd_fast = st.number_input("MACD Fast", 5, 50, value=current_ta.get("macd_fast", 12), key="ta_macd_fast")
    with ta3:
        macd_slow = st.number_input("MACD Slow", 10, 100, value=current_ta.get("macd_slow", 26), key="ta_macd_slow")
        macd_signal = st.number_input("MACD Signal", 3, 20, value=current_ta.get("macd_signal", 9), key="ta_macd_signal")
        bb_period = st.number_input("BB Period", 10, 50, value=current_ta.get("bb_period", 20), key="ta_bb_period")
        bb_std = st.number_input("BB Std Dev", 1.0, 4.0, value=float(current_ta.get("bb_std", 2.0)), step=0.5, key="ta_bb_std", format="%.1f")

    ta_extra = st.columns(3)
    with ta_extra[0]:
        atr_period = st.number_input("ATR Period", 7, 30, value=current_ta.get("atr_period", 14), key="ta_atr_period")
    with ta_extra[1]:
        vol_ma_period = st.number_input("Volume MA Period", 10, 50, value=current_ta.get("volume_ma_period", 20), key="ta_vol_ma")
    with ta_extra[2]:
        vol_surge_mult = st.number_input("Volume Surge Mult", 1.0, 5.0, value=float(current_ta.get("volume_surge_multiplier", 1.5)), step=0.1, key="ta_vol_surge", format="%.1f")

    if st.button("💾 Save TA Parameters", type="primary", use_container_width=True):
        save_ta_params({
            "ema_fast": ema_fast,
            "ema_slow": ema_slow,
            "ema_trend": ema_trend,
            "ema_long_trend": ema_long,
            "rsi_period": rsi_period,
            "rsi_oversold": rsi_oversold,
            "rsi_overbought": rsi_overbought,
            "macd_fast": macd_fast,
            "macd_slow": macd_slow,
            "macd_signal": macd_signal,
            "bb_period": bb_period,
            "bb_std": bb_std,
            "atr_period": atr_period,
            "volume_ma_period": vol_ma_period,
            "volume_surge_multiplier": vol_surge_mult,
        })
        st.success("✅ TA parameters saved and will apply to new scans!")

    st.divider()

    # ─── Preferred Market ─────────────────────────────────────────
    st.markdown("### 🌍 Preferred Market")
    st.markdown(
        "<p style='color: #8892b0; font-size: 0.85rem;'>"
        "Select your default exchange/market. This affects ticker symbols, currencies, "
        "and available stock universes across the app. Changes sync with the sidebar selector.</p>",
        unsafe_allow_html=True,
    )

    market_options = get_market_list()
    current_market = get_current_market_key()
    current_cfg = get_market_config(current_market)

    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        selected_market = st.selectbox(
            "Exchange / Market",
            options=[m["key"] for m in market_options],
            format_func=lambda k: next((m["label"] for m in market_options if m["key"] == k), k),
            index=next((i for i, m in enumerate(market_options) if m["key"] == current_market), 0),
            key="settings_market_selector",
        )
    with col_m2:
        st.markdown(
            f"<div style='background: linear-gradient(135deg, rgba(124,77,255,0.1), rgba(0,200,83,0.05)); "
            f"border: 1px solid rgba(124,77,255,0.2); border-radius: 12px; padding: 12px 16px; "
            f"text-align: center; margin-top: 24px;'>"
            f"<span style='font-size: 1.5rem;'>{current_cfg['emoji']}</span><br>"
            f"<span style='color: #e0e0e0; font-size: 0.9rem;'>{current_cfg['currency']}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    if st.button("💾 Save Preferred Market", type="primary", use_container_width=True):
        set_market(selected_market)
        st.success(f"✅ Market changed to {current_cfg['emoji']} {current_cfg['name']}")
        st.rerun()

    st.divider()

    # ─── Reset All ─────────────────────────────────────────────────
    st.markdown("### 🔄 Reset All Settings")
    st.markdown(
        "<p style='color: #8892b0; font-size: 0.85rem;'>"
        "Clear all session overrides and revert to config.py defaults.</p>",
        unsafe_allow_html=True,
    )

    if st.button("⚠️ Reset All to Defaults", type="secondary", use_container_width=False):
        reset_all()
        st.success("✅ All settings reset to config.py defaults!")
        st.rerun()

    with st.expander("📄 View Active Configuration"):
        from utils.config_helpers import get_active_config
        active = get_active_config()
        st.code(f"""
# === Active Configuration ===

# Scan Limits
Min Score:       {active['min_score']}
Max Stocks:      {active['max_stocks']}

# Strategy Weights
{'\n'.join(f'{k:30s} {v:.1f}x' for k, v in sorted(active['strategy_weights'].items()))}

# Screening Filters
Min Price:       ${active['screening']['min_price']:.1f}
Min Volume:      {active['screening']['min_volume']:,}
Min Market Cap:  ${active['screening']['min_market_cap']:,}
Min ATR:         {active['screening']['min_atr_percent']:.1f}%
Max ATR:         {active['screening']['max_atr_percent']:.1f}%

# TA Parameters
EMA Fast/Slow:   {active['ta_params']['ema_fast']}/{active['ta_params']['ema_slow']}
EMA Trend/Long:  {active['ta_params']['ema_trend']}/{active['ta_params']['ema_long_trend']}
RSI Per/Ov/Ov:   {active['ta_params']['rsi_period']}/{active['ta_params']['rsi_oversold']}/{active['ta_params']['rsi_overbought']}
MACD F/S/Sig:    {active['ta_params']['macd_fast']}/{active['ta_params']['macd_slow']}/{active['ta_params']['macd_signal']}
BB Per/Std:      {active['ta_params']['bb_period']}/{active['ta_params']['bb_std']}
ATR Period:      {active['ta_params']['atr_period']}
Vol MA Period:   {active['ta_params']['volume_ma_period']}
Vol Surge Mult:  {active['ta_params']['volume_surge_multiplier']}
        """)
