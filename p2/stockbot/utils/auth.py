"""User authentication module - file-based with hashed passwords."""

import hashlib
import json
import os
from pathlib import Path
import streamlit as st

AUTH_FILE = Path(__file__).parent.parent / "data" / "users.json"

# ── Email validation ────────────────────────────────────────────────
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

DISPOSABLE_DOMAINS = {
    # Common disposable / temporary email providers
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com",
    "throwaway.email", "trashmail.com", "sharklasers.com", "yopmail.com",
    "mailnator.com", "temp-mail.org", "fakeinbox.com", "maildrop.cc",
    "getnada.com", "burnermail.io", "discard.email", "emailondeck.com",
    "spam4.me", "tempr.email", "mailmetrash.com", "mytemp.email",
    "mailinator2.com", "sogetthis.com", "spambox.us", "tempemail.net",
    "tempinbox.com", "throwawayemail.com", "mailexpire.com", "mailetc.com",
}


def validate_email(email: str) -> tuple[bool, str]:
    """Validate email format and check for disposable domains."""
    email = email.strip().lower()
    if not EMAIL_REGEX.match(email):
        return False, "Please enter a valid email address."
    domain = email.split("@")[-1]
    if domain in DISPOSABLE_DOMAINS:
        return False, "Disposable email addresses are not allowed. Please use a permanent email."
    return True, ""


# ── Remember Me (session tokens) ────────────────────────────────────
import secrets

def _generate_token() -> str:
    """Generate a random 32-character hex token."""
    return secrets.token_hex(16)


def create_remember_token(username: str) -> str:
    """Create a remember-me token for a user and save it."""
    users = _load_users()
    username = username.strip().lower()
    if username not in users:
        return ""
    token = _generate_token()
    if "remember_tokens" not in users[username]:
        users[username]["remember_tokens"] = []
    users[username]["remember_tokens"].append(token)
    # Keep only the last 3 tokens
    users[username]["remember_tokens"] = users[username]["remember_tokens"][-3:]
    _save_users(users)
    return token


def verify_remember_token(username: str, token: str) -> bool:
    """Verify a remember-me token."""
    users = _load_users()
    username = username.strip().lower()
    if username not in users:
        return False
    tokens = users[username].get("remember_tokens", [])
    return token in tokens


def clear_remember_tokens(username: str):
    """Clear all remember-me tokens for a user (on logout)."""
    users = _load_users()
    username = username.strip().lower()
    if username in users and "remember_tokens" in users[username]:
        del users[username]["remember_tokens"]
        _save_users(users)


# ── User Preferences ────────────────────────────────────────────────

def save_preferences(username: str, preferences: dict):
    """Save per-user preferences."""
    users = _load_users()
    username = username.strip().lower()
    if username not in users:
        return False
    users[username]["preferences"] = preferences
    _save_users(users)
    # Also update session state
    if "user_preferences" in st.session_state:
        st.session_state["user_preferences"].update(preferences)
    else:
        st.session_state["user_preferences"] = preferences
    return True


def get_preferences(username: str) -> dict:
    """Get per-user preferences."""
    users = _load_users()
    username = username.strip().lower()
    if username not in users:
        return {}
    return users[username].get("preferences", {})


def apply_preferences(username: str):
    """Apply user preferences to current session (e.g., set default market)."""
    prefs = get_preferences(username)
    st.session_state["user_preferences"] = prefs
    # Apply default market if set
    if "default_market" in prefs and prefs["default_market"]:
        from utils.markets import set_market
        set_market(prefs["default_market"])
    return prefs


SECRET_QUESTIONS = [
    "What is your mother's maiden name?",
    "What was the name of your first pet?",
    "What city were you born in?",
    "What was your childhood nickname?",
    "What is your favorite book?",
    "What elementary school did you attend?",
    "What is the name of your favorite teacher?",
    "What is your dream job?",
    "What was the model of your first car?",
    "What is your favorite movie?",
    "What is the name of your best friend?",
    "What street did you grow up on?",
]


