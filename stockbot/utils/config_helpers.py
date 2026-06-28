"""Configuration helpers — checks session state overrides before falling back to config.py.

All config values (strategy weights, TA params, screening filters, min score, max stocks)
can be overridden via Streamlit session state from the Settings page.
Values persist for the duration of the browser session.
"""

import streamlit as st
from config import (
    STRATEGY_WEIGHTS as _BASE_WEIGHTS,
    SCREENING as _BASE_SCREENING,
    TA_PARAMS as _BASE_TA_PARAMS,
    MIN_SIGNAL_SCORE as _BASE_MIN_SCORE,
    MAX_STOCKS_TO_SCAN as _BASE_MAX_STOCKS,
)

# ─── Keys used in session state ───────────────────────────────────
_SESSION_PREFIX = "settings_"

_KEYS = {
    "min_score": f"{_SESSION_PREFIX}min_score",
    "max_stocks": f"{_SESSION_PREFIX}max_stocks",
    "strategy_weights": f"{_SESSION_PREFIX}strategy_weights",
    "ta_params": f"{_SESSION_PREFIX}ta_params",
    "screening": f"{_SESSION_PREFIX}screening",
}


def get_min_score() -> int:
    """Get minimum signal score, checking session state for overrides."""
    return st.session_state.get(_KEYS["min_score"], _BASE_MIN_SCORE)


def get_max_stocks() -> int:
    """Get max stocks to scan, checking session state for overrides."""
    return st.session_state.get(_KEYS["max_stocks"], _BASE_MAX_STOCKS)


def get_strategy_weights() -> dict:
    """Get strategy weights, checking session state for overrides."""
    val = st.session_state.get(_KEYS["strategy_weights"], _BASE_WEIGHTS)
    return dict(val)  # Return copy to prevent mutation


def get_ta_params() -> dict:
    """Get TA parameters, checking session state for overrides."""
    val = st.session_state.get(_KEYS["ta_params"], _BASE_TA_PARAMS)
    return dict(val)  # Return copy to prevent mutation


def get_screening() -> dict:
    """Get screening filters, checking session state for overrides."""
    val = st.session_state.get(_KEYS["screening"], _BASE_SCREENING)
    return dict(val)  # Return copy to prevent mutation


def save_strategy_weights(weights: dict) -> None:
    """Save strategy weight overrides to session state."""
    st.session_state[_KEYS["strategy_weights"]] = weights


def save_ta_params(params: dict) -> None:
    """Save TA parameter overrides to session state."""
    st.session_state[_KEYS["ta_params"]] = params


def save_screening(screening: dict) -> None:
    """Save screening filter overrides to session state."""
    st.session_state[_KEYS["screening"]] = screening


def save_min_score(score: int) -> None:
    """Save min score override to session state."""
    st.session_state[_KEYS["min_score"]] = score


def save_max_stocks(max_stocks: int) -> None:
    """Save max stocks override to session state."""
    st.session_state[_KEYS["max_stocks"]] = max_stocks


def reset_all() -> None:
    """Clear all config overrides from session state."""
    for key in _KEYS.values():
        if key in st.session_state:
            del st.session_state[key]


def get_active_config() -> dict:
    """Return the full active config (merged from session state and config.py)."""
    return {
        "min_score": get_min_score(),
        "max_stocks": get_max_stocks(),
        "strategy_weights": get_strategy_weights(),
        "ta_params": get_ta_params(),
        "screening": get_screening(),
    }
