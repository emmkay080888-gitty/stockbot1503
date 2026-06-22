"""Market Scan page - scan stocks and view consolidated signals."""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import STRATEGY_WEIGHTS
from utils.config_helpers import get_max_stocks, get_min_score
from utils.markets import get_current_market_key, get_market_config, get_currency
from data.universe import get_universe
from signals.generator import analyze_ticker
from signals.consolidator import consolidate_signals, generate_recommendations


def show():
    st.markdown("<h1 class='main-header'>🔍 Market Scan</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-header'>Run scans across stock universes and view consolidated trading signals</p>",
        unsafe_allow_html=True,
    )

    # ─── Scan Controls ────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        market_key = get_current_market_key()
        mkt_cfg = get_market_config(market_key)
        universe_options = list(mkt_cfg["universes"].keys())
        # Get ticker counts for each option
        def _fmt_universe(name):
            key = mkt_cfg["universes"][name]
            tickers = get_universe(key)
            count = len(tickers)
            return f"{name} ({count} stocks)"
        universe = st.selectbox(
            "Stock Universe",
            options=universe_options,
            format_func=_fmt_universe,
            key="scan_universe",
        )
        universe_key = mkt_cfg["universes"][universe]

    with col2:
        max_stocks = st.number_input(
            "Max Stocks",
            min_value=5,
            max_value=500,
            value=get_max_stocks(),
            step=5,
            key="scan_max",
        )

    with col3:
        min_score = st.number_input(
            "Min Score",
            min_value=10,
            max_value=100,
            value=get_min_score(),
            step=5,
            key="scan_min_score",
        )

    with col4:
        workers = st.number_input(
            "Workers",
            min_value=1,
            max_value=10,
            value=5,
            key="scan_workers",
        )

    # ─── Scan Button ──────────────────────────────────────────────
    scan_col1, scan_col2 = st.columns([1, 5])
    with scan_col1:
        scan_clicked = st.button("🚀 Run Scan", type="primary", use_container_width=True)

    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    # ─── Run Scan ─────────────────────────────────────────────────
    if scan_clicked:
        tickers = get_universe(universe_key)
        if max_stocks and len(tickers) > max_stocks:
            tickers = tickers[:max_stocks]

        status_placeholder.info(f"Scanning {len(tickers)} stocks with {workers} workers...")
        progress_bar = progress_placeholder.progress(0.0, text="Initializing...")

        results = [None] * len(tickers)
        completed = 0

        start_time = time.time()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_map = {
                executor.submit(analyze_ticker, ticker): idx
                for idx, ticker in enumerate(tickers)
            }

            for future in as_completed(future_map):
                idx = future_map[future]
                try:
                    results[idx] = future.result()
                except Exception:
                    pass

                completed += 1
                pct = completed / len(tickers)
                progress_bar.progress(pct, text=f"{completed}/{len(tickers)} stocks ({pct*100:.0f}%)")

        duration = time.time() - start_time
        progress_bar.empty()

        # Consolidate
        consolidated = consolidate_signals(results)
        st.session_state["scan_results"] = consolidated
        st.session_state["scan_time"] = duration
        st.session_state["scan_count"] = len(tickers)

        status_placeholder.success(
            f"✅ Scan complete in {duration:.1f}s — found {len(consolidated)} actionable signals "
            f"out of {len(tickers)} stocks scanned"
        )

    # ─── Display Results ──────────────────────────────────────────
    if "scan_results" in st.session_state and st.session_state["scan_results"]:
        consolidated = st.session_state["scan_results"]
        duration = st.session_state.get("scan_time", 0)
        scan_count = st.session_state.get("scan_count", 0)

        # Summary metrics — use dynamic currency
        curr_symbol = get_currency(get_current_market_key())
        buy_count = sum(1 for s in consolidated if s["signal"] == "buy")
        sell_count = sum(1 for s in consolidated if s["signal"] == "sell")
        avg_score = sum(s["consensus_score"] for s in consolidated) / len(consolidated)

        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("📡 Signals Found", len(consolidated))
        m2.metric("🟢 Buy Signals", buy_count)
        m3.metric("🔴 Sell Signals", sell_count)
        m4.metric("⭐ Avg Score", f"{avg_score:.0f}/100")
        m5.metric("⏱️ Scan Time", f"{duration:.1f}s")

        # Build dataframe for display
        rows = []
        for s in consolidated:
            strategies_detail = "<br>".join(
                f"{sd['strategy']}: {sd['signal'].upper()} ({sd['confidence']})"
                for sd in s.get("strategy_detail", [])[:5]
            )
            rows.append({
                "Ticker": s["ticker"],
                "Price": f"{curr_symbol}{s['price']:.2f}",
                "Signal": s["signal"].upper(),
                "Score": s["consensus_score"],
                "Target": f"{curr_symbol}{s['target_price']:.2f}" if s.get("target_price") else "N/A",
                "Stop": f"{curr_symbol}{s['stop_loss']:.2f}" if s.get("stop_loss") else "N/A",
                "Return %": f"{s['potential_return']:+.1f}%" if s.get("potential_return") else "N/A",
                "R/R": f"{s['risk_reward']:.2f}" if s.get("risk_reward") else "N/A",
                "Strategies": s.get("active_strategies", 0),
                "Sector": s.get("sector", "N/A"),
            })

        df = pd.DataFrame(rows)

        # Filters
        st.markdown("### 📋 Signals Table")
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            signal_filter = st.selectbox("Filter by Signal", ["All", "BUY", "SELL"])
        with fcol2:
            min_score_filter = st.slider("Min Score", 0, 100, 30)

        # Price range filter
        if not df.empty and "Price" in df.columns:
            prices = df["Price"].str.replace(curr_symbol, "").astype(float)
            min_p = float(prices.min())
            max_p = float(prices.max())
            default_min = float(prices.quantile(0.1))
            default_max = float(prices.quantile(0.9))
            with fcol3:
                price_range = st.slider(
                    "Price Range ($)",
                    min_value=min_p,
                    max_value=max_p,
                    value=(default_min, default_max),
                    step=1.0,
                    format="$%.0f",
                )
        else:
            price_range = (0, 1000)

        filtered_df = df.copy()
        if signal_filter != "All":
            filtered_df = filtered_df[filtered_df["Signal"] == signal_filter]
        filtered_df = filtered_df[filtered_df["Score"] >= min_score_filter]
        # Apply price range filter
        filtered_df["_price_val"] = filtered_df["Price"].str.replace(curr_symbol, "").astype(float)
        filtered_df = filtered_df[
            (filtered_df["_price_val"] >= price_range[0]) &
            (filtered_df["_price_val"] <= price_range[1])
        ]
        filtered_df = filtered_df.drop(columns=["_price_val"])

        # Clickable ticker column
        st.dataframe(
            filtered_df,
            column_config={
                "Ticker": st.column_config.TextColumn("Ticker", width="small"),
                "Price": st.column_config.TextColumn("Price", width="small"),
                "Signal": st.column_config.TextColumn("Signal", width="small"),
                "Score": st.column_config.ProgressColumn("Score", min_value=0, max_value=100, width="medium"),
                "Target": st.column_config.TextColumn("Target", width="small"),
                "Stop": st.column_config.TextColumn("Stop Loss", width="small"),
                "Return %": st.column_config.TextColumn("Return %", width="small"),
                "R/R": st.column_config.TextColumn("R/R", width="small"),
                "Strategies": st.column_config.NumberColumn("Strategies", width="small"),
                "Sector": st.column_config.TextColumn("Sector", width="medium"),
            },
            use_container_width=True,
            hide_index=True,
            height=400,
        )

        # Ticker selector for deep dive
        st.markdown("### 🔍 Select a ticker for detailed analysis")
        ticker_options = [s["ticker"] for s in consolidated]
        selected = st.selectbox("Go to Stock Analysis", options=ticker_options)
        if selected:
            st.session_state["selected_ticker"] = selected
            st.session_state["current_page"] = "stock_analysis"
            if st.button(f"Analyze {selected}", type="primary"):
                st.rerun()

        # Export
        st.markdown("### 📤 Export")
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name=f"signals_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    elif "scan_results" in st.session_state:
        st.warning("No actionable signals found. Try lowering the minimum score or scanning a larger universe.")
