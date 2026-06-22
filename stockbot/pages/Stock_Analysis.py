"""Stock Analysis page - deep dive into individual stocks with charts and strategy breakdown."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.markets import get_current_market_key, get_display_tickers, get_currency
from data.fetcher import fetch_historical
from analysis.indicators import add_all_indicators
from signals.generator import analyze_ticker


def plot_price_chart(df: pd.DataFrame, ticker: str):
    """Create an interactive price chart with volume and indicators."""
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{ticker} Price", "Volume", "RSI"),
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price",
            increasing_line_color="#00ff88",
            decreasing_line_color="#ff4444",
        ),
        row=1, col=1,
    )

    # EMAs
    if "ema_9" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["ema_9"], name="EMA 9",
                       line=dict(color="#00bfff", width=1), opacity=0.7),
            row=1, col=1,
        )
    if "ema_21" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["ema_21"], name="EMA 21",
                       line=dict(color="#ffd700", width=1), opacity=0.7),
            row=1, col=1,
        )
    if "ema_50" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["ema_50"], name="EMA 50",
                       line=dict(color="#ff6b35", width=1), opacity=0.7),
            row=1, col=1,
        )

    # Bollinger Bands
    if "bb_upper" in df.columns and "bb_lower" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_upper"], name="BB Upper",
                       line=dict(color="#888", width=0.5, dash="dash"), opacity=0.5),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["bb_lower"], name="BB Lower",
                       line=dict(color="#888", width=0.5, dash="dash"), opacity=0.5),
            row=1, col=1,
        )

    # Volume bars
    colors = ["#ff4444" if row["close"] < row["open"] else "#00ff88" for _, row in df.iterrows()]
    fig.add_trace(
        go.Bar(x=df.index, y=df["volume"], name="Volume",
               marker_color=colors, opacity=0.6),
        row=2, col=1,
    )

    # RSI
    if "rsi" in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["rsi"], name="RSI",
                       line=dict(color="#aa66ff", width=1.5)),
            row=3, col=1,
        )
        # RSI levels
        fig.add_hline(y=70, line_dash="dash", line_color="#ff4444", opacity=0.5, row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", opacity=0.5, row=3, col=1)
        fig.add_hline(y=50, line_dash="dot", line_color="#888", opacity=0.3, row=3, col=1)

    # Layout
    fig.update_layout(
        template="plotly_dark",
        height=700,
        showlegend=True,
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=10)),
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
    )

    fig.update_xaxes(rangeslider_visible=False)
    fig.update_yaxes(title_text=f"Price ({get_currency(get_current_market_key())})", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])

    return fig


def display_strategy_breakdown(strategy_detail: list[dict]):
    """Display strategy signals in a grid of colored cards."""
    if not strategy_detail:
        st.info("No active strategy signals")
        return

    cols = st.columns(min(len(strategy_detail), 3))
    for i, sd in enumerate(strategy_detail):
        with cols[i % 3]:
            color = "#00ff88" if sd["signal"] == "buy" else "#ff4444" if sd["signal"] == "sell" else "#888"
            st.markdown(
                f"""
                <div style="
                    background: #1a1a2e;
                    border: 1px solid {color}44;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 4px 0;
                ">
                    <div style="color: {color}; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">
                        {sd['signal']} — {sd['strategy'].replace('_', ' ').title()}
                    </div>
                    <div style="color: #ccd6f6; font-size: 0.9rem; margin-top: 4px;">
                        Confidence: <span style="color: {color}; font-weight: bold;">{sd['confidence']}/100</span>
                    </div>
                    <div style="color: #8892b0; font-size: 0.75rem; margin-top: 6px;">
                        {sd['reason']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def show():
    st.markdown("<h1 class='main-header'>📊 Stock Analysis</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-header'>Deep-dive analysis with price charts, technical indicators, and strategy signals</p>",
        unsafe_allow_html=True,
    )

    # Ticker input
    market_key = get_current_market_key()
    market_currency = get_currency(market_key)
    market_tickers = get_display_tickers(market_key)
    default_ticker_val = st.session_state.get("selected_ticker", market_tickers[0])

    col1, col2 = st.columns([2, 4])
    with col1:
        ticker = st.text_input("Ticker Symbol", value=default_ticker_val).strip().upper()
    with col2:
        period = st.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"], index=2)

    if not ticker:
        return

    # Run analysis
    analyze_btn = st.button("🔍 Analyze", type="primary", use_container_width=False)

    if analyze_btn or st.session_state.get("current_ticker") == ticker:
        st.session_state["current_ticker"] = ticker

        with st.spinner(f"Fetching data and analyzing {ticker}..."):
            # Fetch and analyze
            df = fetch_historical(ticker, period=period, interval="1d")
            if df is None or len(df) < 20:
                st.error(f"No data available for {ticker}")
                return

            df = add_all_indicators(df)
            signal = analyze_ticker(ticker)

        if signal:
            # Signal header
            sig_color = "signal-buy" if signal["signal"] == "buy" else "signal-sell"
            st.markdown(
                f"""
                <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                            border: 1px solid #333; border-radius: 12px; padding: 20px; margin: 10px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="font-size: 1.8rem; font-weight: bold; color: #ccd6f6;">{ticker}</span>
                            <span style="font-size: 1.4rem; color: #ffd700; margin-left: 12px;">
                                {market_currency}{signal['price']:.2f}
                            </span>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem;" class="{sig_color}">
                                {signal['signal'].upper()} SIGNAL
                            </div>
                            <div style="color: #8892b0; font-size: 0.85rem;">
                                Score: {signal['consensus_score']}/100
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Key metrics
            cm1, cm2, cm3, cm4, cm5 = st.columns(5)
            cm1.metric("Target", f"{market_currency}{signal['target_price']:.2f}" if signal.get("target_price") else "N/A",
                      f"{signal['potential_return']:+.1f}%" if signal.get("potential_return") else "")
            cm2.metric("Stop Loss", f"{market_currency}{signal['stop_loss']:.2f}" if signal.get("stop_loss") else "N/A")
            cm3.metric("R/R Ratio", f"{signal['risk_reward']:.2f}" if signal.get("risk_reward") else "N/A")
            cm4.metric("Active Strategies", signal.get("active_strategies", 0))
            cm5.metric("ATR", f"{signal.get('atr_percent', 0):.1f}%")

            # Price Chart
            st.markdown("### 📈 Price & Indicators")
            fig = plot_price_chart(df, ticker)
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning(f"No clear signal for {ticker}. The stock may not meet screening criteria or strategies may be neutral.")

        # Always show the chart even without a signal
        if df is not None and len(df) >= 20:
            if not signal:
                st.markdown("### 📈 Price Chart")
                fig = plot_price_chart(df, ticker)
                st.plotly_chart(fig, use_container_width=True)

        # Strategy breakdown
        if signal and signal.get("strategy_detail"):
            st.markdown("### 🎯 Strategy Breakdown")
            display_strategy_breakdown(signal["strategy_detail"])

        # Latest data table
        if df is not None and len(df) >= 5:
            with st.expander("📋 Recent Price Data"):
                recent = df.tail(10).round(2)
                display_cols = ["open", "high", "low", "close", "volume"]
                if "rsi" in recent.columns:
                    display_cols.append("rsi")
                if "atr_percent" in recent.columns:
                    display_cols.append("atr_percent")
                if "ema_9" in recent.columns:
                    display_cols.extend(["ema_9", "ema_21", "ema_50"])

                available = [c for c in display_cols if c in recent.columns]
                st.dataframe(
                    recent[available],
                    use_container_width=True,
                    height=300,
                )
