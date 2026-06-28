"""Backtest page - run backtests, view performance stats and trade history."""

import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import STRATEGY_WEIGHTS
from utils.config_helpers import get_min_score, get_max_stocks
from utils.markets import get_current_market_key, get_market_config, get_currency
from data.universe import get_universe
from analysis.backtest import run_backtest


def plot_backtest_results(results: dict):
    """Create visualizations for backtest results."""
    trades = results.get("trades", [])
    if not trades:
        return None

    df_trades = pd.DataFrame(trades)

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Return Distribution", "Returns by Date",
                        "Win vs Loss", "Score vs Return"),
        vertical_spacing=0.12,
        horizontal_spacing=0.15,
        specs=[
            [{"type": "xy"}, {"type": "xy"}],
            [{"type": "domain"}, {"type": "xy"}],
        ],
    )

    # Return distribution
    fig.add_trace(
        go.Histogram(
            x=df_trades["return_pct"],
            nbinsx=20,
            marker_color=["#00ff88" if r > 0 else "#ff4444" for r in df_trades["return_pct"]],
            name="Return Distribution",
            opacity=0.75,
        ),
        row=1, col=1,
    )

    # Returns by date
    if "signal_date" in df_trades.columns:
        df_dates = df_trades.copy()
        df_dates["date"] = pd.to_datetime(df_dates["signal_date"])
        df_dates = df_dates.sort_values("date")

        colors = ["#00ff88" if r > 0 else "#ff4444" for r in df_dates["return_pct"]]
        fig.add_trace(
            go.Bar(
                x=df_dates["date"],
                y=df_dates["return_pct"],
                marker_color=colors,
                name="Trade Returns",
                opacity=0.7,
            ),
            row=1, col=2,
        )
        fig.add_hline(y=10, line_dash="dash", line_color="#ffd700", opacity=0.5,
                      annotation_text="10% Target", row=1, col=2)

    # Score vs Return scatter (added before Pie to avoid Plotly bug with add_hline on mixed subplots)
    if "signal_score" in df_trades.columns:
        colors = ["#00ff88" if r > 0 else "#ff4444" for r in df_trades["return_pct"]]
        fig.add_trace(
            go.Scatter(
                x=df_trades["signal_score"],
                y=df_trades["return_pct"],
                mode="markers",
                marker=dict(color=colors, size=8, opacity=0.7),
                text=df_trades.get("ticker", ""),
                hovertemplate="Score: %{x}<br>Return: %{y:.1f}%<br>Ticker: %{text}",
                name="Trades",
            ),
            row=2, col=2,
        )
        fig.add_hline(y=10, line_dash="dash", line_color="#ffd700", opacity=0.5, row=2, col=2)

    # Win vs Loss pie (added after xy traces to avoid Plotly bug with add_hline on mixed subplots)
    win_count = len(df_trades[df_trades["return_pct"] > 0])
    loss_count = len(df_trades[df_trades["return_pct"] <= 0])
    fig.add_trace(
        go.Pie(
            labels=["Wins", "Losses"],
            values=[win_count, loss_count],
            marker_colors=["#00ff88", "#ff4444"],
            textinfo="label+percent",
            hovertemplate="%{label}: %{value} trades<br>%{percent}",
        ),
        row=2, col=1,
    )

    fig.update_layout(
        template="plotly_dark",
        height=600,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
    )

    return fig


