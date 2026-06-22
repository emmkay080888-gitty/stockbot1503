"""Magic Call — Upload a chart screenshot, get CALL/PUT signals with entry/exit/stop-loss/profit.

The user uploads a candlestick chart screenshot (visual reference), enters the ticker symbol,
timeframe, and expected profit target. The bot runs all 7 strategies + options chain analysis
on the ticker and outputs a full trade plan with multi-timeframe opportunities.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import io
import math
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.markets import get_current_market_key, get_market_config, get_currency, apply_suffix
from data.fetcher import fetch_historical, fetch_multiple_timeframes, fetch_fundamentals, fetch_options_chain
from analysis.indicators import add_all_indicators
from analysis.strategies import run_all_strategies

from analysis.screener import screen_stock, calculate_target_price, estimate_potential_return
from config import STRATEGY_WEIGHTS

# ── Page-specific CSS ──────────────────────────────────────────────
_PAGE_CSS = """
<style>
.magic-hero {
    background: linear-gradient(135deg, #1a0a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(255, 215, 0, 0.3);
    border-radius: 20px;
    padding: 30px;
    margin: 10px 0 20px 0;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.magic-hero-glow {
    position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle at center, rgba(255,215,0,0.1) 0%, transparent 60%);
    animation: magicGlow 4s ease-in-out infinite;
}
@keyframes magicGlow {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(-20px, 20px); }
}
.magic-content { position: relative; z-index: 1; }
.magic-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,152,0,0.1));
    border: 1px solid rgba(255,215,0,0.4);
    border-radius: 20px;
    padding: 4px 16px; font-size: 0.7rem; color: #ffd700;
    letter-spacing: 2px; margin-bottom: 12px;
    animation: pulseMagic 2s ease-in-out infinite;
}
@keyframes pulseMagic { 0%,100%{opacity:1} 50%{opacity:0.6} }
.magic-title {
    font-size: 2.5rem !important; font-weight: 800 !important; margin-bottom: 10px !important;
    background: linear-gradient(135deg, #ffd700, #ff9100) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
}
.magic-subtitle { color: #b0bec5; font-size: 1rem; margin-bottom: 16px; }

.signal-card-call {
    background: linear-gradient(135deg, rgba(0,200,83,0.12), rgba(0,200,83,0.05));
    border: 1px solid rgba(0,200,83,0.4);
    border-radius: 16px; padding: 24px;
    text-align: center;
}
.signal-card-put {
    background: linear-gradient(135deg, rgba(255,23,68,0.12), rgba(255,23,68,0.05));
    border: 1px solid rgba(255,23,68,0.4);
    border-radius: 16px; padding: 24px;
    text-align: center;
}
.signal-badge-call {
    display: inline-block;
    background: linear-gradient(135deg, rgba(0,200,83,0.3), rgba(0,200,83,0.1));
    border: 1px solid rgba(0,200,83,0.5);
    border-radius: 20px; padding: 6px 24px;
    font-size: 1.4rem; font-weight: 800; color: #00c853;
    letter-spacing: 3px;
}
.signal-badge-put {
    display: inline-block;
    background: linear-gradient(135deg, rgba(255,23,68,0.3), rgba(255,23,68,0.1));
    border: 1px solid rgba(255,23,68,0.5);
    border-radius: 20px; padding: 6px 24px;
    font-size: 1.4rem; font-weight: 800; color: #ff1744;
    letter-spacing: 3px;
}
.signal-price { font-size: 2rem; font-weight: 700; color: #e0e0e0; margin: 8px 0; }
.signal-detail { color: #b0bec5; font-size: 0.9rem; }

.tf-card {
    background: linear-gradient(135deg, rgba(124,77,255,0.08), rgba(0,200,83,0.05));
    border: 1px solid rgba(124,77,255,0.2);
    border-radius: 12px; padding: 16px;
    height: 100%; transition: all 0.3s ease;
}
.tf-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(124,77,255,0.15);
    border-color: #7c4dff;
}
.tf-label { font-size: 0.75rem; color: #78909c; text-transform: uppercase; letter-spacing: 1px; }
.tf-direction { font-size: 1.1rem; font-weight: 700; }
.tf-profit { font-size: 0.95rem; }
.tf-confidence { font-size: 0.8rem; color: #8892b0; }

.upload-hint {
    color: #78909c; font-size: 0.8rem; text-align: center;
    margin-top: 8px; font-style: italic;
}
.profit-meter {
    background: linear-gradient(90deg, #ff1744, #ffd700, #00c853);
    height: 8px; border-radius: 4px; margin: 8px 0;
}
</style>
"""

# ── Strategy Name Mapping ──────────────────────────────────────────
STRATEGY_LABELS = {
    "ma_crossover": "MA Crossover",
    "rsi_mean_reversion": "RSI Mean Reversion",
    "macd_divergence": "MACD Divergence",
    "bollinger_squeeze": "Bollinger Squeeze",
    "volume_surge": "Volume Surge",
    "multi_tf_confluence": "Multi-TF Confluence",
    "atr_breakout": "ATR Breakout",
}

TIMEFRAME_OPTIONS = {
    "15 min": ("5d", "15m"),
    "30 min": ("5d", "30m"),
    "1 hour": ("1mo", "60m"),
    "4 hours": ("3mo", "60m"),
    "Daily": ("1y", "1d"),
    "Weekly": ("2y", "1wk"),
    "Monthly": ("5y", "1mo"),
}

ADDITIONAL_TF = [
    ("15 min", "5d", "15m", 0.005),
    ("1 hour", "1mo", "60m", 0.01),
    ("4 hours", "3mo", "60m", 0.015),
    ("Daily", "1y", "1d", 0.02),
    ("Weekly", "2y", "1wk", 0.03),
]


def _safe(val, default=0.0):
    """Return a safe numeric value, replacing NaN/None with default."""
    if val is None:
        return default
    if hasattr(val, 'item'):
        val = val.item()
    try:
        if math.isnan(val):
            return default
    except (TypeError, ValueError):
        return default
    return val


def analyze_timeframe(ticker: str, period: str, interval: str, atr_mult: float = 0.02) -> dict | None:
    """Run analysis on a specific timeframe and return signal + targets."""
    df = fetch_historical(ticker, period=period, interval=interval)
    if df is None or len(df) < 30:
        return None

    df = add_all_indicators(df)
    if df is None or len(df) < 30:
        return None

    signals = run_all_strategies(df)
    active = [s for s in signals if s["signal"] != "neutral" and s["confidence"] > 0]

    if not active:
        return {"signal": "neutral", "confidence": 0, "strategies": 0}

    # Weighted consensus
    buy_w = sum(s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active if s["signal"] == "buy")
    sell_w = sum(s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active if s["signal"] == "sell")
    total_w = sum(STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active)

    if total_w == 0:
        return {"signal": "neutral", "confidence": 0, "strategies": 0}

    if buy_w > sell_w:
        direction = "buy"
        confidence = min(100, int((buy_w / total_w) * 100))
    elif sell_w > buy_w:
        direction = "sell"
        confidence = min(100, int((sell_w / total_w) * 100))
    else:
        return {"signal": "neutral", "confidence": 0, "strategies": 0}

    price = float(df["close"].iloc[-1])
    targets = calculate_target_price(df, direction)
    potential = estimate_potential_return(targets["target"], price) if targets["target"] else 0

    return {
        "signal": direction,
        "confidence": confidence,
        "price": round(price, 2),
        "target": _safe(targets["target"]),
        "stop_loss": _safe(targets["stop_loss"]),
        "risk_reward": _safe(targets["risk_reward"]),
        "potential_return": potential,
        "strategies": len(active),
        "strategy_detail": active,
    }


def plot_magic_chart(df: pd.DataFrame, ticker: str, signal_type: str, entry: float, target: float, stop: float, currency: str):
    """Create an annotated chart with entry, target, and stop lines."""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
    )

    # Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["open"], high=df["high"],
            low=df["low"], close=df["close"], name=ticker,
            increasing_line_color="#00c853", decreasing_line_color="#ff1744",
        ),
        row=1, col=1,
    )

    # EMAs
    for ema, color, name in [("ema_9", "#00bfff", "EMA 9"), ("ema_21", "#ffd700", "EMA 21"), ("ema_50", "#ff6b35", "EMA 50")]:
        if ema in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[ema], name=name,
                           line=dict(color=color, width=1), opacity=0.6),
                row=1, col=1,
            )

    # Entry / Target / Stop lines
    line_color = "#00c853" if signal_type == "buy" else "#ff1744"
    label = "CALL" if signal_type == "buy" else "PUT"

    fig.add_hline(y=entry, line_dash="solid", line_color=line_color, opacity=0.8,
                  annotation_text=f"Entry {currency}{entry:.2f}", row=1, col=1)
    if target:
        fig.add_hline(y=target, line_dash="dash", line_color="#00c853", opacity=0.7,
                      annotation_text=f"Target {currency}{target:.2f}", row=1, col=1)
    if stop:
        fig.add_hline(y=stop, line_dash="dash", line_color="#ff1744", opacity=0.7,
                      annotation_text=f"Stop {currency}{stop:.2f}", row=1, col=1)

    # Volume
    colors = ["#ff1744" if row["close"] < row["open"] else "#00c853" for _, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df["volume"], name="Volume",
               marker_color=colors, opacity=0.5),
        row=2, col=1,
    )

    fig.update_layout(
        template="plotly_dark", height=500,
        showlegend=True, legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10, color="#e0e0e0")),
        margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text=f"Price ({currency})", row=1, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Volume", row=2, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.05)")

    return fig


def show():
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    market_key = get_current_market_key()
    mkt_cfg = get_market_config(market_key)
    currency = mkt_cfg["currency"]
    suffix = mkt_cfg["suffix"]

    # ── Hero ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="magic-hero">
        <div class="magic-hero-glow"></div>
        <div class="magic-content">
            <div class="magic-badge">✨ LIVE AI ANALYSIS</div>
            <h1 class="magic-title">🔮 Magic Call</h1>
            <p class="magic-subtitle">
                Upload a chart screenshot, set your targets — and let the bot decode the perfect
                CALL/PUT with entry, exit, stop-loss, and profit projections across all timeframes
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input Section ─────────────────────────────────────────────
    col_inp1, col_inp2 = st.columns([1, 1])

    with col_inp1:
        st.markdown("### 📤 Upload Chart")
        uploaded_file = st.file_uploader(
            "Upload a candlestick chart screenshot",
            type=["png", "jpg", "jpeg", "webp"],
            key="magic_chart_upload",
            help="Upload any candlestick chart screenshot. The bot will use the ticker symbol you enter below for analysis.",
        )

        if uploaded_file:
            st.image(uploaded_file, caption="📊 Uploaded Chart", use_container_width=True)
            st.markdown("<p class='upload-hint'>✅ Chart received! Enter the ticker below for analysis.</p>", unsafe_allow_html=True)

    with col_inp2:
        st.markdown("### 🎯 Trade Parameters")

        ticker = st.text_input(
            "Ticker Symbol",
            value=st.session_state.get("magic_ticker", ""),
            placeholder="e.g. AAPL, RELIANCE, TSLA",
            key="magic_ticker_input",
            help="Enter the stock ticker from your chart",
        ).strip().upper()

        # Apply market suffix if needed
        ticker_full = apply_suffix(ticker, market_key) if ticker else ticker

        timeframe = st.selectbox(
            "Trading Timeframe",
            options=list(TIMEFRAME_OPTIONS.keys()),
            index=4,  # Default: Daily
            key="magic_tf",
            help="Select the timeframe you want to trade on",
        )

        expected_profit = st.slider(
            "Expected Profit Target (%)",
            min_value=1.0, max_value=50.0, value=10.0, step=0.5,
            key="magic_profit",
            help="What percentage profit are you expecting?",
            format="%.1f%%",
        )

        risk_per_trade = st.slider(
            "Max Risk Per Trade (%)",
            min_value=1.0, max_value=20.0, value=5.0, step=0.5,
            key="magic_risk",
            help="Maximum loss you're willing to take",
            format="%.1f%%",
        )

        analyze_btn = st.button("🔮 Analyze & Predict", type="primary", use_container_width=True)

    st.divider()

    # ── Analysis ──────────────────────────────────────────────────
    if analyze_btn and ticker:
        if not uploaded_file:
            st.info("💡 Tip: Upload a chart screenshot for visual reference. Analysis will still run without it.")

        with st.spinner(f"🔮 Analyzing {ticker} across all strategies and timeframes..."):
            try:
                tf_period, tf_interval = TIMEFRAME_OPTIONS[timeframe]
            except KeyError:
                tf_period, tf_interval = "1y", "1d"

            start_time = time.time()

            # 1. Fetch primary timeframe data
            df = fetch_historical(ticker_full, period=tf_period, interval=tf_interval)
            if df is None or len(df) < 20:
                # Try without suffix
                df = fetch_historical(ticker, period=tf_period, interval=tf_interval)

            if df is None or len(df) < 20:
                st.error(f"❌ Could not fetch data for {ticker}. Check the ticker symbol and try again.")
                st.stop()

            # 2. Stock Qualification Test ("simple test")
            st.markdown("### ✅ Stock Qualification Test")
            info = fetch_fundamentals(ticker_full) or fetch_fundamentals(ticker)
            screen_result = screen_stock(ticker_full or ticker, df, info)

            test_col1, test_col2, test_col3 = st.columns(3)
            if screen_result:
                with test_col1:
                    st.markdown(f"""
                    <div style="background: #0a2e1a; border: 1px solid #00c85344; border-radius: 12px; padding: 16px; text-align: center;">
                        <div style="color:#00c853; font-size:1.5rem;">✅ PASS</div>
                        <div style="color:#b0bec5; font-size:0.8rem;">Liquidity Check</div>
                        <div style="color:#78909c; font-size:0.7rem;">{screen_result['screening'].get('liquidity', 'OK')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with test_col2:
                    st.markdown(f"""
                    <div style="background: #0a2e1a; border: 1px solid #00c85344; border-radius: 12px; padding: 16px; text-align: center;">
                        <div style="color:#00c853; font-size:1.5rem;">✅ PASS</div>
                        <div style="color:#b0bec5; font-size:0.8rem;">Volatility Check</div>
                        <div style="color:#78909c; font-size:0.7rem;">{screen_result['screening'].get('volatility', 'OK')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with test_col3:
                    st.markdown(f"""
                    <div style="background: #0a2e1a; border: 1px solid #00c85344; border-radius: 12px; padding: 16px; text-align: center;">
                        <div style="color:#00c853; font-size:1.5rem;">✅ SCREENED</div>
                        <div style="color:#b0bec5; font-size:0.8rem;">Fundamentals</div>
                        <div style="color:#78909c; font-size:0.7rem;">Market cap: {info.get('sector', 'N/A') if info else 'N/A'}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ {ticker} did not pass the stock qualification test. Proceeding with analysis anyway (results may be less reliable).")

            st.divider()

            # 3. Run full analysis
            df_indicators = add_all_indicators(df.copy())
            if df_indicators is not None and len(df_indicators) >= 30:
                strategies_result = run_all_strategies(df_indicators)
            else:
                strategies_result = run_all_strategies(df)

            # 3. Weighted consensus
            active_strategies = [s for s in strategies_result if s["signal"] != "neutral" and s["confidence"] > 0]
            buy_weighted = sum(s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active_strategies if s["signal"] == "buy")
            sell_weighted = sum(s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active_strategies if s["signal"] == "sell")
            total_weight = sum(STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active_strategies)

            if total_weight == 0:
                st.warning("⚠️ All strategies returned neutral signals. Try a different ticker or timeframe.")
                st.stop()

            if buy_weighted > sell_weighted:
                signal_type = "buy"
                confidence = min(100, int((buy_weighted / total_weight) * 100))
                call_put = "CALL"
            elif sell_weighted > buy_weighted:
                signal_type = "sell"
                confidence = min(100, int((sell_weighted / total_weight) * 100))
                call_put = "PUT"
            else:
                st.warning("⚠️ Buy and sell signals are evenly matched. No clear direction.")
                st.stop()

            # 4. Calculate entry/target/stop
            current_price = float(df["close"].iloc[-1])
            targets = calculate_target_price(df_indicators if df_indicators is not None else df, signal_type)
            entry_price = current_price
            target_price = targets.get("target", entry_price * (1 + expected_profit / 100 * (1 if signal_type == "buy" else -1)))
            stop_price = targets.get("stop_loss", entry_price * (1 - risk_per_trade / 100 * (1 if signal_type == "buy" else -1)))
            risk_reward = targets.get("risk_reward", 0)

            # Override target with user's expected profit if it's more conservative
            user_target = entry_price * (1 + expected_profit / 100) if signal_type == "buy" else entry_price * (1 - expected_profit / 100)
            if target_price is not None:
                if signal_type == "buy" and user_target < target_price:
                    target_price = user_target
                elif signal_type == "sell" and user_target > target_price:
                    target_price = user_target
            else:
                target_price = user_target

            # Apply user risk
            user_stop = entry_price * (1 - risk_per_trade / 100) if signal_type == "buy" else entry_price * (1 + risk_per_trade / 100)
            stop_price = user_stop

            # Recalculate R/R
            if signal_type == "buy":
                risk_amount = entry_price - stop_price
                reward_amount = target_price - entry_price
            else:
                risk_amount = stop_price - entry_price
                reward_amount = entry_price - target_price
            risk_reward = round(reward_amount / risk_amount, 2) if risk_amount > 0 else 0

            actual_profit = estimate_potential_return(target_price, entry_price)

            analysis_time = time.time() - start_time

        # ── RESULTS ───────────────────────────────────────────────
        st.markdown("## 📊 Analysis Results")
        st.caption(f"Analyzed in {analysis_time:.1f}s • {len(active_strategies)} active strategies • {timeframe} timeframe")

        # Main signal card
        sig_col1, sig_col2 = st.columns([1, 1])

        with sig_col1:
            card_class = "signal-card-call" if call_put == "CALL" else "signal-card-put"
            badge_class = "signal-badge-call" if call_put == "CALL" else "signal-badge-put"

            st.markdown(f"""
            <div class="{card_class}">
                <div class="{badge_class}">{call_put} SIGNAL</div>
                <div class="signal-price">{currency}{entry_price:.2f}</div>
                <div class="signal-detail">Current Price</div>
                <div style="margin-top: 12px;">
                    <span style="color:#e0e0e0; font-size:0.9rem;">Confidence: </span>
                    <span style="color: {'#00c853' if confidence >= 65 else '#ffd700' if confidence >= 40 else '#ff1744'};
                              font-size:1.4rem; font-weight:700;">{confidence}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        with sig_col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                        border: 1px solid rgba(124,77,255,0.3); border-radius: 16px; padding: 24px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div>
                        <div style="color:#78909c; font-size:0.75rem;">ENTRY</div>
                        <div style="color:#e0e0e0; font-size:1.3rem; font-weight:700;">{currency}{entry_price:.2f}</div>
                    </div>
                    <div>
                        <div style="color:#78909c; font-size:0.75rem;">TARGET</div>
                        <div style="color:#00c853; font-size:1.3rem; font-weight:700;">{currency}{target_price:.2f}</div>
                    </div>
                    <div>
                        <div style="color:#78909c; font-size:0.75rem;">STOP LOSS</div>
                        <div style="color:#ff1744; font-size:1.3rem; font-weight:700;">{currency}{stop_price:.2f}</div>
                    </div>
                    <div>
                        <div style="color:#78909c; font-size:0.75rem;">R/R RATIO</div>
                        <div style="color:#ffd700; font-size:1.3rem; font-weight:700;">{risk_reward}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Profit projection meter
        profit_color = "#00c853" if actual_profit > 0 else "#ff1744"
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                    border: 1px solid rgba(124,77,255,0.2); border-radius: 12px; padding: 20px; margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color:#78909c; font-size:0.8rem;">EXPECTED PROFIT</span>
                    <div style="font-size:1.8rem; font-weight:700; color:{profit_color};">
                        {actual_profit:+.1f}%
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="color:#78909c; font-size:0.8rem;">TIME HORIZON</span>
                    <div style="font-size:1.1rem; color:#e0e0e0; font-weight:600;">
                        {timeframe}
                    </div>
                </div>
                <div style="text-align:right;">
                    <span style="color:#78909c; font-size:0.8rem;">POSITION TYPE</span>
                    <div style="font-size:1.1rem; color:{'#00c853' if call_put == 'CALL' else '#ff1744'}; font-weight:700;">
                        {call_put}
                    </div>
                </div>
            </div>
            <div class="profit-meter" style="width: {min(100, abs(actual_profit) * 5)}%;"></div>
        </div>
        """, unsafe_allow_html=True)

        # Price chart with annotations
        st.markdown("### 📈 Price Chart — Annotated")
        chart = plot_magic_chart(df, ticker, signal_type, entry_price, target_price, stop_price, currency)
        st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

        # Strategy breakdown
        st.markdown("### 🧩 Strategy Breakdown")
        strat_cols = st.columns(min(len(active_strategies), 4))
        for i, s in enumerate(active_strategies):
            with strat_cols[i % 4]:
                color = "#00c853" if s["signal"] == "buy" else "#ff1744" if s["signal"] == "sell" else "#888"
                name = STRATEGY_LABELS.get(s["strategy"], s["strategy"].replace("_", " ").title())
                st.markdown(f"""
                <div class="tf-card" style="border-color: {color}33;">
                    <div style="color: {color}; font-size:0.7rem; text-transform:uppercase; letter-spacing:1px;">
                        {s['signal']}
                    </div>
                    <div style="color:#e0e0e0; font-size:0.9rem; font-weight:600; margin:2px 0;">{name}</div>
                    <div style="color:#8892b0; font-size:0.8rem;">
                        Confidence: <span style="color:{color};">{s['confidence']}/100</span>
                    </div>
                    <div style="color:#78909c; font-size:0.7rem; margin-top:4px;">{s.get('reason', '')[:80]}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()

        # ── Multi-Timeframe Analysis ──────────────────────────────
        st.markdown("### 🕐 Multi-Timeframe Opportunities")
        st.markdown(
            "<p style='color: #8892b0; font-size: 0.85rem; margin-bottom: 16px;'>"
            "The bot scans additional timeframes to find other profitable setups for the same ticker</p>",
            unsafe_allow_html=True,
        )

        tf_results = {}
        tf_progress = st.progress(0, text="Scanning additional timeframes...")

        for i, (tf_name, tf_period, tf_interval, atr_mult) in enumerate(ADDITIONAL_TF):
            if tf_name == timeframe:
                tf_results[tf_name] = None  # Skip primary timeframe
                tf_progress.progress((i + 1) / len(ADDITIONAL_TF), text=f"Skipping {tf_name} (primary)...")
                continue

            tf_progress.progress((i + 1) / len(ADDITIONAL_TF), text=f"Analyzing {tf_name}...")
            result = analyze_timeframe(ticker_full, tf_period, tf_interval, atr_mult)
            if result is None:
                # Try without suffix
                result = analyze_timeframe(ticker, tf_period, tf_interval, atr_mult)
            tf_results[tf_name] = result
            time.sleep(0.3)  # Rate limiting

        tf_progress.empty()

        # Display TF results
        tf_cols = st.columns(len([k for k in ADDITIONAL_TF if k[0] != timeframe]))
        col_idx = 0
        for tf_name, _, _, _ in ADDITIONAL_TF:
            if tf_name == timeframe:
                continue
            result = tf_results.get(tf_name)
            with tf_cols[col_idx]:
                col_idx += 1
                if result and result["signal"] != "neutral":
                    tf_color = "#00c853" if result["signal"] == "buy" else "#ff1744"
                    tf_label = "CALL" if result["signal"] == "buy" else "PUT"
                    st.markdown(f"""
                    <div class="tf-card">
                        <div class="tf-label">{tf_name}</div>
                        <div class="tf-direction" style="color:{tf_color};">{tf_label}</div>
                        <div class="tf-profit" style="color:{tf_color};">
                            {result.get('potential_return', 0):+.1f}%
                        </div>
                        <div class="tf-confidence">
                            Confidence: {result['confidence']}/100
                            {'· R/R: ' + str(result.get('risk_reward', 0)) if result.get('risk_reward') else ''}
                        </div>
                        {f'''<div style="color:#78909c; font-size:0.7rem; margin-top:4px;">
                            Entry: {currency}{result['price']} · Target: {currency}{result.get('target', 0)}
                        </div>''' if result.get('target') else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="tf-card" style="opacity:0.5;">
                        <div class="tf-label">{tf_name}</div>
                        <div style="color:#78909c; font-size:0.9rem;">⏸️ Neutral</div>
                        <div style="color:#555; font-size:0.8rem;">No clear signal</div>
                    </div>
                    """, unsafe_allow_html=True)

        st.divider()

        # ── Options Chain (if available) ──────────────────────────
        st.markdown("### 📋 Options Chain — ATM Pricing")
        with st.spinner("Fetching options data..."):
            opt = fetch_options_chain(ticker_full)
            if opt is None:
                opt = fetch_options_chain(ticker)

        if opt is not None and not opt.empty:
            st.dataframe(
                opt[["strike", "lastPrice", "bid", "ask", "impliedVolatility", "type"]].round(2),
                column_config={
                    "strike": st.column_config.NumberColumn("Strike", format=f"{currency}%.2f"),
                    "lastPrice": st.column_config.NumberColumn("Last", format=f"{currency}%.2f"),
                    "bid": st.column_config.NumberColumn("Bid", format=f"{currency}%.2f"),
                    "ask": st.column_config.NumberColumn("Ask", format=f"{currency}%.2f"),
                    "impliedVolatility": st.column_config.NumberColumn("IV", format="%.1f%%"),
                    "type": st.column_config.TextColumn("Type"),
                },
                use_container_width=True,
                hide_index=True,
            )
            st.caption("Nearest ATM options for the next expiration cycle")
        else:
            st.info("ℹ️ Options chain data not available for this ticker.")

        st.divider()

        # ── Trade Plan Summary ────────────────────────────────────
        st.markdown("### 📝 Trade Plan Summary")

        rr_grade = "Excellent" if risk_reward >= 3 else "Good" if risk_reward >= 2 else "Fair" if risk_reward >= 1 else "Poor"
        confidence_grade = "High" if confidence >= 70 else "Moderate" if confidence >= 45 else "Speculative"

        plan_cols = st.columns(3)
        with plan_cols[0]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(124,77,255,0.1), rgba(0,200,83,0.05));
                        border: 1px solid rgba(124,77,255,0.2); border-radius: 12px; padding: 16px;">
                <div style="color:#78909c; font-size:0.75rem;">DIRECTION</div>
                <div style="color:{'#00c853' if call_put == 'CALL' else '#ff1744'}; font-size:1.5rem; font-weight:700;">
                    {call_put}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with plan_cols[1]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(124,77,255,0.1), rgba(0,200,83,0.05));
                        border: 1px solid rgba(124,77,255,0.2); border-radius: 12px; padding: 16px;">
                <div style="color:#78909c; font-size:0.75rem;">CONFIDENCE</div>
                <div style="color:#e0e0e0; font-size:1.5rem; font-weight:700;">
                    {confidence_grade}
                </div>
                <div style="color:#8892b0; font-size:0.8rem;">{confidence}/100 score</div>
            </div>
            """, unsafe_allow_html=True)
        with plan_cols[2]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(124,77,255,0.1), rgba(0,200,83,0.05));
                        border: 1px solid rgba(124,77,255,0.2); border-radius: 12px; padding: 16px;">
                <div style="color:#78909c; font-size:0.75rem;">RISK/REWARD</div>
                <div style="color:#ffd700; font-size:1.5rem; font-weight:700;">
                    {rr_grade}
                </div>
                <div style="color:#8892b0; font-size:0.8rem;">{risk_reward}:1 ratio</div>
            </div>
            """, unsafe_allow_html=True)

        # Actions
        st.markdown("### 🎯 Suggested Action")
        if confidence >= 60 and risk_reward >= 2:
            action_msg = f"✅ **Strong setup!** Consider entering a {call_put} position at {currency}{entry_price:.2f} with target {currency}{target_price:.2f} and stop at {currency}{stop_price:.2f}"
            st.success(action_msg)
        elif confidence >= 40 and risk_reward >= 1:
            action_msg = f"⚠️ **Moderate setup.** You could enter a {call_put} position at {currency}{entry_price:.2f}, but consider a tighter stop or wait for confirmation"
            st.warning(action_msg)
        else:
            action_msg = f"ℹ️ **Weak signal.** The bot suggests waiting for better alignment before entering a {call_put} position"
            st.info(action_msg)

        # Risk disclaimer
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(255,152,0,0.05), rgba(255,23,68,0.03));
                    border: 1px solid rgba(255,152,0,0.15); border-radius: 12px;
                    padding: 16px; margin-top: 20px;">
            <p style="color: #90a4ae; font-size: 0.75rem; line-height: 1.5; margin: 0;">
            ⚠️ <strong>Risk Disclaimer:</strong> This analysis is for <strong>educational and informational purposes only</strong>
            and does NOT constitute financial advice. Trading involves substantial risk of loss. Past performance
            is not indicative of future results. The signals generated are based on technical analysis algorithms
            and may not be accurate. <strong>You alone are solely responsible</strong> for your trading decisions.
            Always conduct your own due diligence and consult a qualified financial advisor.
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif analyze_btn and not ticker:
        st.error("❌ Please enter a ticker symbol to analyze.")
