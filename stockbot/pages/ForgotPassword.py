"""Forgot Password page - reset password via secret question."""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import get_secret_question, verify_secret_answer, reset_password


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
    .step-badge {
        display: inline-block;
        background: linear-gradient(135deg, rgba(124,77,255,0.2), rgba(0,200,83,0.1));
        border: 1px solid rgba(124,77,255,0.3);
        border-radius: 12px;
        padding: 2px 12px;
        font-size: 0.7rem;
        color: #7c4dff;
        letter-spacing: 1px;
        margin-bottom: 16px;
    }
    .back-link {
        margin-top: 20px;
        color: #78909c;
        font-size: 0.85rem;
    }
    .back-link a {
        color: #7c4dff;
        text-decoration: none;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='auth-title'>🔑 Reset Password</h1>", unsafe_allow_html=True)
    st.markdown("<p class='auth-sub'>Verify your identity using your security question</p>", unsafe_allow_html=True)

    # Step tracking
    if "fp_step" not in st.session_state:
        st.session_state.fp_step = 1
    if "fp_username" not in st.session_state:
        st.session_state.fp_username = ""

    # ─── Step 1: Enter Username ───────────────────────────────────
    if st.session_state.fp_step == 1:
        st.markdown("<div class='step-badge'>STEP 1 OF 3</div>", unsafe_allow_html=True)
        st.markdown("<p style='color: #e0e0e0; font-size: 0.9rem;'>Enter your username to look up your security question.</p>", unsafe_allow_html=True)

        username = st.text_input("Username", key="fp_user", placeholder="Enter your username")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Continue", type="primary", use_container_width=True):
                if not username:
                    st.error("Please enter your username.")
                else:
                    question = get_secret_question(username)
                    if question:
                        st.session_state.fp_username = username.strip().lower()
                        st.session_state.fp_question = question
                        st.session_state.fp_step = 2
                        st.rerun()
                    else:
                        st.error("Username not found or no security question set.")

        with col2:
            if st.button("Back to Login", use_container_width=True):
                if "fp_step" in st.session_state:
                    del st.session_state.fp_step
                    del st.session_state.fp_username
                st.session_state.current_page = "login"
                st.rerun()

    # ─── Step 2: Answer Secret Question ───────────────────────────
    elif st.session_state.fp_step == 2:
        st.markdown("<div class='step-badge'>STEP 2 OF 3</div>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='color: #e0e0e0; font-size: 0.9rem;'>"
            f"Username: <strong>{st.session_state.fp_username}</strong></p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='color: #b0bec5; font-size: 1rem; margin: 16px 0;'>"
            f"❓ {st.session_state.fp_question}</p>",
            unsafe_allow_html=True,
        )

        answer = st.text_input("Your Answer", key="fp_answer", placeholder="Type your answer")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Verify", type="primary", use_container_width=True):
                if not answer:
                    st.error("Please enter your answer.")
                elif verify_secret_answer(st.session_state.fp_username, answer):
                    st.session_state.fp_step = 3
                    st.rerun()
                else:
                    st.error("Incorrect answer. Please try again.")

        with col2:
            if st.button("Back", use_container_width=True):
                st.session_state.fp_step = 1
                st.rerun()

    # ─── Step 3: Set New Password ─────────────────────────────────
    elif st.session_state.fp_step == 3:
        st.markdown("<div class='step-badge'>STEP 3 OF 3</div>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='color: #e0e0e0; font-size: 0.9rem;'>"
            f"Username: <strong>{st.session_state.fp_username}</strong></p>",
            unsafe_allow_html=True,
        )
        st.markdown("<p style='color: #b0bec5; font-size: 0.85rem; margin-bottom: 16px;'>✅ Identity verified! Choose a new password.</p>", unsafe_allow_html=True)

        new_pass = st.text_input("New Password", type="password", key="fp_new_pass", placeholder="At least 4 characters")
        confirm_pass = st.text_input("Confirm New Password", type="password", key="fp_confirm", placeholder="Repeat password")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Reset Password", type="primary", use_container_width=True):
                if not new_pass:
                    st.error("Please enter a new password.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 4:
                    st.error("Password must be at least 4 characters.")
                else:
                    success, msg = reset_password(st.session_state.fp_username, new_pass)
                    if success:
                        st.success("✅ Password reset successfully! You can now log in.")
                        # Clean up session
                        for key in ["fp_step", "fp_username", "fp_question"]:
                            if key in st.session_state:
                                del st.session_state[key]
                        st.session_state.current_page = "login"
                        st.rerun()
                    else:
                        st.error(msg)

        with col2:
            if st.button("Cancel", use_container_width=True):
                for key in ["fp_step", "fp_username", "fp_question"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_page = "login"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
