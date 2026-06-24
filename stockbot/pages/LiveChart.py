"""LiveChart — Real-time candlestick chart with analysis, historical snapshots, and comparison.

User inputs a ticker, selects a universe, and gets:
- Today's live candlestick chart with full technical analysis + signal summary
- A historical date snapshot with the same analysis for that point in time
- Side-by-side comparison between past and present
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta, date
import math
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.markets import get_current_market_key, get_market_config, get_currency, apply_suffix
from utils.ticker_search import search_tickers
from data.fetcher import fetch_historical, fetch_fundamentals
from analysis.indicators import add_all_indicators
from analysis.strategies import run_all_strategies
from analysis.screener import calculate_target_price, estimate_potential_return, screen_stock
from config import STRATEGY_WEIGHTS

# ── Page CSS ────────────────────────────────────────────────────────
_PAGE_CSS = """
<style>
.live-hero {
    background: linear-gradient(135deg, #0a1628 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid rgba(0, 200, 255, 0.3);
    border-radius: 20px;
    padding: 24px 30px;
    margin: 10px 0 20px 0;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.live-hero-glow {
    position: absolute; top: -50%; left: -50%; width: 200%; height: 200%;
    background: radial-gradient(circle at center, rgba(0,200,255,0.08) 0%, transparent 60%);
    animation: liveGlow 4s ease-in-out infinite;
}
@keyframes liveGlow {
    0%, 100% { transform: translate(0, 0); }
    50% { transform: translate(20px, -20px); }
}
.live-content { position: relative; z-index: 1; }
.live-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(0,200,255,0.2), rgba(0,200,83,0.1));
    border: 1px solid rgba(0,200,255,0.4);
    border-radius: 20px;
    padding: 4px 16px; font-size: 0.7rem; color: #00c8ff;
    letter-spacing: 2px; margin-bottom: 12px;
    animation: pulseLiveBadge 2s ease-in-out infinite;
}
@keyframes pulseLiveBadge { 0%,100%{opacity:1} 50%{opacity:0.6} }
.live-title {
    font-size: 2.8rem !important; font-weight: 800 !important; margin-bottom: 6px !important;
    background: linear-gradient(135deg, #00c8ff, #7c4dff, #00c853) !important;
    -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important;
}
.live-subtitle { color: #b0bec5; font-size: 0.95rem; }

.snapshot-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid rgba(124,77,255,0.25);
    border-radius: 14px; padding: 20px;
    height: 100%;
    transition: all 0.3s ease;
}
.snapshot-card:hover {
    border-color: #7c4dff;
    box-shadow: 0 4px 20px rgba(124,77,255,0.15);
}
.snapshot-header {
    font-size: 0.8rem; color: #78909c; text-transform: uppercase; letter-spacing: 1px;
    margin-bottom: 8px;
}
.snapshot-price { font-size: 1.8rem; font-weight: 700; color: #e0e0e0; }
.snapshot-change { font-size: 1rem; font-weight: 600; }
.snapshot-metric { 
    background: rgba(124,77,255,0.08);
    border-radius: 8px; padding: 8px 12px;
    margin: 4px 0;
}
.snapshot-metric-label { color: #78909c; font-size: 0.7rem; }
.snapshot-metric-value { color: #e0e0e0; font-size: 0.95rem; font-weight: 600; }

.compare-bar {
    display: flex; justify-content: space-between; align-items: center;
    background: linear-gradient(135deg, rgba(0,200,255,0.08), rgba(124,77,255,0.05));
    border: 1px solid rgba(0,200,255,0.2);
    border-radius: 12px; padding: 16px 20px;
    margin: 10px 0;
}
.compare-label { color: #78909c; font-size: 0.75rem; }
.compare-value { color: #e0e0e0; font-size: 1.2rem; font-weight: 700; }

.comp-gain { color: #00c853; }
.comp-loss { color: #ff1744; }
.comp-neutral { color: #ffd700; }
</style>
"""

# ── Strategy Labels ─────────────────────────────────────────────────
STRATEGY_LABELS = {
    "ma_crossover": "MA Cross",
    "rsi_mean_reversion": "RSI",
    "macd_divergence": "MACD",
    "bollinger_squeeze": "Bollinger",
    "volume_surge": "Volume",
    "multi_tf_confluence": "Multi-TF",
    "atr_breakout": "ATR Break",
}

# ── Chart Interval Mapping ──────────────────────────────────────────
CHART_OPTIONS = {
    "Today (5min)": ("5d", "5m"),
    "Today (15min)": ("5d", "15m"),
    "1 Hour": ("5d", "60m"),
    "1 Day": ("1mo", "1d"),
    "5 Days": ("5d", "1d"),
    "1 Month": ("1mo", "1d"),
    "3 Months": ("3mo", "1d"),
    "6 Months": ("6mo", "1d"),
    "1 Year": ("1y", "1d"),
    "2 Years": ("2y", "1wk"),
}


def _safe(val, default=0.0):
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


def search_company(query: str) -> list[str]:
    """Search for a company by name using the multi-source ticker search."""
    if not query or len(query) < 2:
        return []
    try:
        results = search_tickers(query, limit=8)
        return [r["symbol"] for r in results]
    except Exception:
        pass
    return []


def analyze_snapshot(df: pd.DataFrame) -> dict | None:
    """Run full analysis on a dataframe and return the signal and metrics."""
    if df is None or len(df) < 30:
        return None

    df_i = add_all_indicators(df.copy())
    if df_i is None or len(df_i) < 30:
        return None

    signals = run_all_strategies(df_i)
    active = [s for s in signals if s["signal"] != "neutral" and s["confidence"] > 0]

    if not active:
        return {"signal": "neutral", "confidence": 0, "strategies": 0}

    buy_w = sum(s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active if s["signal"] == "buy")
    sell_w = sum(s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active if s["signal"] == "sell")
    total_w = sum(STRATEGY_WEIGHTS.get(s["strategy"], 1.0) for s in active)

    if total_w == 0:
        return {"signal": "neutral", "confidence": 0, "strategies": 0}

    if buy_w > sell_w:
        direction = "buy"
        conf = min(100, int((buy_w / total_w) * 100))
    elif sell_w > buy_w:
        direction = "sell"
        conf = min(100, int((sell_w / total_w) * 100))
    else:
        return {"signal": "neutral", "confidence": 0, "strategies": 0}

    price = float(df_i["close"].iloc[-1])
    targets = calculate_target_price(df_i, direction)
    potential = estimate_potential_return(targets["target"], price) if targets["target"] else 0

    return {
        "signal": direction,
        "confidence": conf,
        "price": round(price, 2),
        "target": round(targets["target"], 2) if targets["target"] else None,
        "stop_loss": round(targets["stop_loss"], 2) if targets["stop_loss"] else None,
        "risk_reward": targets["risk_reward"],
        "potential_return": potential,
        "strategies": len(active),
        "strategy_detail": active,
        "rsi": round(float(df_i["rsi"].iloc[-1]), 1) if "rsi" in df_i.columns else None,
        "ema_9": round(float(df_i["ema_9"].iloc[-1]), 2) if "ema_9" in df_i.columns else None,
        "ema_21": round(float(df_i["ema_21"].iloc[-1]), 2) if "ema_21" in df_i.columns else None,
        "ema_50": round(float(df_i["ema_50"].iloc[-1]), 2) if "ema_50" in df_i.columns else None,
        "atr_pct": round(float(df_i["atr_percent"].iloc[-1]), 2) if "atr_percent" in df_i.columns else None,
        "volume_ratio": round(float(df_i["volume_ratio"].iloc[-1]), 2) if "volume_ratio" in df_i.columns else None,
    }


def plot_candlestick_chart(df: pd.DataFrame, ticker: str, timeframe: str, currency: str,
                           title_suffix: str = "") -> go.Figure:
    """Create a full candlestick chart with EMAs, volume, and RSI."""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{ticker}{title_suffix}", "Volume", "RSI (14)"),
    )

    # Candlesticks
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["open"], high=df["high"],
            low=df["low"], close=df["close"], name="Price",
            increasing_line_color="#00c853", decreasing_line_color="#ff1744",
        ),
        row=1, col=1,
    )

    # EMAs
    for ema, color, name in [
        ("ema_9", "#00bfff", "EMA 9"),
        ("ema_21", "#ffd700", "EMA 21"),
        ("ema_50", "#ff6b35", "EMA 50"),
        ("ema_200", "#aa66ff", "EMA 200"),
    ]:
        if ema in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df[ema], name=name,
                           line=dict(color=color, width=1.2), opacity=0.7),
                row=1, col=1,
            )

    # Bollinger Bands
    if "bb_upper" in df.columns and "bb_lower" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_upper"], name="BB Upper",
                       line=dict(color="#888", width=0.5, dash="dash"), opacity=0.4),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_lower"], name="BB Lower",
                       line=dict(color="#888", width=0.5, dash="dash"), opacity=0.4),
            row=1, col=1,
        )

    # Volume
    vol_colors = ["#ff1744" if row["close"] < row["open"] else "#00c853" for _, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df["volume"], name="Volume",
               marker_color=vol_colors, opacity=0.5),
        row=2, col=1,
    )

    # RSI
    if "rsi" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["rsi"], name="RSI",
                       line=dict(color="#aa66ff", width=1.5)),
            row=3, col=1,
        )
        fig.add_hline(y=70, line_dash="dash", line_color="#ff4444", opacity=0.4, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", opacity=0.4, row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="#888", opacity=0.2, row=3, col=1)
        fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])

    fig.update_layout(
        template="plotly_dark", height=600,
        showlegend=True,
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=9)),
        margin=dict(l=10, r=10, t=40, b=10),
        hovermode="x unified",
    )
    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text=f"Price ({currency})", row=1, col=1,
                     showgrid=True, gridcolor="rgba(255,255,255,0.05)")
    fig.update_yaxes(title_text="Volume", row=2, col=1,
                     showgrid=True, gridcolor="rgba(255,255,255,0.05)")

    return fig


def render_snapshot_card(snapshot: dict, label: str, currency: str):
    """Render analysis summary card for a snapshot."""
    if snapshot is None or snapshot.get("signal") == "neutral":
        st.markdown(f"""
        <div class="snapshot-card">
            <div class="snapshot-header">{label}</div>
            <div style="color:#78909c; text-align:center; padding:20px 0;">No clear signal</div>
        </div>
        """, unsafe_allow_html=True)
        return

    sig = snapshot["signal"]
    sig_color = "#00c853" if sig == "buy" else "#ff1744"
    sig_label = "CALL" if sig == "buy" else "PUT"
    conf = snapshot["confidence"]

    st.markdown(f"""
    <div class="snapshot-card">
        <div class="snapshot-header">{label}</div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="background:{sig_color}22; border:1px solid {sig_color}44;
                         border-radius:12px; padding:2px 14px; font-size:1rem;
                         font-weight:700; color:{sig_color};">{sig_label}</span>
            <span style="color:#e0e0e0; font-size:1.3rem; font-weight:700;">
                {currency}{snapshot['price']:.2f}
            </span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
            <div class="snapshot-metric">
                <div class="snapshot-metric-label">Confidence</div>
                <div class="snapshot-metric-value" style="color:{'#00c853' if conf >= 65 else '#ffd700' if conf >= 40 else '#ff1744'}">
                    {conf}/100
                </div>
            </div>
            <div class="snapshot-metric">
                <div class="snapshot-metric-label">Return</div>
                <div class="snapshot-metric-value" style="color:{'#00c853' if snapshot.get('potential_return', 0) > 0 else '#ff1744'}">
                    {snapshot.get('potential_return', 0):+.1f}%
                </div>
            </div>
            <div class="snapshot-metric">
                <div class="snapshot-metric-label">R/R</div>
                <div class="snapshot-metric-value" style="color:#ffd700;">
                    {snapshot.get('risk_reward', 0):.2f}
                </div>
            </div>
            <div class="snapshot-metric">
                <div class="snapshot-metric-label">RSI</div>
                <div class="snapshot-metric-value">
                    {snapshot.get('rsi', '—')}
                </div>
            </div>
        </div>
        {f'''<div style="margin-top:8px; display:flex; gap:8px;">
            <span style="font-size:0.75rem; color:#78909c;">🎯 {currency}{snapshot.get('target', 0):.2f}</span>
            <span style="font-size:0.75rem; color:#78909c;">🛑 {currency}{snapshot.get('stop_loss', 0):.2f}</span>
        </div>''' if snapshot.get('target') else ''}
        <div style="margin-top:6px; font-size:0.7rem; color:#555;">
            {snapshot.get('strategies', 0)} strategies · ATR: {snapshot.get('atr_pct', 0):.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_comparison_bar(current: dict | None, historical: dict | None, currency: str):
    """Render a side-by-side comparison between current and historical data."""
    if not current or not historical:
        return

    c_price = current.get("price", 0)
    h_price = historical.get("price", 0)
    price_change = c_price - h_price
    change_pct = (price_change / h_price * 100) if h_price > 0 else 0

    c_sig = current.get("signal", "neutral")
    h_sig = historical.get("signal", "neutral")
    sig_map = {"buy": "CALL ↑", "sell": "PUT ↓", "neutral": "—"}

    price_class = "comp-gain" if change_pct >= 0 else "comp-loss"

    st.markdown(f"""
    <div class="compare-bar">
        <div style="text-align:center; flex:1;">
            <div class="compare-label">HISTORICAL</div>
            <div class="compare-value">{currency}{h_price:.2f}</div>
            <div style="color:#78909c; font-size:0.8rem;">Signal: {sig_map.get(h_sig, '—')}</div>
        </div>
        <div style="text-align:center; flex:1; border-left:1px solid rgba(124,77,255,0.2); border-right:1px solid rgba(124,77,255,0.2);">
            <div class="compare-label">CHANGE</div>
            <div class="compare-value {price_class}">
                {change_pct:+.2f}%
            </div>
            <div style="color:#78909c; font-size:0.8rem;">
                {currency}{price_change:+.2f}
            </div>
        </div>
        <div style="text-align:center; flex:1;">
            <div class="compare-label">CURRENT</div>
            <div class="compare-value">{currency}{c_price:.2f}</div>
            <div style="color:#78909c; font-size:0.8rem;">Signal: {sig_map.get(c_sig, '—')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show():
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    market_key = get_current_market_key()
    mkt_cfg = get_market_config(market_key)
    currency = mkt_cfg["currency"]
    suffix = mkt_cfg["suffix"]

    # ── Hero ──────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="live-hero">
        <div class="live-hero-glow"></div>
        <div class="live-content">
            <div class="live-badge">● LIVE · {mkt_cfg['emoji']} {mkt_cfg['name']}</div>
            <h1 class="live-title">📊 LiveChart</h1>
            <p class="live-subtitle">
                Real-time candlestick charts · Historical snapshots · Side-by-side comparison
                — analyze any stock at any point in time
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Input Controls ────────────────────────────────────────────
    with st.expander("🔍 Search & Configure", expanded=True):
        col_s1, col_s2, col_s3 = st.columns([2, 1, 1])

        with col_s1:
            # Smart ticker search with autocomplete
            ticker_input = st.text_input(
                "Search Company or Ticker",
                value=st.session_state.get("live_ticker_input", ""),
                placeholder="Type company name or ticker (e.g., 'Reliance', 'RELIANCE')",
                key="live_ticker_input",
                help="Search by company name, ticker symbol, or short form"
            ).strip().upper()
            
            # Search for tickers
            if ticker_input:
                search_results = search_tickers(ticker_input, limit=5)
                
                if search_results:
                    # Create dropdown options
                    ticker_options = [f"{r['symbol']} - {r['name']} ({r['exchange']})" for r in search_results]
                    selected_idx = st.selectbox(
                        "Select Ticker",
                        range(len(ticker_options)),
                        format_func=lambda i: ticker_options[i],
                        label_visibility="collapsed"
                    )
                    ticker_input = search_results[selected_idx]["symbol"]
                else:
                    # No results, use input as-is
                    st.caption(f"Using: {ticker_input}")
            else:
                ticker_input = ""

            ticker_full = apply_suffix(ticker_input, market_key) if ticker_input else ""

        with col_s2:
            chart_range = st.selectbox(
                "Chart Range",
                options=list(CHART_OPTIONS.keys()),
                index=6,  # 3 Months
                key="live_range",
            )
            period, interval = CHART_OPTIONS[chart_range]

        with col_s3:
            # Universe display context
            universal_options = list(mkt_cfg["universes"].keys())
            st.selectbox(
                "Market Universe",
                options=universal_options,
                index=0,
                key="live_universe",
                help="Reference universe (for context only — you enter any ticker above)",
            )

        # ── Date Picker for Historical Snapshot ───────────────────
        st.markdown("### 📅 Historical Snapshot")
        st.markdown(
            "<p style='color:#8892b0; font-size:0.85rem;'>Select a past date to see the chart snapshot, "
            "analysis, and signal as it was on that day — then compare with the current day.</p>",
            unsafe_allow_html=True,
        )

        col_d1, col_d2 = st.columns([1, 1])
        with col_d1:
            use_historical = st.checkbox(
                "Compare with historical date",
                value=st.session_state.get("live_use_hist", False),
                key="live_use_hist",
                help="Enable to select a past date and compare with today's data",
            )

        hist_date = None
        if use_historical:
            with col_d2:
                max_date = date.today() - timedelta(days=5)  # Need some data gap
                min_date = date.today() - timedelta(days=365 * 3)
                hist_date = st.date_input(
                    "Historical Date",
                    value=max_date - timedelta(days=30),
                    min_value=min_date,
                    max_value=max_date,
                    key="live_hist_date",
                    help="Pick a past trading day to snapshot",
                )

        analyze_btn = st.button("📊 Generate LiveChart", type="primary", use_container_width=True)

    st.divider()

    # ── Main Analysis ─────────────────────────────────────────────
    if analyze_btn and ticker_input:
        if not ticker_input:
            st.error("❌ Please enter a ticker symbol.")
            st.stop()

        with st.spinner(f"📊 Fetching live data for {ticker_input}..."):
            # Fetch current data
            df_current = fetch_historical(ticker_full, period=period, interval=interval)
            if df_current is None or len(df_current) < 10:
                df_current = fetch_historical(ticker_input, period=period, interval=interval)
            if df_current is None or len(df_current) < 10:
                st.error(f"❌ Could not fetch data for {ticker_input}. Check the ticker and try again.")
                st.stop()

            # Fetch fundamentals
            info = fetch_fundamentals(ticker_full) or fetch_fundamentals(ticker_input)

            # Run current analysis
            current_snapshot = analyze_snapshot(df_current)

            # Fetch historical data if requested
            df_historical = None
            historical_snapshot = None
            if use_historical and hist_date:
                # Fetch more data to cover the historical date
                hist_period = "2y" if period in ("5d", "1mo") else period
                df_full = fetch_historical(ticker_full, period=hist_period, interval=interval)
                if df_full is None or len(df_full) < 20:
                    df_full = fetch_historical(ticker_input, period=hist_period, interval=interval)

                if df_full is not None and len(df_full) >= 20:
                    # Find the historical date index
                    # Match timezone: yfinance returns tz-aware (America/New_York), so make Timestamp tz-aware too
                    tz = getattr(df_full.index, 'tz', None)
                    hist_dt = pd.Timestamp(hist_date).tz_localize(tz) if tz else pd.Timestamp(hist_date)
                    # Get data up to and including the historical date
                    hist_data = df_full[df_full.index <= hist_dt]
                    if len(hist_data) >= 30:
                        df_historical = hist_data
                        historical_snapshot = analyze_snapshot(hist_data)
                    else:
                        # Try to get a broader range
                        st.info(f"ℹ️ Limited data for {hist_date}. Using closest available date.")
                        if len(df_full) >= 30:
                            df_historical = df_full.iloc[:len(df_full) // 2]
                            historical_snapshot = analyze_snapshot(df_historical)

        # ── Display Results ───────────────────────────────────────
        # Ticker header with fundamentals
        sector = info.get("sector", "N/A") if info else "N/A"
        mcap = info.get("market_cap", 0) if info else 0
        mcap_str = f"${mcap:,.0f}" if mcap else "N/A"

        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e);
                    border: 1px solid rgba(124,77,255,0.25); border-radius: 16px;
                    padding: 16px 24px; margin-bottom: 16px;
                    display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-size:1.8rem; font-weight:700; color:#e0e0e0;">{ticker_input}</span>
                <span style="font-size:1rem; color:#78909c; margin-left:12px;">{sector}</span>
            </div>
            <div style="display:flex; gap:20px;">
                <div style="text-align:center;">
                    <div style="color:#78909c; font-size:0.7rem;">MARKET CAP</div>
                    <div style="color:#e0e0e0; font-size:0.95rem; font-weight:600;">{mcap_str}</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#78909c; font-size:0.7rem;">RANGE</div>
                    <div style="color:#e0e0e0; font-size:0.95rem; font-weight:600;">{chart_range}</div>
                </div>
                <div style="text-align:center;">
                    <div style="color:#78909c; font-size:0.7rem;">DATA PTS</div>
                    <div style="color:#e0e0e0; font-size:0.95rem; font-weight:600;">{len(df_current)}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Live Candlestick Chart ─────────────────────────────────
        st.markdown("### 📈 Live Candlestick Chart")
        st.caption(f"Showing {chart_range} of data · Interval: {interval}")
        fig = plot_candlestick_chart(df_current, ticker_input, chart_range, currency)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        st.divider()

        # ── Current Analysis Summary ──────────────────────────────
        st.markdown("### 🎯 Current Analysis & Signal")
        col_c1, col_c2 = st.columns(2)

        with col_c1:
            render_snapshot_card(current_snapshot, "📡 CURRENT DAY", currency)

        with col_c2:
            # Quick metrics table
            if current_snapshot and current_snapshot.get("signal") != "neutral":
                sd = current_snapshot.get("strategy_detail", [])
                if sd:
                    st.markdown("""
                    <div class="snapshot-card">
                        <div class="snapshot-header">ACTIVE STRATEGIES</div>
                    """, unsafe_allow_html=True)
                    for s in sd[:6]:
                        color = "#00c853" if s["signal"] == "buy" else "#ff1744"
                        name = STRATEGY_LABELS.get(s["strategy"], s["strategy"])
                        st.markdown(
                            f"<div style='display:flex; justify-content:space-between; "
                            f"padding:3px 0; border-bottom:1px solid rgba(255,255,255,0.03);'>"
                            f"<span style='color:#b0bec5; font-size:0.85rem;'>{name}</span>"
                            f"<span style='color:{color}; font-size:0.85rem; font-weight:600;'>"
                            f"{s['signal'].upper()} ({s['confidence']})</span></div>",
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # ── Comparison Section ────────────────────────────────────
        if use_historical and historical_snapshot:
            st.markdown("### 🔄 Past vs Present Comparison")
            st.markdown(
                f"<p style='color:#8892b0; font-size:0.85rem;'>"
                f"Comparing today's analysis with a snapshot from "
                f"<strong>{hist_date.strftime('%B %d, %Y') if hist_date else 'selected date'}</strong></p>",
                unsafe_allow_html=True,
            )

            # Comparison bar
            render_comparison_bar(current_snapshot, historical_snapshot, currency)

            # Side-by-side snapshot cards
            comp_col1, comp_col2 = st.columns(2)
            with comp_col1:
                render_snapshot_card(
                    historical_snapshot,
                    f"📜 HISTORICAL — {hist_date.strftime('%b %d, %Y') if hist_date else ''}",
                    currency,
                )
            with comp_col2:
                render_snapshot_card(current_snapshot, "📡 CURRENT DAY", currency)

            # Historical chart
            if df_historical is not None:
                st.markdown(f"### 📜 Historical Chart Snapshot ({hist_date.strftime('%b %d, %Y') if hist_date else ''})")
                with st.expander("View Historical Chart", expanded=False):
                    hist_fig = plot_candlestick_chart(
                        df_historical, ticker_input, chart_range, currency,
                        title_suffix=f" — Snapshot: {hist_date.strftime('%b %d, %Y') if hist_date else ''}",
                    )
                    st.plotly_chart(hist_fig, use_container_width=True, config={"displayModeBar": False})

                    # Historical data table
                    with st.expander("📋 Historical Data Table", expanded=False):
                        recent_hist = df_historical.tail(15).round(2)
                        cols = ["open", "high", "low", "close", "volume"]
                        avail = [c for c in cols if c in recent_hist.columns]
                        st.dataframe(recent_hist[avail], use_container_width=True)

        # ── Current Data Table ────────────────────────────────────
        st.markdown("### 📋 Recent Data")
        with st.expander("View Recent Price Data", expanded=False):
            recent = df_current.tail(15).round(2)
            cols = ["open", "high", "low", "close", "volume"]
            for extra in ["rsi", "atr_percent", "ema_9", "ema_21", "ema_50"]:
                if extra in recent.columns:
                    cols.append(extra)
            avail = [c for c in cols if c in recent.columns]
            st.dataframe(recent[avail], use_container_width=True)

            # Download
            csv_data = recent.to_csv()
            st.download_button(
                "📥 Download CSV",
                data=csv_data,
                file_name=f"{ticker_input}_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )

        # ── Risk Disclaimer ───────────────────────────────────────
        st.markdown("""
        <div style="background: rgba(255,152,0,0.05); border: 1px solid rgba(255,152,0,0.15);
                    border-radius: 12px; padding: 16px; margin-top: 20px;">
            <p style="color: #90a4ae; font-size: 0.7rem; line-height: 1.5; margin: 0;">
            ⚠️ <strong>Risk Disclaimer:</strong> This analysis is for educational and informational purposes only
            and does NOT constitute financial advice. Past performance is not indicative of future results.
            Historical snapshots are approximations based on available data and may not reflect real-time
            conditions at that exact date. Always conduct your own due diligence before making trading decisions.
            </p>
        </div>
        """, unsafe_allow_html=True)

    elif analyze_btn and not ticker_input:
        st.error("❌ Please enter a ticker symbol to analyze.")
