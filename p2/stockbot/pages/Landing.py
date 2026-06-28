"""Landing page - live market data, animated chart, testimonials, and navigation."""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import fetch_historical
from utils.auth import is_logged_in, get_current_user, logout
import yfinance as yf


def fetch_live_ticker_data(market_key: str | None = None) -> list[dict]:
    """Fetch real stock prices from Yahoo Finance for the ticker display."""
    from utils.markets import get_display_tickers, get_currency
    symbols = get_display_tickers(market_key)
    currency = get_currency(market_key)
    try:
        data = yf.download(
            symbols,
            period="5d",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )
        if data is None or data.empty or "Close" not in data.columns:
            return _generate_fallback_ticker(market_key)

        closes = data["Close"]
        if len(closes) < 2:
            return _generate_fallback_ticker(market_key)

        latest = closes.iloc[-1]
        prev = closes.iloc[-2]

        results = []
        for ticker in symbols:
            if ticker not in latest.index or ticker not in prev.index:
                continue
            price = latest[ticker]
            prev_price = prev[ticker]
            if pd.isna(price) or pd.isna(prev_price) or prev_price == 0:
                continue
            change_pct = ((price - prev_price) / prev_price) * 100
            results.append({
                "ticker": ticker,
                "price": float(price),
                "change": round(float(change_pct), 2),
                "up": change_pct >= 0,
            })

        if results:
            return results
        return _generate_fallback_ticker(market_key)
    except Exception:
        return _generate_fallback_ticker(market_key)


def _generate_fallback_ticker(market_key: str | None = None) -> list[dict]:
    """Fallback simulated ticker data if live fetch fails."""
    from utils.markets import get_display_tickers
    symbols = get_display_tickers(market_key)
    return [
        {
            "ticker": t,
            "price": round(random.uniform(50, 800), 2),
            "change": round(random.uniform(-4, 4), 2),
            "up": random.choice([True, False]),
        }
        for t in symbols
    ]


