"""Login page."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import login


def show():
    st.markdown("""
    <style>
    .auth-container {
        max-width: 400px;
        margin: 60px auto;
        padding: 40px;
        background: linear-gradient(135deg, rgba(124,77,255,0.08), rgba(0,200,83,0.05));
        border: 1px solid rgba(124,77,255,0.2);
        border-radius: 20px;
        text-align: center;
    }
    .auth-title {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 8px !important;
    }
    .auth-sub {
        color: #b0bec5;
        font-size: 0.9rem;
        margin-bottom: 24px;
    }
    .auth-switch {
        margin-top: 20px;
        color: #78909c;
        font-size: 0.85rem;
    }
    .auth-switch a {
        color: #7c4dff;
        text-decoration: none;
        cursor: pointer;
    }
    .remember-row {
        display: flex; align-items: center; justify-content: center;
        gap: 8px; margin: 12px 0; color: #b0bec5; font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='auth-title'>🔐 Welcome Back</h1>", unsafe_allow_html=True)
    st.markdown("<p class='auth-sub'>Sign in to your StockBot account</p>", unsafe_allow_html=True)

    username = st.text_input("Username", key="login_user", placeholder="Enter your username")
    password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")

    # Remember Me checkbox
    remember = st.checkbox("Remember Me", value=False, key="login_remember",
                          help="Stay logged in across browser sessions")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Sign In", type="primary", use_container_width=True):
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                result = login(username, password, remember=remember)
                if result is not None:
                    # If remember was checked, set query params for auto-login
                    if remember and result:
                        token = result
                        st.query_params["auto_user"] = username.strip().lower()
                        st.query_params["auto_token"] = token
                        # Clear any logged_out flag so JS saves the new token
                        if "logged_out" in st.query_params:
                            del st.query_params["logged_out"]
                    st.success("Login successful!")
                    next_page = st.session_state.get("login_redirect", "landing")
                    st.session_state["current_page"] = next_page
                    if "login_redirect" in st.session_state:
                        del st.session_state["login_redirect"]
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state["current_page"] = "landing"
            st.rerun()

    # Forgot password link
    st.markdown(
        "<p style='text-align: center; margin-top: 8px;'>"
        "<a onclick='' style='color: #ff9100; text-decoration: none; cursor: pointer; font-size: 0.85rem;'>"
        "🔑 Forgot Password?</a></p>",
        unsafe_allow_html=True,
    )

    if st.button("🔑 Forgot Password?", use_container_width=False, type="secondary"):
        st.session_state["current_page"] = "forgot_password"
        st.rerun()

    st.markdown(
        "<p class='auth-switch'>Don't have an account? "
        "<strong><a onclick=''>Sign up</a></strong></p>",
        unsafe_allow_html=True,
    )

    if st.button("Create New Account →", use_container_width=False):
        st.session_state["current_page"] = "signup"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
