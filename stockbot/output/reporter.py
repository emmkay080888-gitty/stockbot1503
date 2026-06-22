"""Output and reporting module - CLI display and file export."""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box

from config import OUTPUT_DIR

logger = logging.getLogger(__name__)
console = Console()


def _color_for_score(score: int) -> str:
    """Return color name for a given score."""
    if score >= 80:
        return "green"
    elif score >= 60:
        return "cyan"
    elif score >= 40:
        return "yellow"
    else:
        return "red"


def _signal_icon(signal: str) -> str:
    """Return unicode icon for signal type."""
    if signal == "buy":
        return "▲ BUY"
    elif signal == "sell":
        return "▼ SELL"
    return "● HOLD"


def cli_report_single(signal: dict):
    """Display a detailed single signal analysis."""
    panel_content = []

    # Header
    ticker = signal["ticker"]
    signal_type = signal["signal"]
    score = signal["consensus_score"]
    color = _color_for_score(score)

    header = Text()
    header.append(f"{ticker} ", style="bold white")
    header.append(f"${signal['price']:.2f}", style="bold yellow")
    header.append(f"  {_signal_icon(signal_type)} ", style=color)
    header.append(f"Score: {score}/100", style=f"bold {color}")
    panel_content.append(header)

    # Strategy breakdown
    if signal.get("strategy_detail"):
        strategies = Text("\n\nStrategies:\n", style="underline")
        for s in signal["strategy_detail"]:
            strat_color = "green" if s["signal"] == "buy" else "red"
            strategies.append(
                f"  {s['strategy']:25s} "
                f"[{s['signal'].upper():5s}] "
                f"confidence: {s['confidence']:3d}\n",
                style=strat_color,
            )
        panel_content.append(strategies)

    # Price targets
    if signal.get("target_price"):
        prices = Text("\n")
        prices.append(f"  Target:     ${signal['target_price']:.2f}", style="green")
        prices.append(
            f"  ({signal['potential_return']:+.1f}%)\n", style="bold green"
        )
        prices.append(f"  Stop Loss:  ${signal['stop_loss']:.2f}", style="red")
        prices.append(f"  R/R Ratio:  {signal['risk_reward']:.2f}\n", style="yellow")
        panel_content.append(prices)

    # Metadata
    meta = Text(f"\nATR: {signal.get('atr_percent', 0):.1f}%")
    meta.append(f" | Active Strategies: {signal.get('active_strategies', 0)}")
    if signal.get("sector"):
        meta.append(f" | Sector: {signal['sector']}")
    panel_content.append(meta)

    console.print(Panel(Text.assemble(*panel_content), border_style=color))


