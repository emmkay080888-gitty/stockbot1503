"""Backtesting module - validates trading strategies against historical data.

Simulates trades based on generated signals to estimate potential
win rate, average return, and number of profitable trades.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import numpy as np

from config import STRATEGY_WEIGHTS
from data.fetcher import fetch_historical
from analysis.indicators import add_all_indicators
from analysis.strategies import run_all_strategies

logger = logging.getLogger(__name__)


def simulate_trade(
    df: pd.DataFrame,
    signal_idx: int,
    signal_type: str,
    holding_period: int = 10,
    stop_loss_pct: float = 5.0,
    target_pct: float = 10.0,
) -> dict:
    """Simulate a single trade from a signal.

    Args:
        df: Full dataframe with indicators.
        signal_idx: Index in df where the signal occurred.
        signal_type: 'buy' or 'sell'.
        holding_period: Max days to hold (default 10 trading days ~ 2 weeks).
        stop_loss_pct: Stop loss percentage from entry.
        target_pct: Target profit percentage.

    Returns:
        Dict with trade outcome details.
    """
    if signal_idx >= len(df) - 1:
        return {"result": "error", "return_pct": 0, "reason": "No forward data"}

    entry_price = df.iloc[signal_idx]["close"]
    exit_idx = min(signal_idx + holding_period, len(df) - 1)
    exit_price = df.iloc[exit_idx]["close"]

    best_price = entry_price
    worst_price = entry_price
    peak_return = 0.0
    max_drawdown = 0.0
    stop_hit = False
    target_hit = False

    # Walk forward day by day to check stops and targets
    for i in range(signal_idx + 1, exit_idx + 1):
        daily_high = df.iloc[i]["high"]
        daily_low = df.iloc[i]["low"]
        daily_close = df.iloc[i]["close"]

        if signal_type == "buy":
            # Check stop loss (intraday)
            if daily_low <= entry_price * (1 - stop_loss_pct / 100):
                exit_price = entry_price * (1 - stop_loss_pct / 100)
                exit_idx = i
                stop_hit = True
                break

            # Check target (intraday)
            if daily_high >= entry_price * (1 + target_pct / 100):
                exit_price = entry_price * (1 + target_pct / 100)
                exit_idx = i
                target_hit = True
                break

            # Track peak return
            daily_return = (daily_close - entry_price) / entry_price * 100
            peak_return = max(peak_return, daily_return)
            max_drawdown = min(max_drawdown, daily_return)

        else:  # sell
            if daily_high >= entry_price * (1 + stop_loss_pct / 100):
                exit_price = entry_price * (1 + stop_loss_pct / 100)
                exit_idx = i
                stop_hit = True
                break

            if daily_low <= entry_price * (1 - target_pct / 100):
                exit_price = entry_price * (1 - target_pct / 100)
                exit_idx = i
                target_hit = True
                break

            daily_return = (entry_price - daily_close) / entry_price * 100
            peak_return = max(peak_return, daily_return)
            max_drawdown = min(max_drawdown, daily_return)

    # Calculate actual return
    if signal_type == "buy":
        actual_return = (exit_price - entry_price) / entry_price * 100
    else:
        actual_return = (entry_price - exit_price) / entry_price * 100

    holding_days = exit_idx - signal_idx

    return {
        "entry_price": round(entry_price, 2),
        "exit_price": round(exit_price, 2),
        "return_pct": round(actual_return, 2),
        "holding_days": holding_days,
        "peak_return": round(peak_return, 2),
        "max_drawdown": round(max_drawdown, 2),
        "stop_hit": stop_hit,
        "target_hit": target_hit,
        "result": "win" if actual_return > 0 else "loss",
    }


def backtest_ticker(
    ticker: str,
    lookback_months: int = 12,
    signal_interval_days: int = 5,
    min_signal_score: int = 40,
) -> list[dict]:
    """Backtest strategies on a single ticker over historical data.

    Walks through historical data, generating signals at intervals,
    then simulates trades to measure performance.

    Args:
        ticker: Stock ticker symbol.
        lookback_months: Months of historical data to use.
        signal_interval_days: Days between signal checks.
        min_signal_score: Minimum consensus score to take a trade.
        holding_period: Max days to hold a position.

    Returns:
        List of trade result dicts.
    """
    # Fetch longer history
    df = fetch_historical(ticker, period=f"{lookback_months}mo", interval="1d")

    if df is None or len(df) < 60:
        logger.debug(f"{ticker}: insufficient history for backtest ({len(df) if df is not None else 0} rows)")
        return []

    # Add indicators
    df = add_all_indicators(df)
    if df is None or len(df) < 60:
        return []

    trades = []

    # Calculate adaptive loop bounds based on available data
    # Need: buffer for indicator calculation + room for forward trade simulation
    min_data_buffer = 50         # minimum rows needed for indicator warmup
    forward_buffer = 10          # minimum forward rows needed for trade simulation

    start_idx = min(60, max(min_data_buffer, len(df) - forward_buffer - signal_interval_days))
    end_idx = len(df) - forward_buffer

    if end_idx <= start_idx:
        logger.debug(f"{ticker}: insufficient data for backtest ({len(df)} rows, would need {start_idx + forward_buffer + 1}+)")
        return []

    last_signal_idx = -signal_interval_days

    # Walk through history, generating signals every N days
    for i in range(start_idx, end_idx, signal_interval_days):
        # Create a slice that ends at position i (simulates "current" data)
        window = df.iloc[: i + 1].copy()

        if len(window) < 50:
            continue

        # Run strategies on this window
        strategy_results = run_all_strategies(window)

        # Filter for non-neutral signals
        active = [s for s in strategy_results if s["signal"] != "neutral"]

        if not active:
            continue

        # Weighted consensus (simplified version for backtest)
        buy_weighted = sum(
            s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0)
            for s in active
            if s["signal"] == "buy"
        )
        sell_weighted = sum(
            s["confidence"] * STRATEGY_WEIGHTS.get(s["strategy"], 1.0)
            for s in active
            if s["signal"] == "sell"
        )
        total_weight = sum(
            STRATEGY_WEIGHTS.get(s["strategy"], 1.0)
            for s in active
        )

        if total_weight == 0:
            continue

        if buy_weighted > sell_weighted:
            score = int((buy_weighted / total_weight) * 100)
            signal_type = "buy"
        elif sell_weighted > buy_weighted:
            score = int((sell_weighted / total_weight) * 100)
            signal_type = "sell"
        else:
            continue

        if score < min_signal_score:
            continue

        # Simulate trade
        trade = simulate_trade(df, i, signal_type)

        if trade["result"] != "error":
            trade["ticker"] = ticker
            trade["signal_score"] = score
            trade["signal_date"] = df.index[i].strftime("%Y-%m-%d")
            trade["signal_type"] = signal_type
            trade["strategies_triggered"] = len(active)
            trades.append(trade)

    return trades


def run_backtest(
    tickers: list[str],
    lookback_months: int = 12,
    min_score: int = 40,
) -> dict:
    """Run backtest on a list of tickers.

    Returns:
        Dict with backtest results, performance stats, and trade details.
    """
    all_trades = []
    tickers_with_signals = 0

    for ticker in tickers:
        trades = backtest_ticker(
            ticker,
            lookback_months=lookback_months,
            min_signal_score=min_score,
        )
        if trades:
            tickers_with_signals += 1
            all_trades.extend(trades)

        logger.info(
            f"{ticker}: {len(trades)} backtest trades"
        )

    if not all_trades:
        return {
            "total_trades": 0,
            "win_rate": 0,
            "avg_return": 0,
            "profitable_trades": 0,
            "trades_over_10pct": 0,
            "summary": "No backtest trades generated",
            "trades": [],
        }

    # Calculate performance stats
    df_trades = pd.DataFrame(all_trades)
    wins = df_trades[df_trades["result"] == "win"]
    losses = df_trades[df_trades["result"] == "loss"]

    win_rate = len(wins) / len(df_trades) * 100 if len(df_trades) > 0 else 0
    avg_return = df_trades["return_pct"].mean()
    profitable_trades = len(df_trades[df_trades["return_pct"] > 0])
    trades_over_10pct = len(df_trades[df_trades["return_pct"] >= 10])

    # Top profitable trades (for the "5 trades with 10%+" requirement)
    top_trades = (
        df_trades[df_trades["return_pct"] >= 10]
        .nlargest(10, "return_pct")
        .to_dict("records")
    )

    return {
        "total_trades": len(df_trades),
        "win_rate": round(win_rate, 1),
        "avg_return": round(avg_return, 2),
        "avg_win": round(wins["return_pct"].mean(), 2) if len(wins) > 0 else 0,
        "avg_loss": round(losses["return_pct"].mean(), 2) if len(losses) > 0 else 0,
        "profitable_trades": profitable_trades,
        "trades_over_10pct": trades_over_10pct,
        "best_trade": round(df_trades["return_pct"].max(), 2),
        "worst_trade": round(df_trades["return_pct"].min(), 2),
        "avg_holding_days": round(df_trades["holding_days"].mean(), 1),
        "tickers_with_signals": tickers_with_signals,
        "summary": (
            f"Backtested {len(tickers)} tickers over {lookback_months} months. "
            f"Generated {len(df_trades)} trades across {tickers_with_signals} tickers. "
            f"Win rate: {win_rate:.1f}%. "
            f"Avg return: {avg_return:.2f}%. "
            f"{profitable_trades} profitable trades, "
            f"{trades_over_10pct} trades with 10%+ return."
        ),
        "trades": sorted(
            all_trades, key=lambda t: t["return_pct"], reverse=True
        ),
    }


def print_backtest_report(results: dict):
    """Print a formatted backtest report."""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text

    console = Console()

    if results["total_trades"] == 0:
        console.print("[yellow]No backtest trades generated.[/yellow]")
        return

    # Header
    console.print(
        Panel(
            f"[bold white]Backtest Report[/bold white]\n"
            f"{results['summary']}",
            border_style="cyan",
        )
    )

    # Stats table
    stats = Table(title="Performance Summary", show_lines=True)
    stats.add_column("Metric", style="bold")
    stats.add_column("Value", justify="right")

    stats.add_row("Total Trades", str(results["total_trades"]))
    stats.add_row("Win Rate", f"{results['win_rate']}%")
    stats.add_row("Avg Return", f"{results['avg_return']}%")
    stats.add_row("Avg Win", f"+{results['avg_win']}%")
    stats.add_row("Avg Loss", f"{results['avg_loss']}%")
    stats.add_row("Profitable Trades", str(results["profitable_trades"]))
    stats.add_row("Trades ≥ 10% Return", f"[green bold]{results['trades_over_10pct']}[/green bold]")
    stats.add_row("Best Trade", f"+{results['best_trade']}%")
    stats.add_row("Worst Trade", f"{results['worst_trade']}%")
    stats.add_row("Avg Holding Period", f"{results['avg_holding_days']} days")
    stats.add_row("Tickers with Signals", str(results["tickers_with_signals"]))

    console.print(stats)

    # Top trades table
    top_trades = [t for t in results["trades"] if t["return_pct"] >= 10][:10]
    if top_trades:
        tt = Table(title=f"Top {len(top_trades)} Trades with ≥10% Return", show_lines=True)
        tt.add_column("Ticker", style="bold")
        tt.add_column("Date")
        tt.add_column("Direction")
        tt.add_column("Return %", justify="right")
        tt.add_column("Holding", justify="right")
        tt.add_column("Score", justify="right")
        tt.add_column("Strategies", justify="center")

        for t in top_trades[:10]:
            direction = "[green]BUY[/green]" if t.get("signal_type") == "buy" else "[red]SELL[/red]"
            ret_style = "green" if t["return_pct"] > 0 else "red"
            tt.add_row(
                t.get("ticker", "N/A"),
                t.get("signal_date", "N/A"),
                direction,
                f"[{ret_style}]{t['return_pct']:+.1f}%[/{ret_style}]",
                f"{t['holding_days']}d",
                str(t.get("signal_score", "N/A")),
                str(t.get("strategies_triggered", "N/A")),
            )

        console.print(tt)

    # Assessment
    meets_target = results["trades_over_10pct"] >= 5
    assessment = Text()
    assessment.append("\nAssessment: ", style="bold")
    if meets_target:
        assessment.append(
            f"✓ PASS - System generated {results['trades_over_10pct']} trades "
            f"with ≥10% return (target: 5)",
            style="green bold",
        )
    else:
        assessment.append(
            f"✗ System generated {results['trades_over_10pct']} trades "
            f"with ≥10% return (target: 5)",
            style="yellow bold",
        )

    assessment.append(
        f"\nNote: Backtest results are hypothetical and do not represent "
        f"actual trading. Past performance does not guarantee future results.",
        style="dim",
    )
    console.print(assessment)
