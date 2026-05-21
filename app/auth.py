import streamlit as st
import requests
from pathlib import Path

# Backend API base URL — override via Streamlit secrets if present
API_URL = st.secrets.get("API_URL", "http://localhost:8000")


def signup_user():
    st.title("Signup")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        try:
            resp = requests.post(
                f"{API_URL}/signup",
                json={"username": username, "password": password},
                timeout=5,
            )
        except Exception as e:
            st.error(f"Failed to reach backend: {e}")
            return

        if resp.status_code == 200:
            st.success("Account Created Successfully")
        else:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            st.error(f"Signup failed: {detail}")


def login_user():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            resp = requests.post(
                f"{API_URL}/login",
                json={"username": username, "password": password},
                timeout=5,
            )
        except Exception as e:
            st.error(f"Failed to reach backend: {e}")
            return

        if resp.status_code == 200:
            data = resp.json()
            token = data.get("token")
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.token = token
            st.success("Login Successful")
        else:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            st.error(f"Login failed: {detail}")

    st.markdown("---")
    st.markdown("### Or sign in with Google")
    google_url = f"{API_URL}/auth/google/login"
    st.markdown(
        f'<a href="{google_url}" target="_blank"><button style="background-color:#4285F4;color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;">Sign in with Google</button></a>',
        unsafe_allow_html=True,
    )
    st.caption("A new browser tab will open for Google sign-in. After login, return here.")