def cli_report_summary(consolidated: list[dict], scan_time: float, scanned: int):
    """Display a consolidated summary table of all signals."""
    console.print(
        Panel(
            f"[bold white]Stock Signal Bot - Analysis Report[/bold white]\n"
            f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Scanned {scanned} stocks in {scan_time:.1f}s | "
            f"Found {len(consolidated)} actionable signals[/dim]",
            border_style="blue",
        )
    )

    if not consolidated:
        console.print("[yellow]No actionable signals found in this scan.[/yellow]")
        return

    # Create main table
    table = Table(box=box.ROUNDED, show_lines=True)
    table.add_column("Ticker", style="bold white")
    table.add_column("Price", justify="right", style="yellow")
    table.add_column("Signal", justify="center")
    table.add_column("Score", justify="center")
    table.add_column("Target", justify="right", style="green")
    table.add_column("Stop Loss", justify="right", style="red")
    table.add_column("Return %", justify="right")
    table.add_column("R/R", justify="center")
    table.add_column("Strategies", justify="center")

    for signal in consolidated[:15]:  # Top 15
        ticker = signal["ticker"]
        price = f"${signal['price']:.2f}"
        score = signal["consensus_score"]
        signal_type = signal["signal"]
        icon = _signal_icon(signal_type)
        color = _color_for_score(score)

        target = f"${signal['target_price']:.2f}" if signal.get("target_price") else "N/A"
        stop = f"${signal['stop_loss']:.2f}" if signal.get("stop_loss") else "N/A"
        ret = f"{signal['potential_return']:+.1f}%" if signal.get("potential_return") else "N/A"
        rr = f"{signal['risk_reward']:.1f}" if signal.get("risk_reward") else "N/A"
        strategies = str(signal.get("active_strategies", 0))

        table.add_row(
            ticker,
            price,
            f"[{color}]{icon}[/{color}]",
            f"[{color}]{score}[/{color}]",
            target,
            stop,
            f"[green]{ret}[/green]" if signal["signal"] == "buy" else f"[red]{ret}[/red]",
            f"[yellow]{rr}[/yellow]",
            strategies,
        )

    console.print(table)

    # Summary statistics
    buy_count = sum(1 for s in consolidated if s["signal"] == "buy")
    sell_count = sum(1 for s in consolidated if s["signal"] == "sell")
    avg_score = sum(s["consensus_score"] for s in consolidated) / len(consolidated)
    avg_rr = sum(s.get("risk_reward", 0) for s in consolidated) / len(consolidated)

    summary = Text()
    summary.append(f"\nSummary: ", style="bold")
    summary.append(f"{buy_count} Buy", style="green bold")
    summary.append(f" / {sell_count} Sell", style="red bold")
    summary.append(f" signals | Avg Score: {avg_score:.0f}/100", style="cyan")
    summary.append(f" | Avg R/R: {avg_rr:.2f}", style="yellow")
    summary.append(
        f"\nTarget: Look for trades with score > 65 and R/R > 2.5 for best setups",
        style="dim",
    )
    console.print(summary)


def export_signals_to_json(consolidated: list[dict]) -> Optional[str]:
    """Export signals to a JSON file."""
    if not consolidated:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"signals_{timestamp}.json"
    filepath = OUTPUT_DIR / filename

    # Prepare serializable data
    export_data = []
    for s in consolidated:
        export_data.append(
            {
                "ticker": s["ticker"],
                "price": s["price"],
                "signal": s["signal"],
                "score": s["consensus_score"],
                "target_price": s.get("target_price"),
                "stop_loss": s.get("stop_loss"),
                "potential_return": s.get("potential_return"),
                "risk_reward": s.get("risk_reward"),
                "atr_percent": s.get("atr_percent"),
                "active_strategies": s.get("active_strategies"),
                "strategies": [
                    {
                        "name": sd["strategy"],
                        "signal": sd["signal"],
                        "confidence": sd["confidence"],
                    }
                    for sd in s.get("strategy_detail", [])
                ],
            }
        )

    with open(filepath, "w") as f:
        json.dump(export_data, f, indent=2)

    logger.info(f"Exported {len(export_data)} signals to {filepath}")
    return str(filepath)


def export_signals_to_csv(consolidated: list[dict]) -> Optional[str]:
    """Export signals to a CSV file."""
    if not consolidated:
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"signals_{timestamp}.csv"
    filepath = OUTPUT_DIR / filename

    fieldnames = [
        "ticker",
        "price",
        "signal",
        "score",
        "target_price",
        "stop_loss",
        "potential_return",
        "risk_reward",
        "atr_percent",
        "active_strategies",
    ]

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in consolidated:
            writer.writerow(
                {
                    "ticker": s["ticker"],
                    "price": s["price"],
                    "signal": s["signal"],
                    "score": s["consensus_score"],
                    "target_price": s.get("target_price", ""),
                    "stop_loss": s.get("stop_loss", ""),
                    "potential_return": s.get("potential_return", ""),
                    "risk_reward": s.get("risk_reward", ""),
                    "atr_percent": s.get("atr_percent", ""),
                    "active_strategies": s.get("active_strategies", ""),
                }
            )

    logger.info(f"Exported {len(consolidated)} signals to {filepath}")
    return str(filepath)
