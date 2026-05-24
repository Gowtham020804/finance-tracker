import sys
import os
import streamlit as st
from pathlib import Path

# Ensure project root is on sys.path
ROOT = os.path.dirname(os.path.dirname(__file__))

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.auth import login_user, signup_user
from app.dashboard import dashboard_page

st.set_page_config(
    page_title="Finance Tracker",
    layout="wide"
)

# =========================
# GOOGLE LOGIN SESSION
# =========================
params = st.query_params

# Handle Google OAuth callback
if params.get("auth_token"):
    token = params.get("auth_token")[0] if isinstance(params.get("auth_token"), list) else params.get("auth_token")
    username = params.get("username")[0] if isinstance(params.get("username"), list) else params.get("username")
    
    if token and username:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.token = token

# Handle old format for backward compatibility
elif params.get("logged_in") == "true":
    st.session_state.logged_in = True
    st.session_state.username = params.get("username")

# =========================
# LOAD CSS
# =========================
css_path = Path(__file__).resolve().parents[1] / "static" / "style.css"

if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True
        )

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =========================
# MENU
# =========================
menu = ["Login", "Signup"]

choice = st.sidebar.selectbox(
    "Menu",
    menu
)

# =========================
# PAGE ROUTING
# =========================
if not st.session_state.logged_in:

    if choice == "Login":
        login_user()

    else:
        signup_user()

else:
    dashboard_page()