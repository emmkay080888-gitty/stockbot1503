"""
GitHub OAuth module for Stock Signal Bot.
Implements Authorization Code Grant flow via Streamlit query params.

Add to .streamlit/secrets.toml:
[github_oauth]
client_id = "your_github_client_id"
client_secret = "your_github_client_secret"
redirect_uri = "http://localhost:8501"
"""

import os
import secrets
from typing import Optional
from urllib.parse import urlencode

import requests
import streamlit as st

# ─── GitHub OAuth Endpoints ────────────────────────────────────────────────

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com/user"
SCOPE = "read:user user:email"


# ─── Configuration ─────────────────────────────────────────────────────────

def get_client_config() -> dict:
    """Get GitHub OAuth credentials from Streamlit secrets, then env vars."""
    client_id = ""
    client_secret = ""
    redirect_uri = ""

    # Try Streamlit secrets first (recommended for Streamlit Cloud)
    try:
        if "github_oauth" in st.secrets:
            cfg = st.secrets["github_oauth"]
            client_id = cfg.get("client_id", "")
            client_secret = cfg.get("client_secret", "")
            redirect_uri = cfg.get("redirect_uri", "")
    except Exception:
        pass

    # Fall back to environment variables
    if not client_id:
        client_id = os.getenv("GITHUB_OAUTH_CLIENT_ID", "")
    if not client_secret:
        client_secret = os.getenv("GITHUB_OAUTH_CLIENT_SECRET", "")
    if not redirect_uri:
        redirect_uri = os.getenv("GITHUB_OAUTH_REDIRECT_URI", "http://localhost:8501")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }


def is_configured() -> bool:
    """Check if GitHub OAuth credentials are available."""
    cfg = get_client_config()
    return bool(cfg["client_id"] and cfg["client_secret"])


# ─── OAuth Flow Steps ──────────────────────────────────────────────────────

def get_authorization_url() -> str:
    """Build the GitHub OAuth authorization URL with CSRF state."""
    cfg = get_client_config()
    state = secrets.token_hex(16)
    st.session_state["github_oauth_state"] = state

    params = {
        "client_id": cfg["client_id"],
        "redirect_uri": cfg["redirect_uri"],
        "scope": SCOPE,
        "state": state,
        "response_type": "code",
    }

    return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_token(code: str) -> Optional[str]:
    """Exchange the authorization code for an access token."""
    cfg = get_client_config()

    try:
        resp = requests.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": cfg["client_id"],
                "client_secret": cfg["client_secret"],
                "code": code,
                "redirect_uri": cfg["redirect_uri"],
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data.get("access_token")
    except requests.RequestException:
        return None


def fetch_github_user(access_token: str) -> Optional[dict]:
    """Fetch the authenticated GitHub user's profile."""
    try:
        resp = requests.get(
            GITHUB_API_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return None
        return resp.json()
    except requests.RequestException:
        return None


def fetch_github_emails(access_token: str) -> list:
    """Fetch the user's verified emails from GitHub."""
    try:
        resp = requests.get(
            f"{GITHUB_API_URL}/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []
        return resp.json()
    except requests.RequestException:
        return []


# ─── Callback Handler (called from app.py) ─────────────────────────────────

def handle_callback() -> bool:
    """
    Handle the OAuth callback received via query params.
    Returns True if login was successful, False otherwise.
    """
    # Lazy import to avoid circular dependency
    from utils.auth import _load_users, _save_users, apply_preferences

    params = st.query_params

    # Check for error from GitHub
    if "error" in params:
        st.error(f"GitHub authorization failed: {params['error']}")
        _cleanup_params()
        return False

    code = params.get("code")
    state = params.get("state")

    if not code or not state:
        return False

    # Verify CSRF state token
    expected_state = st.session_state.pop("github_oauth_state", None)
    if not expected_state or state != expected_state:
        st.error("Security validation failed. Please try signing in again.")
        _cleanup_params()
        return False

    # Exchange code for access token
    token = exchange_code_for_token(code)
    if not token:
        st.error("Failed to authenticate with GitHub. Please try again.")
        _cleanup_params()
        return False

    # Fetch user info
    github_user = fetch_github_user(token)
    if not github_user:
        st.error("Failed to fetch GitHub profile.")
        _cleanup_params()
        return False

    github_login = github_user.get("login", "")
    github_name = github_user.get("name") or github_login
    github_id = str(github_user.get("id", ""))
    github_avatar = github_user.get("avatar_url", "")

    # Get primary verified email
    primary_email = github_user.get("email", "")
    if not primary_email:
        emails = fetch_github_emails(token)
        for email in emails:
            if email.get("primary") and email.get("verified"):
                primary_email = email.get("email", "")
                break
        if not primary_email and emails:
            primary_email = emails[0].get("email", "")

    # Username convention: github_{login}
    username = f"github_{github_login}"

    users = _load_users()

    if username in users:
        # Existing GitHub-linked user — log them in
        user_data = users[username]
        st.session_state["user"] = {
            "username": username,
            "name": user_data.get("name", github_name),
            "email": user_data.get("email", primary_email),
            "github_login": github_login,
            "github_id": github_id,
            "github_avatar": github_avatar,
        }
    else:
        # Check if any user has this email (link accounts)
        linked_user = None
        for uname, uinfo in users.items():
            if uinfo.get("email", "").lower() == primary_email.lower():
                linked_user = uname
                break

        if linked_user:
            # Link GitHub identity to existing account
            users[linked_user]["github_login"] = github_login
            users[linked_user]["github_id"] = github_id
            users[linked_user]["github_avatar"] = github_avatar
            _save_users(users)
            st.session_state["user"] = {
                "username": linked_user,
                "name": users[linked_user].get("name", github_name),
                "email": users[linked_user].get("email", primary_email),
                "github_login": github_login,
                "github_id": github_id,
                "github_avatar": github_avatar,
            }
        else:
            # Create a new user account linked to GitHub
            email_for_storage = primary_email or f"{github_login}@github.local"
            users[username] = {
                "email": email_for_storage,
                "password": "",
                "name": github_name,
                "github_login": github_login,
                "github_id": github_id,
                "github_avatar": github_avatar,
            }
            _save_users(users)
            st.session_state["user"] = {
                "username": username,
                "name": github_name,
                "email": email_for_storage,
                "github_login": github_login,
                "github_id": github_id,
                "github_avatar": github_avatar,
            }

    # Apply user preferences (market, etc.)
    apply_preferences(st.session_state["user"]["username"])

    st.session_state["github_oauth_done"] = True
    _cleanup_params()
    st.rerun()
    return True


def _cleanup_params():
    """Remove OAuth-related query params and state from the URL."""
    for key in ["code", "state", "error", "error_description", "error_uri"]:
        if key in st.query_params:
            del st.query_params[key]
    if "github_oauth_done" in st.session_state:
        del st.session_state["github_oauth_done"]
