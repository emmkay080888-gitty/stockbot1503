"""User profile page."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import is_logged_in, get_current_user, get_preferences, save_preferences, logout
from utils.markets import get_market_list, get_current_market_key, set_market, get_market_config


def show():
    if not is_logged_in():
        st.warning("You are not logged in.")
        if st.button("Go to Login"):
            st.session_state["current_page"] = "login"
            st.rerun()
        return

    user = get_current_user()
    username = user.get("username", "")
    current_prefs = get_preferences(username)

    st.markdown("<h1 class='main-header'>👤 My Profile</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(124,77,255,0.1), rgba(0,200,83,0.05));
                    border: 1px solid rgba(124,77,255,0.2); border-radius: 16px; padding: 30px; text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 10px;">👤</div>
            <h3 style="color: #e0e0e0; margin: 0;">{user.get('name', 'User')}</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Account Details")
        st.markdown(f"**Username:** {user.get('username', '—')}")
        st.markdown(f"**Email:** {user.get('email', '—')}")
        st.markdown(f"**Status:** {'✅ Active' if is_logged_in() else '❌ Not logged in'}")

    st.divider()

    # ─── User Preferences ─────────────────────────────────────────
    st.markdown("### ⚙️ My Preferences")
    st.markdown(
        "<p style='color: #8892b0; font-size: 0.85rem;'>"
        "Customize your default settings. These are saved to your account and applied on every login.</p>",
        unsafe_allow_html=True,
    )

    # Default Market preference
    market_options = get_market_list()
    saved_market = current_prefs.get("default_market", get_current_market_key())
    pref_market = st.selectbox(
        "Default Market / Exchange",
        options=[m["key"] for m in market_options],
        format_func=lambda k: next((m["label"] for m in market_options if m["key"] == k), k),
        index=next((i for i, m in enumerate(market_options) if m["key"] == saved_market), 0),
        key="profile_pref_market",
        help="This market will be selected automatically when you log in.",
    )

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("💾 Save Preferences", type="primary", use_container_width=True):
            new_prefs = {"default_market": pref_market}
            save_preferences(username, new_prefs)
            # Apply immediately
            set_market(pref_market)
            st.success("✅ Preferences saved!")
            st.rerun()

    st.divider()

    if st.button("🚪 Log Out", type="secondary", use_container_width=False):
        logout()
        st.query_params["logged_out"] = "1"
        st.success("Logged out successfully.")
        st.session_state["current_page"] = "landing"
        st.rerun()
