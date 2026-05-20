import streamlit as st
from app.auth import login_user, signup_user
from app.dashboard import dashboard_page

st.set_page_config(page_title="Finance Tracker", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

menu = ["Login", "Signup"]
choice = st.sidebar.selectbox("Menu", menu)

st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to right, #141e30, #243b55);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if not st.session_state.logged_in:
    if choice == "Login":
        login_user()
    else:
        signup_user()
else:
    dashboard_page()