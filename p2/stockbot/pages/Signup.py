"""Signup / Registration page."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import create_user, SECRET_QUESTIONS, validate_email


def show():
    st.markdown("""
    <style>
    .auth-container {
        max-width: 420px;
        margin: 40px auto;
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
    .secret-note {
        color: #78909c;
        font-size: 0.75rem;
        margin: -8px 0 12px 0;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='auth-title'>📝 Create Account</h1>", unsafe_allow_html=True)
    st.markdown("<p class='auth-sub'>Join StockBot and start analyzing markets</p>", unsafe_allow_html=True)

    username = st.text_input("Username", key="signup_user", placeholder="Choose a username")
    email = st.text_input("Email", key="signup_email", placeholder="your@email.com")
    password = st.text_input("Password", type="password", key="signup_pass", placeholder="At least 4 characters")
    confirm = st.text_input("Confirm Password", type="password", key="signup_confirm", placeholder="Repeat password")

    st.markdown("<hr style='margin: 20px 0; border-color: rgba(124,77,255,0.2);'>", unsafe_allow_html=True)
    st.markdown("<p style='color: #e0e0e0; font-size: 0.9rem; font-weight: 600;'>🔒 Account Recovery</p>", unsafe_allow_html=True)
    st.markdown("<p class='secret-note'>Set a security question to recover your account if you forget your password.</p>", unsafe_allow_html=True)

    secret_question = st.selectbox(
        "Security Question",
        options=SECRET_QUESTIONS,
        key="signup_secret_q",
    )
    secret_answer = st.text_input(
        "Your Answer",
        key="signup_secret_a",
        placeholder="Enter your answer",
        help="This will be used to verify your identity if you forget your password.",
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Create Account", type="primary", use_container_width=True):
            if not username or not email or not password:
                st.error("Please fill in all fields.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                # Email validation
                email_valid, email_msg = validate_email(email)
                if not email_valid:
                    st.error(email_msg)
                else:
                    success, msg = create_user(username, email, password, secret_question, secret_answer)
                    if success:
                        st.success("✅ Account created! Please log in.")
                        st.session_state["current_page"] = "login"
                        st.rerun()
                    else:
                        st.error(msg)

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.session_state["current_page"] = "landing"
            st.rerun()

    st.markdown(
        "<p class='auth-switch'>Already have an account? "
        "<strong><a onclick=''>Sign in</a></strong></p>",
        unsafe_allow_html=True,
    )

    if st.button("Sign In Instead →", use_container_width=False):
        st.session_state["current_page"] = "login"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
