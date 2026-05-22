import streamlit as st
import requests

# Your Render backend URL
API_URL = "https://finance-tracker-mv0i.onrender.com"


def signup_user():
    st.title("Signup")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        try:
            resp = requests.post(
                f"{API_URL}/signup",
                json={"username": username, "password": password},
                timeout=15,
            )

            if resp.status_code == 200:
                st.success("Account Created Successfully")
            else:
                st.error(f"Signup failed: {resp.text}")

        except Exception as e:
            st.error(f"Failed to reach backend: {e}")


def login_user():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            resp = requests.post(
                f"{API_URL}/login",
                json={"username": username, "password": password},
                timeout=15,
            )

            if resp.status_code == 200:
                data = resp.json()

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = data.get("token")

                st.success("Login Successful")

            else:
                st.error(f"Login failed: {resp.text}")

        except Exception as e:
            st.error(f"Failed to reach backend: {e}")

    st.markdown("---")
    st.markdown("### Or sign in with Google")

    google_url = f"{API_URL}/auth/google/login"

    st.markdown(
        f"""
        <a href="{google_url}" target="_self">
            <button style="
                background-color:#4285F4;
                color:white;
                border:none;
                padding:10px 20px;
                border-radius:6px;
                cursor:pointer;">
                Sign in with Google
            </button>
        </a>
        """,
        unsafe_allow_html=True,
    )