def _load_users() -> dict:
    """Load all registered users from JSON file."""
    if not AUTH_FILE.exists():
        return {}
    try:
        with open(AUTH_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_users(users: dict):
    """Save all users to JSON file."""
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    salt = "stockbot_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()


def create_user(username: str, email: str, password: str, secret_question: str = "", secret_answer: str = "") -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    users = _load_users()
    username = username.strip().lower()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    if not secret_question:
        return False, "Please select a security question."
    if not secret_answer or len(secret_answer.strip()) < 2:
        return False, "Please provide a valid answer to the security question."
    if username in users:
        return False, "Username already exists."
    if any(u["email"] == email for u in users.values()):
        return False, "Email already registered."

    users[username] = {
        "email": email,
        "password": _hash_password(password),
        "name": username,
        "secret_question": secret_question,
        "secret_answer": _hash_password(secret_answer.strip().lower()),
    }
    _save_users(users)
    return True, "Account created successfully!"


def authenticate(username: str, password: str) -> tuple[bool, str]:
    """Verify login credentials. Returns (success, message)."""
    users = _load_users()
    username = username.strip().lower()

    if username not in users:
        return False, "Invalid username or password."

    user = users[username]
    if user["password"] != _hash_password(password):
        return False, "Invalid username or password."

    return True, f"Welcome back, {user.get('name', username)}!"


def login(username: str, password: str, remember: bool = False) -> str:
    """Authenticate and set session state. Returns empty string on success, or error message."""
    success, msg = authenticate(username, password)
    if success:
        username_lower = username.strip().lower()
        st.session_state["user"] = {
            "username": username_lower,
            "name": _load_users()[username_lower].get("name", username),
            "email": _load_users()[username_lower].get("email", ""),
        }
        # Apply user preferences
        apply_preferences(username_lower)
        # Generate remember token if requested
        if remember:
            token = create_remember_token(username_lower)
            return token  # Return token for JS to save to localStorage
        return ""
    return None  # Login failed


def logout():
    """Clear user session state and remember tokens."""
    if "user" in st.session_state:
        clear_remember_tokens(st.session_state["user"]["username"])
        del st.session_state["user"]
    if "user_preferences" in st.session_state:
        del st.session_state["user_preferences"]


def is_logged_in() -> bool:
    """Check if a user is currently logged in."""
    return "user" in st.session_state and st.session_state["user"] is not None


def get_current_user() -> dict | None:
    """Get the current logged-in user's info."""
    return st.session_state.get("user")


# ── Admin Role ──────────────────────────────────────────────────────

ADMIN_USERNAME = "admin"


def is_admin() -> bool:
    """Check if the current logged-in user is the super admin."""
    if not is_logged_in():
        return False
    user = get_current_user()
    return user.get("username", "") == ADMIN_USERNAME


def seed_admin(password: str, email: str = "admin@stockbot.local", secret_question: str = "What is your favorite book?", secret_answer: str = "admin") -> tuple[bool, str]:
    """Seed the admin user into the users file. Idempotent (won't overwrite existing admin)."""
    users = _load_users()
    if ADMIN_USERNAME in users:
        return True, "Admin account already exists."
    from datetime import datetime
    users[ADMIN_USERNAME] = {
        "email": email.strip().lower(),
        "password": _hash_password(password),
        "name": "Admin",
        "secret_question": secret_question,
        "secret_answer": _hash_password(secret_answer.strip().lower()),
        "role": "admin",
        "created_at": datetime.now().isoformat(),
    }
    _save_users(users)
    return True, f"Admin account created! Username: {ADMIN_USERNAME}"


def get_all_users() -> dict:
    """Get all registered users (admin only)."""
    return _load_users()


def delete_user(username: str) -> tuple[bool, str]:
    """Delete a user account. Cannot delete the admin account."""
    users = _load_users()
    username = username.strip().lower()
    if username == ADMIN_USERNAME:
        return False, "Cannot delete the admin account."
    if username not in users:
        return False, "User not found."
    del users[username]
    _save_users(users)
    return True, f"User '{username}' deleted successfully."


def get_user_count() -> dict:
    """Get app statistics: total users, total with preferences, etc."""
    users = _load_users()
    total = len(users)
    with_prefs = sum(1 for u in users.values() if u.get("preferences"))
    with_secret = sum(1 for u in users.values() if u.get("secret_question"))
    return {
        "total_users": total,
        "with_preferences": with_prefs,
        "with_secret_question": with_secret,
    }


def get_secret_question(username: str) -> str | None:
    """Get the secret question for a username. Returns None if user doesn't exist."""
    users = _load_users()
    username = username.strip().lower()
    if username not in users:
        return None
    return users[username].get("secret_question", "")


def verify_secret_answer(username: str, answer: str) -> bool:
    """Verify the secret answer for a user."""
    users = _load_users()
    username = username.strip().lower()
    if username not in users:
        return False
    stored_hash = users[username].get("secret_answer", "")
    if not stored_hash:
        return False
    return stored_hash == _hash_password(answer.strip().lower())


def reset_password(username: str, new_password: str) -> tuple[bool, str]:
    """Reset password after secret question verification."""
    if len(new_password) < 4:
        return False, "Password must be at least 4 characters."
    users = _load_users()
    username = username.strip().lower()
    if username not in users:
        return False, "User not found."
    users[username]["password"] = _hash_password(new_password)
    _save_users(users)
    return True, "Password reset successfully!"
