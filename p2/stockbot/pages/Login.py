"""Login page with GitHub OAuth support."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import login
from utils.oauth_github import is_configured, get_authorization_url


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
    .github-btn {
        display: inline-flex; align-items: center; justify-content: center; gap: 8px;
        width: 100%; padding: 12px 20px; border-radius: 12px;
        font-size: 0.95rem; font-weight: 600; cursor: pointer; border: none;
        background: #24292e; color: white !important;
        transition: all 0.3s ease; text-decoration: none;
    }
    .github-btn:hover {
        background: #1b1f23; transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(36,41,46,0.4);
    }
    .divider-row {
        display: flex; align-items: center; gap: 12px; margin: 20px 0; color: #555;
        font-size: 0.8rem;
    }
    .divider-row hr { flex: 1; border: none; border-top: 1px solid rgba(124,77,255,0.2); }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='auth-title'>🔐 Welcome Back</h1>", unsafe_allow_html=True)
    st.markdown("<p class='auth-sub'>Sign in to your StockBot account</p>", unsafe_allow_html=True)

    # ── GitHub OAuth Button ────────────────────────────────────────────────
    if is_configured():
        github_url = get_authorization_url()
        st.markdown(
            f'<a href="{github_url}" class="github-btn">'
            '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="white">'
            '<path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>'
            '</svg> Sign in with GitHub</a>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="divider-row"><hr><span>or sign in with your password</span><hr></div>', unsafe_allow_html=True)

    # ── Email / Password Form ──────────────────────────────────────────────
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