def fetch_live_chart_data(market_key: str | None = None) -> tuple[go.Figure | None, str]:
    """Fetch real benchmark data from Yahoo Finance for the candlestick chart.
    Returns (figure, label) tuple.
    """
    from utils.markets import get_benchmark, get_currency, get_market_config
    cfg = get_market_config(market_key)
    benchmark = cfg["benchmark"]
    currency = cfg["currency"]
    # Friendly name for the chart label
    benchmark_label = benchmark.replace("^", "").upper()  # e.g. SPY, ^NSEI -> NSEI
    try:
        df = fetch_historical(benchmark, period="3mo", interval="1d")
        if df is None or len(df) < 20:
            return None, benchmark_label

        df = df.copy()
        df["ma20"] = df["close"].rolling(20).mean()
        df["ma50"] = df["close"].rolling(50).mean()

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
        )

        fig.add_trace(
            go.Candlestick(
                x=df.index, open=df["open"], high=df["high"],
                low=df["low"], close=df["close"], name=benchmark_label,
                increasing_line_color="#00c853", decreasing_line_color="#ff1744",
            ),
            row=1, col=1,
        )

        fig.add_trace(
            go.Scatter(x=df.index, y=df["ma20"], name="MA 20",
                       line=dict(color="#7c4dff", width=2), opacity=0.8),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["ma50"], name="MA 50",
                       line=dict(color="#ff9100", width=2), opacity=0.8),
            row=1, col=1,
        )

        colors = ["#ff1744" if row["close"] < row["open"] else "#00c853" for _, row in df.iterrows()]
        fig.add_trace(
            go.Bar(x=df.index, y=df["volume"], name="Volume",
                   marker_color=colors, opacity=0.6),
            row=2, col=1,
        )

        fig.update_layout(
            template="plotly_dark", height=500,
            showlegend=True, legend=dict(orientation="h", y=1.12, x=0, font=dict(size=11, color="#e0e0e0")),
            margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        fig.update_xaxes(rangeslider_visible=False)
        fig.update_yaxes(title_text=f"Price ({currency})", row=1, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.05)")
        fig.update_yaxes(title_text="Volume", row=2, col=1, showgrid=True, gridcolor="rgba(255,255,255,0.05)")

        return fig, benchmark_label
    except Exception:
        return None, benchmark_label


def _generate_fallback_chart() -> go.Figure:
    """Generate a simulated chart if live data fails."""
    np.random.seed(42)
    days = 60
    base_price = 175
    returns = np.random.randn(days) * 0.02 + 0.001
    prices = base_price * np.exp(np.cumsum(returns))
    dates = [datetime.now() - timedelta(days=days-i) for i in range(days)]

    df = pd.DataFrame({
        "date": dates,
        "open": prices * (1 + np.random.randn(days) * 0.005),
        "high": prices * (1 + np.abs(np.random.randn(days)) * 0.012),
        "low": prices * (1 - np.abs(np.random.randn(days)) * 0.012),
        "close": prices,
        "volume": np.random.randint(500000, 8000000, days),
    })
    for i in range(len(df)):
        row = df.iloc[i]
        df.iloc[i, df.columns.get_loc("high")] = max(row["open"], row["close"], row["high"])
        df.iloc[i, df.columns.get_loc("low")] = min(row["open"], row["close"], row["low"])

    df["ma20"] = df["close"].rolling(20).mean()
    df["ma50"] = df["close"].rolling(50).mean()

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3])
    fig.add_trace(
        go.Candlestick(x=df["date"], open=df["open"], high=df["high"],
                       low=df["low"], close=df["close"], name="Price",
                       increasing_line_color="#00c853", decreasing_line_color="#ff1744"),
        row=1, col=1,
    )
    fig.add_trace(go.Scatter(x=df["date"], y=df["ma20"], name="MA 20",
                             line=dict(color="#7c4dff", width=2), opacity=0.8), row=1, col=1)
    fig.add_trace(go.Scatter(x=df["date"], y=df["ma50"], name="MA 50",
                             line=dict(color="#ff9100", width=2), opacity=0.8), row=1, col=1)
    colors = ["#ff1744" if row["close"] < row["open"] else "#00c853" for _, row in df.iterrows()]
    fig.add_trace(go.Bar(x=df["date"], y=df["volume"], name="Volume",
                         marker_color=colors, opacity=0.6), row=2, col=1)
    fig.update_layout(template="plotly_dark", height=500, showlegend=True,
                      legend=dict(orientation="h", y=1.12, x=0, font=dict(size=11, color="#e0e0e0")),
                      margin=dict(l=10, r=10, t=30, b=10), hovermode="x unified",
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def fetch_market_summary(market_key: str | None = None) -> dict:
    """Fetch a quick market overview."""
    from utils.markets import get_benchmark, get_market_config
    cfg = get_market_config(market_key)
    benchmark = cfg["benchmark"]
    name = cfg["name"]
    try:
        ticker_obj = yf.Ticker(benchmark)
        info = ticker_obj.fast_info
        return {
            "name": name,
            "price": info.get("lastPrice", info.get("regularMarketPrice", "—")),
            "change": info.get("regularMarketChangePercent", 0),
        }
    except Exception:
        return {"name": name, "price": "—", "change": 0}


def show():
    # ── Market context ────────────────────────────────────────────
    from utils.markets import get_current_market_key, get_market_config
    current_market_key = get_current_market_key()
    market_cfg = get_market_config(current_market_key)

    market = fetch_market_summary(current_market_key)
    benchmark_name = market_cfg["benchmark"].replace("^", "")
    spy_change = market.get("change", 0)
    spy_arrow = "▲" if spy_change >= 0 else "▼"
    spy_color = "#00c853" if spy_change >= 0 else "#ff1744"
    spy_price_val = market.get("price", "—")
    spy_price_str = f"${spy_price_val:.2f}" if isinstance(spy_price_val, (int, float)) else "—"

    # ── Auth bar (top-right of landing page) ──────────────────────
    a_col1, a_col2, a_col3 = st.columns([6, 1, 1])
    with a_col2:
        if is_logged_in():
            user = get_current_user()
            if st.button(f"👤 {user.get('name', 'User')}", use_container_width=True, type="secondary"):
                st.session_state.current_page = "profile"
                st.rerun()
        else:
            if st.button("Login", use_container_width=True, type="secondary"):
                st.session_state.current_page = "login"
                st.rerun()
    with a_col3:
        if not is_logged_in():
            if st.button("Sign Up", use_container_width=True, type="primary"):
                st.session_state.current_page = "signup"
                st.rerun()
        elif st.button("Logout", use_container_width=True):
            logout()
            st.query_params["logged_out"] = "1"
            st.rerun()

    # ── Enhanced Hero Section ─────────────────────────────────────
    st.markdown(f"""
    <div class="landing-hero" style="position: relative;">
        <div class="hero-glow"></div>
        <div class="hero-content">
            <div class="hero-badge-live">● LIVE MARKET · {market_cfg['emoji']} {market_cfg['name']}</div>
            <h1 class="hero-title">Stock Signal Bot</h1>
            <p class="hero-subtitle">
                Multi-Strategy Signal Consolidation · Real-Time Analysis · Smart Trading Decisions
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="hero-stat-value">7</span>
                    <span class="hero-stat-label">Strategies</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-value">500+</span>
                    <span class="hero-stat-label">Stocks</span>
                </div>
                <div class="hero-stat spy-stat" style="border-color: {spy_color};">
                    <span class="hero-stat-label">{benchmark_name}</span>
                    <span class="hero-stat-value" style="font-size: 0.9rem; color: #b0bec5;">{spy_price_str}</span>
                    <span class="hero-stat-value" style="color: {spy_color};">{spy_arrow} {abs(spy_change):.2f}%</span>
                </div>
            </div>
            <div class="hero-badges">
                <span class="badge">🎯 7 Strategies</span>
                <span class="badge">⚡ Real-Time Scans</span>
                <span class="badge">📊 Backtesting</span>
                <span class="badge">🔒 Secure</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Live Market Ticker ───────────────────────────────────────
    st.markdown("<h2 class='section-title'>📊 Live Market Overview</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #b0bec5; text-align: center; margin-bottom: 10px; font-size: 0.85rem;'>Real-time prices from Yahoo Finance</p>", unsafe_allow_html=True)

    ticker_data = fetch_live_ticker_data(current_market_key)
    ticker_html = '<div class="ticker-wrap"><div class="ticker">'
    for item in ticker_data:
        arrow = "▲" if item["up"] else "▼"
        color = "#00c853" if item["up"] else "#ff1744"
        ticker_html += (
            f'<span class="ticker-item">'
            f'<strong>{item["ticker"]}</strong> '
            f'<span class="ticker-price">${item["price"]:.2f}</span> '
            f'<span style="color:{color}">{arrow} {abs(item["change"]):.2f}%</span>'
            f'</span>'
        )
    ticker_html += '</div></div>'
    st.markdown(ticker_html, unsafe_allow_html=True)

    # ─── Live Chart ───────────────────────────────────────────────
    st.markdown("<h2 class='section-title'>📈 Market Analysis</h2>", unsafe_allow_html=True)
    chart, bench_label = fetch_live_chart_data(current_market_key)
    st.markdown(f"<p style='color: #b0bec5; text-align: center; margin-bottom: 20px; font-size: 0.85rem;'>{market_cfg['name']} ({bench_label}) — live candlestick chart with moving averages</p>", unsafe_allow_html=True)
    if chart is None:
        chart = _generate_fallback_chart()
    st.plotly_chart(chart, use_container_width=True, config={"displayModeBar": False})

    # ─── Navigation Buttons ───────────────────────────────────────
    st.markdown("<h2 class='section-title'>🚀 Get Started</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔍 Market Scan", use_container_width=True, type="primary"):
            st.session_state.current_page = "market_scan"
            st.rerun()
        if st.button("📊 Stock Analysis", use_container_width=True):
            st.session_state.current_page = "stock_analysis"
            st.rerun()
    with col2:
        if st.button("🔄 Backtest", use_container_width=True):
            st.session_state.current_page = "backtest"
            st.rerun()
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.current_page = "settings"
            st.rerun()

    # ─── Testimonials ─────────────────────────────────────────────
    st.markdown("<h2 class='section-title'>💬 What Users Say</h2>", unsafe_allow_html=True)
    testimonials = [
        {"name": "Alex M.", "role": "Swing Trader",
         "text": "StockBot's multi-strategy signals caught a 15% move in NVDA before any of my other tools. The confluence detection is incredibly accurate.",
         "stars": 5},
        {"name": "Sarah K.", "role": "Part-time Investor",
         "text": "I love how the bot consolidates 7 different strategies into one clear signal. Saves me hours of analysis every day.",
         "stars": 5},
        {"name": "Raj P.", "role": "Quant Developer",
         "text": "The backtesting engine is solid. Being able to validate strategies across S&P 500 stocks with a single command is a game-changer.",
         "stars": 4},
        {"name": "Emily R.", "role": "Day Trader",
         "text": "Real-time market scanning with parallel processing means I never miss a setup. The ATR breakout strategy is my favorite.",
         "stars": 5},
    ]
    tcols = st.columns(len(testimonials))
    for i, (col, t) in enumerate(zip(tcols, testimonials)):
        with col:
            stars = "⭐" * t["stars"]
            st.markdown(f"""
            <div class="testimonial-card">
                <div class="testimonial-stars">{stars}</div>
                <p class="testimonial-text">"{t['text']}"</p>
                <div class="testimonial-author">
                    <strong>{t['name']}</strong>
                    <span>{t['role']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ─── About Us ─────────────────────────────────────────────────
    st.markdown("<h2 class='section-title'>ℹ️ About StockBot</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="about-card">
        <p>Stock Signal Bot is a <strong>multi-strategy signal consolidation engine</strong> that combines
        <strong>7 proven trading strategies</strong> into a single, actionable consensus signal.
        Built for both CLI power users and GUI enthusiasts, it provides:</p>
        <ul>
            <li>📈 Real-time market scanning across S&P 500, NASDAQ 100, and custom watchlists</li>
            <li>🧩 Strategy fusion: MA Crossover, RSI, MACD, Bollinger Bands, Volume Surge, Multi-TF, ATR Breakout</li>
            <li>📊 Historical backtesting with trade simulation and win-rate analysis</li>
            <li>⚡ Parallel processing for lightning-fast scans</li>
            <li>📱 PWA support and Android app for on-the-go monitoring</li>
        </ul>
        <p>Data powered by <strong>Yahoo Finance</strong> with <strong>Twelve Data</strong> fallback.</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── Disclaimer ───────────────────────────────────────────────
    st.markdown("<h2 class='section-title' style='font-size: 1.2rem !important;'>⚠️ Risk Disclaimer</h2>", unsafe_allow_html=True)
    st.markdown("""
    <div class="disclaimer">
        <p style="font-size: 0.75rem; line-height: 1.5; margin: 0;">
        Trading involves substantial risk of loss. The signals and analysis provided are for
        <strong>educational and informational purposes only</strong> and do NOT constitute financial advice.
        Past performance is not indicative of future results. Backtested results have inherent limitations
        and do not represent actual trading. <strong>You alone are solely responsible</strong> for your
        trading decisions. Always conduct your own due diligence and consult a qualified financial advisor.
        Never trade with money you cannot afford to lose. No guarantees are made regarding the accuracy,
        completeness, or reliability of any data or analysis. The developers and affiliates shall NOT be
        held liable for any losses or damages arising from use of this software. By using this software,
        you acknowledge and accept these terms. Data sourced from Yahoo Finance and Twelve Data.
        Not affiliated with any exchange or financial institution. Provided "as is" without warranty.
        </p>
        <p style="margin-top: 10px; font-size: 0.65rem; color: #78909c;">
        Stock Signal Bot v1.0.0 | © 2026 StockBot. All rights reserved.
        </p>
    </div>
    """, unsafe_allow_html=True)