def show():
    st.markdown("<h1 class='main-header'>🔄 Backtest</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-header'>Validate trading strategies against historical data to estimate performance</p>",
        unsafe_allow_html=True,
    )

    # ─── Backtest Controls ────────────────────────────────────────
    market_key = get_current_market_key()
    mkt_cfg = get_market_config(market_key)
    universe_options = list(mkt_cfg["universes"].keys())
    def _fmt_bt_universe(name):
        key = mkt_cfg["universes"][name]
        count = len(get_universe(key))
        return f"{name} ({count} stocks)"

    curr_symbol = get_currency(get_current_market_key())

    col1, col2, col3 = st.columns(3)
    with col1:
        universe = st.selectbox(
            "Universe",
            options=universe_options,
            format_func=_fmt_bt_universe,
            key="bt_universe",
        )
        universe_key = mkt_cfg["universes"][universe]
    with col2:
        lookback_months = st.selectbox(
            "Lookback Period",
            options=[3, 6, 12, 24],
            format_func=lambda x: f"{x} months",
            index=2,
            key="bt_months",
        )
    with col3:
        min_score = st.number_input(
            "Min Signal Score",
            min_value=10,
            max_value=100,
            value=get_min_score(),
            step=5,
            key="bt_min_score",
        )

    col1, col2 = st.columns(2)
    with col1:
        max_stocks = st.number_input(
            "Max Stocks to Test",
            min_value=5,
            max_value=200,
            value=get_max_stocks(),
            step=5,
            key="bt_max",
        )

    # ─── Run Button ───────────────────────────────────────────────
    run_btn = st.button("🔄 Run Backtest", type="primary", use_container_width=True)
    status_placeholder = st.empty()

    # ─── Execute Backtest ─────────────────────────────────────────
    if run_btn:
        tickers = get_universe(universe_key)
        if max_stocks and len(tickers) > max_stocks:
            tickers = tickers[:max_stocks]

        status_placeholder.info(f"Running backtest on {len(tickers)} tickers over {lookback_months} months...")
        progress_bar = st.progress(0.0, text="Starting...")

        start_time = time.time()

        # Run backtest
        results = run_backtest(tickers, lookback_months=lookback_months, min_score=min_score)

        duration = time.time() - start_time
        progress_bar.empty()

        st.session_state["backtest_results"] = results
        st.session_state["backtest_duration"] = duration

        status_placeholder.success(f"✅ Backtest complete in {duration:.0f}s")

    # ─── Display Results ──────────────────────────────────────────
    if "backtest_results" in st.session_state:
        results = st.session_state["backtest_results"]
        duration = st.session_state.get("backtest_duration", 0)

        if results["total_trades"] == 0:
            st.warning("No trades generated. Try a larger universe or lower minimum score.")
            return

        # Summary header
        total = results["total_trades"]
        win_rate = results["win_rate"]
        avg_ret = results["avg_return"]
        over_10 = results["trades_over_10pct"]

        meets_target = over_10 >= 5
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                        border: 1px solid {'#00ff88' if meets_target else '#ffd700'}44;
                        border-radius: 12px; padding: 20px; margin: 10px 0;">
                <div style="font-size: 1.1rem; font-weight: bold; color: #ccd6f6;">
                    Backtest Results — {total} trades across {results['tickers_with_signals']} tickers
                </div>
                <div style="color: #8892b0; font-size: 0.85rem; margin-top: 4px;">
                    {results['summary']}
                </div>
                <div style="margin-top: 8px; font-size: 0.95rem;">
                    Target: 5 trades with ≥10% return →
                    <span style="color: {'#00ff88' if meets_target else '#ffd700'}; font-weight: bold;">
                        {'✓ ACHIEVED' if meets_target else f'{over_10}/5 so far'}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Performance metrics
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Total Trades", results["total_trades"])
        m2.metric("Win Rate", f"{win_rate:.1f}%")
        m3.metric("Avg Return", f"{avg_ret:.2f}%")
        m4.metric("Avg Win", f"+{results['avg_win']:.2f}%")
        m5.metric("Avg Loss", f"{results['avg_loss']:.2f}%")
        m6.metric("Best Trade", f"+{results['best_trade']:.1f}%")

        # Charts
        st.markdown("### 📊 Visualizations")
        fig = plot_backtest_results(results)
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Trade History Table
        st.markdown("### 📋 Trade History")
        trades = results.get("trades", [])
        if trades:
            df_trades = pd.DataFrame(trades)
            display_cols = ["ticker", "signal_date", "signal_type", "signal_score",
                           "return_pct", "holding_days", "strategies_triggered",
                           "entry_price", "exit_price"]
            available = [c for c in display_cols if c in df_trades.columns]

            display_df = df_trades[available].copy()

            # Rename columns
            rename_map = {
                "ticker": "Ticker", "signal_date": "Date", "signal_type": "Direction",
                "signal_score": "Score", "return_pct": "Return %",
                "holding_days": "Holding", "strategies_triggered": "Strategies",
                "entry_price": f"Entry ({curr_symbol})", "exit_price": f"Exit ({curr_symbol})",
            }
            display_df = display_df.rename(columns={k: v for k, v in rename_map.items() if k in display_df.columns})

            st.dataframe(
                display_df,
                column_config={
                    "Return %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Score": st.column_config.NumberColumn(format="%d"),
                },
                use_container_width=True,
                hide_index=True,
                height=400,
            )

        # Export
        if trades:
            csv_data = df_trades.to_csv(index=False)
            st.download_button(
                "📥 Download Trade History CSV",
                data=csv_data,
                file_name=f"backtest_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )

        # Performance by ticker
        st.markdown("### 📈 Best Performing Tickers")
        if trades:
            ticker_stats = df_trades.groupby("ticker").agg(
                Trades=("return_pct", "count"),
                Avg_Return=("return_pct", "mean"),
                Best=("return_pct", "max"),
                Win_Rate=("result", lambda x: (x == "win").mean() * 100),
            ).round(2)
            ticker_stats = ticker_stats.sort_values("Avg_Return", ascending=False)
            st.dataframe(ticker_stats, use_container_width=True)
