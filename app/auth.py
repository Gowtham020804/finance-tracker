import streamlit as st
import requests

# IMPORTANT:
# NEVER use localhost in deployed apps
API_URL = "https://finance-tracker-mv0i.onrender.com"


def signup_user():
    st.title("Signup")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        try:
            response = requests.post(
                f"{API_URL}/signup",
                json={
                    "username": username,
                    "password": password
                },
                timeout=20
            )

            if response.status_code == 200:
                st.success("Account Created Successfully")
            else:
                st.error(f"Signup failed: {response.text}")

        except Exception as e:
            st.error(f"Backend connection failed: {e}")


def login_user():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            response = requests.post(
                f"{API_URL}/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = data.get("token")

                st.success("Login Successful")
                st.rerun()

            else:
                st.error(f"Login failed: {response.text}")

        except Exception as e:
            st.error(f"Backend connection failed: {e}")

    st.markdown("---")
    st.subheader("Google Login")

    google_login_url = f"{API_URL}/auth/google/login"

    st.markdown(
        f"""
        <a href="{google_login_url}" target="_self">
            <button style="
                background-color:#4285F4;
                color:white;
                border:none;
                padding:10px 20px;
                border-radius:8px;
                cursor:pointer;
                font-size:16px;">
                Sign in with Google
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )