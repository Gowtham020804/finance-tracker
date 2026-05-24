import streamlit as st
import requests

# =========================
# BACKEND API URL
# =========================
API_URL = "https://finance-tracker-mv0i.onrender.com"


# =========================
# SIGNUP
# =========================
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
                timeout=10
            )

            if response.status_code == 200:

                st.success("Account Created Successfully")

            else:

                try:
                    detail = response.json().get("detail")
                except:
                    detail = response.text

                st.error(f"Signup failed: {detail}")

        except Exception as e:

            st.error(f"Backend Error: {e}")


# =========================
# LOGIN
# =========================
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
                timeout=10
            )

            if response.status_code == 200:

                data = response.json()

                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = data.get("token")

                st.success("Login Successful")

                st.rerun()

            else:

                try:
                    detail = response.json().get("detail")
                except:
                    detail = response.text

                st.error(f"Login failed: {detail}")

        except Exception as e:

            st.error(f"Backend Error: {e}")

    # =========================
    # GOOGLE LOGIN
    # =========================
    st.markdown("---")

    st.markdown("## Or Sign in with Google")

    # IMPORTANT FIX
    google_url = f"{API_URL}/auth/google/login"

    st.markdown(
        f"""
        <a href="{google_url}" target="_self">
            <button style="
                background-color:#4285F4;
                color:white;
                border:none;
                padding:10px 20px;
                border-radius:8px;
                cursor:pointer;
                font-size:16px;
                font-weight:bold;
            ">
                Sign in with Google
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Click the button to continue with Google authentication."
    )