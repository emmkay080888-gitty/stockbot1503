"""Exchange and market definitions.

Primary focus: Indian NSE market.
Legacy US/UK/EU markets kept for backward compatibility.
"""

import streamlit as st

# ── Market Definitions ──────────────────────────────────────────────
# Each market has:
#   key:        Internal key
#   name:       Display name
#   suffix:     Yahoo Finance ticker suffix (empty for US)
#   benchmark:  Benchmark ETF/index ticker
#   emoji:      Flag emoji
#   display_tickers: 12 tickers shown on the landing page ticker
#   universes:  Dict of display_name -> internal_universe_key
#   currencies: Currency symbol

MARKETS = {
    "india": {
        "name": "India (NSE)",
        "suffix": ".NS",
        "benchmark": "^NSEI",
        "emoji": "🇮🇳",
        "currency": "₹",
        "timezone": "Asia/Kolkata",
        "display_tickers": [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS",
            "ICICIBANK.NS", "HINDUNILVR.NS", "ITC.NS", "SBIN.NS",
            "BHARTIARTL.NS", "KOTAKBANK.NS", "BAJFINANCE.NS", "LT.NS",
        ],
        "universes": {
            "Nifty 50": "nifty50",
            "Nifty Next 50": "nifty_next50",
            "Nifty 200": "nifty200",
            "Nifty 500": "nifty500",
            "Nifty Midcap 150": "nifty_midcap150",
            "Nifty Smallcap 250": "nifty_smallcap250",
            "Nifty Mid Small Cap 400": "nifty_midsml400",
            "Nifty Bank": "nifty_bank",
        },
    },
    "us": {
        "name": "US Markets",
        "suffix": "",
        "benchmark": "SPY",
        "emoji": "🇺🇸",
        "currency": "$",
        "timezone": "America/New_York",
        "display_tickers": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META",
            "TSLA", "AMD", "JPM", "V", "WMT", "COST",
        ],
        "universes": {
            "S&P 500": "sp500",
            "NASDAQ 100": "nasdaq100",
            "Watchlist": "watchlist",
        },
    },
    "uk": {
        "name": "UK (LSE)",
        "suffix": ".L",
        "benchmark": "^FTSE",
        "emoji": "🇬🇧",
        "currency": "£",
        "timezone": "Europe/London",
        "display_tickers": [
            "HSBA.L", "BP.L", "SHEL.L", "GSK.L", "AZN.L", "DGE.L",
            "ULVR.L", "RIO.L", "BARC.L", "LLOY.L", "PRU.L", "VOD.L",
        ],
        "universes": {
            "FTSE 100": "ftse100",
        },
    },
    "europe": {
        "name": "Europe (Xetra)",
        "suffix": ".DE",
        "benchmark": "^STOXX50E",
        "emoji": "🇪🇺",
        "currency": "€",
        "timezone": "Europe/Berlin",
        "display_tickers": [
            "SAP.DE", "AIR.PA", "MC.PA", "OR.PA", "SIE.DE",
            "ALV.DE", "BN.PA", "BMW.DE", "VOW3.DE", "BAS.DE", "BAYN.DE", "ADS.DE",
        ],
        "universes": {
            "Euro Stoxx 50": "euro50",
        },
    },
}


def get_market_list() -> list[dict]:
    """Return all available markets as a list of dicts for display."""
    return [
        {
            "key": k,
            "label": f"{m['emoji']} {m['name']}",
            "suffix": m["suffix"],
            "benchmark": m["benchmark"],
            "currency": m["currency"],
        }
        for k, m in MARKETS.items()
    ]


def get_default_market() -> str:
    """Return the default market key (India / NSE)."""
    return "india"


def get_current_market_key() -> str:
    """Get the currently selected market from session state."""
    if "selected_market" not in st.session_state:
        st.session_state["selected_market"] = get_default_market()
    return st.session_state["selected_market"]


def set_market(market_key: str):
    """Set the selected market in session state."""
    if market_key in MARKETS:
        st.session_state["selected_market"] = market_key


def get_market_config(market_key: str | None = None) -> dict:
    """Get the full config for a market (current if not specified)."""
    if market_key is None:
        market_key = get_current_market_key()
    return MARKETS.get(market_key, MARKETS["india"])


def get_ticker_suffix(market_key: str | None = None) -> str:
    """Get the Yahoo Finance ticker suffix for a market."""
    return get_market_config(market_key)["suffix"]


def get_display_tickers(market_key: str | None = None) -> list[str]:
    """Get the tickers for the landing page ticker display."""
    return get_market_config(market_key)["display_tickers"]


def get_benchmark(market_key: str | None = None) -> str:
    """Get the benchmark ticker for a market."""
    return get_market_config(market_key)["benchmark"]


def get_currency(market_key: str | None = None) -> str:
    """Get the currency symbol for a market."""
    return get_market_config(market_key)["currency"]


def get_timezone(market_key: str | None = None) -> str:
    """Get the IANA timezone string for a market (e.g. Asia/Kolkata, America/New_York)."""
    return get_market_config(market_key)["timezone"]


def get_market_context(market_key: str | None = None) -> str:
    """Get a short human-readable market context string (emoji + name + currency + timezone)."""
    cfg = get_market_config(market_key)
    return f"{cfg['emoji']} {cfg['name']} · {cfg['currency']} · {cfg['timezone']}"


def apply_suffix(ticker: str, market_key: str | None = None) -> str:
    """Apply the Yahoo Finance suffix to a ticker (e.g., RELIANCE -> RELIANCE.NS).
    Does NOT double-apply suffix if it already has one or has a ^ prefix.
    """
    if "." in ticker or "^" in ticker:
        return ticker
    suffix = get_ticker_suffix(market_key)
    return ticker + suffix
