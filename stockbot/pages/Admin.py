"""Admin Dashboard - user management and app statistics."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.auth import is_admin, is_logged_in, get_all_users, delete_user, get_user_count


def show():
    if not is_logged_in():
        st.warning("You are not logged in.")
        if st.button("Go to Login"):
            st.session_state.current_page = "login"
            st.rerun()
        return

    if not is_admin():
        st.error("⛔ Access denied. Admin privileges required.")
        st.markdown(
            "<p style='color: #b0bec5;'>This page is restricted to the super admin account.</p>",
            unsafe_allow_html=True,
        )
        if st.button("← Back to Home"):
            st.session_state.current_page = "landing"
            st.rerun()
        return

    st.markdown("<h1 class='main-header'>🛡️ Admin Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='sub-header'>Super admin panel — manage users and view app statistics</p>",
        unsafe_allow_html=True,
    )

    # ─── App Statistics ───────────────────────────────────────────
    stats = get_user_count()

    st.markdown("### 📊 App Statistics")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Users", stats["total_users"])
    c2.metric("⚙️ With Preferences", stats["with_preferences"])
    c3.metric("🔒 With Secret Q", stats["with_secret_question"])
    c4.metric("🛡️ Admin Users", 1)

    st.divider()

    # ─── User Management ──────────────────────────────────────────
    st.markdown("### 👥 User Management")
    st.markdown(
        "<p style='color: #8892b0; font-size: 0.85rem;'>"
        "View all registered users. You can delete non-admin accounts here.</p>",
        unsafe_allow_html=True,
    )

    users = get_all_users()
    if not users:
        st.info("No users registered yet.")
        return

    # Build user dataframe
    user_rows = []
    for username, data in users.items():
        role = data.get("role", "user")
        role_label = "🛡️ Admin" if role == "admin" else "👤 User"
        has_prefs = "✅" if data.get("preferences") else "—"
        has_secret = "✅" if data.get("secret_question") else "—"
        user_rows.append({
            "Username": username,
            "Email": data.get("email", "—"),
            "Role": role_label,
            "Prefs": has_prefs,
            "Secret Q": has_secret,
        })

    df = pd.DataFrame(user_rows)

    st.dataframe(
        df,
        column_config={
            "Username": st.column_config.TextColumn("Username", width="small"),
            "Email": st.column_config.TextColumn("Email", width="medium"),
            "Role": st.column_config.TextColumn("Role", width="small"),
            "Prefs": st.column_config.TextColumn("Prefs", width="small"),
            "Secret Q": st.column_config.TextColumn("Secret Q", width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### 🗑️ Delete User")
    st.markdown(
        "<p style='color: #b0bec5; font-size: 0.85rem;'>"
        "Select a non-admin user to permanently delete their account.</p>",
        unsafe_allow_html=True,
    )

    non_admin_users = [u for u in users.keys() if u != "admin"]
    if non_admin_users:
        col_d1, col_d2 = st.columns([2, 1])
        with col_d1:
            user_to_delete = st.selectbox(
                "Select user to delete",
                options=non_admin_users,
                key="admin_delete_user",
            )
        with col_d2:
            if st.button("🗑️ Delete User", type="secondary", use_container_width=True):
                success, msg = delete_user(user_to_delete)
                if success:
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(msg)
    else:
        st.info("No non-admin users to manage.")

    st.divider()

    # ─── System Info ──────────────────────────────────────────────
    st.markdown("### ℹ️ System Information")
    with st.expander("View System Details"):
        import platform
        info = {
            "Python Version": platform.python_version(),
            "Platform": platform.platform(),
            "Users File": str(Path(__file__).parent.parent / "data" / "users.json"),
            "Streamlit Version": st.__version__,
        }
        for key, val in info.items():
            st.markdown(f"**{key}:** `{val}`")
