import sys
import os
import streamlit as st
from pathlib import Path

# Ensure project root is on sys.path so `import app.*` works when Streamlit
# runs the script from the `app/` directory.
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.auth import login_user, signup_user
from app.dashboard import dashboard_page

st.set_page_config(page_title="Finance Tracker", layout="wide")

params = st.query_params
if params.get("auth_token") and params.get("username") and not st.session_state.get("logged_in"):
    st.session_state.token = params.get("auth_token")[0]
    st.session_state.username = params.get("username")[0]
    st.session_state.logged_in = True

css_path = Path(__file__).resolve().parents[1] / "static" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as css_file:
        st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

if not st.session_state.logged_in:
    if choice == "Login":
        login_user()
    else:
        signup_user()
else:
    dashboard_page()