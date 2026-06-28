#!/usr/bin/env python3
"""Stock Signal Bot - Main Entry Point.

Usage:
    python main.py scan [--universe sp500] [--max-stocks 50] [--min-score 40]
    python main.py watchlist [--min-score 40]
    python main.py tickers AAPL,MSFT,GOOGL [--min-score 40]
    python main.py backtest [--universe watchlist] [--months 12] [--min-score 40]
    python main.py backtest --tickers AAPL,MSFT,TSLA
"""

import argparse
import logging
import time
import sys
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional

from config import MAX_STOCKS_TO_SCAN, MIN_SIGNAL_SCORE
from data.universe import get_universe
from signals.generator import analyze_ticker
from signals.consolidator import consolidate_signals, generate_recommendations
from output.reporter import (
    cli_report_summary,
    export_signals_to_json,
    export_signals_to_csv,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("stockbot")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Stock Signal Bot - Multi-strategy signal consolidation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- scan command ---
    scan_parser = subparsers.add_parser("scan", help="Scan a universe for signals")
    scan_parser.add_argument(
        "--universe", type=str, default="sp500",
        choices=["sp500", "nasdaq100", "watchlist"],
        help="Stock universe to scan (default: sp500)",
    )
    scan_parser.add_argument(
        "--max-stocks", type=int, default=MAX_STOCKS_TO_SCAN,
        help=f"Max stocks to scan (default: {MAX_STOCKS_TO_SCAN})",
    )
    scan_parser.add_argument(
        "--min-score", type=int, default=MIN_SIGNAL_SCORE,
        help=f"Minimum signal score (default: {MIN_SIGNAL_SCORE})",
    )
    scan_parser.add_argument(
        "--workers", type=int, default=5,
        help="Parallel workers (default: 5)",
    )
    scan_parser.add_argument("--no-json", action="store_true", help="Skip JSON export")
    scan_parser.add_argument("--no-csv", action="store_true", help="Skip CSV export")

    # --- watchlist command ---
    wl_parser = subparsers.add_parser("watchlist", help="Scan predefined watchlist")
    wl_parser.add_argument("--min-score", type=int, default=MIN_SIGNAL_SCORE)
    wl_parser.add_argument("--workers", type=int, default=5)
    wl_parser.add_argument("--no-json", action="store_true")
    wl_parser.add_argument("--no-csv", action="store_true")

    # --- tickers command ---
    tk_parser = subparsers.add_parser("tickers", help="Scan specific tickers")
    tk_parser.add_argument("tickers", type=str, help="Comma-separated tickers")
    tk_parser.add_argument("--min-score", type=int, default=MIN_SIGNAL_SCORE)
    tk_parser.add_argument("--workers", type=int, default=5)
    tk_parser.add_argument("--no-json", action="store_true")
    tk_parser.add_argument("--no-csv", action="store_true")

    # --- backtest command ---
    bt_parser = subparsers.add_parser("backtest", help="Backtest strategies on historical data")
    bt_parser.add_argument(
        "--universe", type=str, default="watchlist",
        choices=["sp500", "nasdaq100", "watchlist"],
        help="Stock universe to backtest (default: watchlist)",
    )
    bt_parser.add_argument("--tickers", type=str, default=None, help="Comma-separated tickers")
    bt_parser.add_argument("--months", type=int, default=12, help="Months of history (default: 12)")
    bt_parser.add_argument("--min-score", type=int, default=40)
    bt_parser.add_argument("--max-stocks", type=int, default=30)
    bt_parser.add_argument("--workers", type=int, default=3)

    # Global args
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")

    # For backward compatibility (no subcommand)
    parser.add_argument("--universe", dest="legacy_universe", help=argparse.SUPPRESS)
    parser.add_argument("--watchlist", action="store_true", dest="legacy_watchlist", help=argparse.SUPPRESS)
    parser.add_argument("--tickers", dest="legacy_tickers", help=argparse.SUPPRESS)
    parser.add_argument("--max-stocks", dest="legacy_max_stocks", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--min-score", dest="legacy_min_score", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--no-json", dest="legacy_no_json", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--no-csv", dest="legacy_no_csv", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--workers", dest="legacy_workers", type=int, help=argparse.SUPPRESS)

    return parser.parse_args()


def scan_tickers(tickers: list[str], max_workers: int = 5) -> list[Optional[dict]]:
    """Scan a list of tickers in parallel and return analysis results."""
    total = len(tickers)
    results = [None] * total
    completed = 0

    logger.info(f"Scanning {total} tickers with {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(analyze_ticker, ticker): idx
            for idx, ticker in enumerate(tickers)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                results[idx] = future.result()
            except Exception as e:
                logger.error(f"Worker error on {tickers[idx]}: {e}")

            completed += 1
            if completed % 10 == 0 or completed == total:
                pct = (completed / total) * 100
                logger.info(f"Progress: {completed}/{total} ({pct:.0f}%)")

    return results


def cmd_scan(args):
    """Run a scan command."""
    tickers = get_universe(args.universe)

    if args.max_stocks and len(tickers) > args.max_stocks:
        logger.info(f"Limiting scan from {len(tickers)} to {args.max_stocks} stocks")
        tickers = tickers[: args.max_stocks]

    logger.info(
        f"Scanning {len(tickers)} tickers from '{args.universe}' "
        f"(min score: {args.min_score}, workers: {args.workers})"
    )

    start = time.time()
    results = scan_tickers(tickers, max_workers=args.workers)
    duration = time.time() - start

    consolidated = consolidate_signals(results)
    cli_report_summary(consolidated, duration, len(tickers))

    exports = []
    if not args.no_json:
        p = export_signals_to_json(consolidated)
        if p: exports.append(p)
    if not args.no_csv:
        p = export_signals_to_csv(consolidated)
        if p: exports.append(p)

    if exports:
        print(f"\n📁 Reports:")
        for p in exports:
            print(f"   • {p}")

    if consolidated:
        recs = generate_recommendations(consolidated)
        top_buys = [r for r in recs if r["action"] == "BUY"][:5]
        if top_buys:
            print(f"\n{'='*60}")
            print(f"  TOP {len(top_buys)} BUY SIGNALS")
            print(f"{'='*60}")
            for i, rec in enumerate(top_buys, 1):
                print(f"\n  {i}. {rec['ticker']} @ ${rec['entry_price']:.2f}")
                print(f"     Confidence: {rec['confidence']}/100 | R/R: {rec['risk_reward']:.2f}")
                print(f"     Target: ${rec['target_price']:.2f} ({rec['potential_return']:+.1f}%)")
                print(f"     Stop:   ${rec['stop_loss']:.2f}")
                print(f"     Position: {rec['position_size']}")

    print(f"\n✅ Scan complete in {duration:.1f}s")


def cmd_watchlist(args):
    """Run a watchlist scan."""
    args.universe = "watchlist"
    cmd_scan(args)


def cmd_tickers(args):
    """Run a scan on specific tickers."""
    tickers = [t.strip().upper() for t in args.tickers.split(",")]
    args.universe = f"custom ({len(tickers)} tickers)"
    args.max_stocks = len(tickers)
    _original_scan = scan_tickers

    # Override tickers directly
    start = time.time()
    results = scan_tickers(tickers, max_workers=args.workers)
    duration = time.time() - start

    consolidated = consolidate_signals(results)
    cli_report_summary(consolidated, duration, len(tickers))

    exports = []
    if not args.no_json:
        p = export_signals_to_json(consolidated)
        if p: exports.append(p)
    if not args.no_csv:
        p = export_signals_to_csv(consolidated)
        if p: exports.append(p)

    if exports:
        print(f"\n📁 Reports:")
        for p in exports:
            print(f"   • {p}")

    if consolidated:
        recs = generate_recommendations(consolidated)
        top_buys = [r for r in recs if r["action"] == "BUY"][:5]
        if top_buys:
            print(f"\n{'='*60}")
            print(f"  TOP {len(top_buys)} BUY SIGNALS")
            print(f"{'='*60}")
            for i, rec in enumerate(top_buys, 1):
                print(f"\n  {i}. {rec['ticker']} @ ${rec['entry_price']:.2f}")
                print(f"     Confidence: {rec['confidence']}/100 | R/R: {rec['risk_reward']:.2f}")
                print(f"     Target: ${rec['target_price']:.2f} ({rec['potential_return']:+.1f}%)")
                print(f"     Stop:   ${rec['stop_loss']:.2f}")
                print(f"     Position: {rec['position_size']}")

    print(f"\n✅ Scan complete in {duration:.1f}s")


def cmd_backtest(args):
    """Run a backtest command."""
    from analysis.backtest import run_backtest, print_backtest_report

    if args.tickers:
        tickers = [t.strip().upper() for t in args.tickers.split(",")]
    else:
        tickers = get_universe(args.universe)
        if args.max_stocks and len(tickers) > args.max_stocks:
            tickers = tickers[: args.max_stocks]

    logger.info(
        f"Running backtest on {len(tickers)} tickers "
        f"({args.months} months history, min score: {args.min_score})"
    )

    start = time.time()
    results = run_backtest(
        tickers,
        lookback_months=args.months,
        min_score=args.min_score,
    )
    duration = time.time() - start

    print(f"\n{'='*60}")
    print(f"  BACKTEST RESULTS ({duration:.0f}s)")
    print(f"{'='*60}")
    print_backtest_report(results)


def main():
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Route to command handler
    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "watchlist":
        cmd_watchlist(args)
    elif args.command == "tickers":
        cmd_tickers(args)
    elif args.command == "backtest":
        cmd_backtest(args)
    else:
        # Legacy mode - no subcommand given
        print("Stock Signal Bot")
        print("=" * 40)
        print("\nUsage: python main.py <command> [options]")
        print("\nCommands:")
        print("  scan       Scan a stock universe for trading signals")
        print("  watchlist  Scan the predefined watchlist")
        print("  tickers    Scan specific tickers (comma-separated)")
        print("  backtest   Backtest strategies on historical data")
        print("\nExamples:")
        print("  python main.py scan --universe sp500 --max-stocks 50")
        print("  python main.py watchlist")
        print("  python main.py tickers AAPL,MSFT,TSLA")
        print("  python main.py backtest --universe watchlist --months 6")
        sys.exit(0)


if __name__ == "__main__":
    main()
