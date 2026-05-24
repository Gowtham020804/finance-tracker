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
    
    st.caption("Password requirements:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("✓ At least 6 characters")
    with col2:
        st.markdown("✓ Maximum 72 characters")

    if st.button("Create Account"):
        
        if not username or not username.strip():
            st.error("Please enter a username")
            return
            
        if not password or len(password) < 6:
            st.error("Password must be at least 6 characters")
            return
        
        if len(password) > 72:
            st.error("⚠️ Password is too long (max 72 characters). Please shorten it.")
            return

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

                st.success("Account Created Successfully!")
                st.info("Please log in with your credentials")

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
        
        if not username or not username.strip():
            st.error("Please enter your username")
            return
            
        if not password:
            st.error("Please enter your password")
            return

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

                st.success("Login Successful!")

                st.rerun()

            else:

                try:
                    detail = response.json().get("detail")
                except:
                    detail = response.text

                st.error(f"Login failed: {detail}")

        except Exception as e:

            st.error(f"Backend connection error: {e}")
            st.info("Please check if the backend server is running")

    # =========================
    # GOOGLE LOGIN SECTION
    # =========================
    st.markdown("---")

    st.markdown("### Or Sign in with Google")

    # Check for Google OAuth errors/callback
    params = st.query_params
    
    if params.get("error") == "oauth_failed":
        st.error("❌ Google Sign-in failed. Make sure your OAuth credentials are properly configured.")
        
    if params.get("auth_token") and params.get("auth_token")[0].startswith("google_"):
        email = params.get("username")[0] if params.get("username") else "User"
        st.session_state.logged_in = True
        st.session_state.username = email
        st.session_state.token = params.get("auth_token")[0]
        st.success(f"✅ Logged in as {email}")
        st.rerun()

    google_url = f"{API_URL}/auth/google/login"

    st.markdown(
        f"""
        <div style="display: flex; justify-content: center; margin-top: 20px;">
            <a href="{google_url}" target="_self">
                <button style="
                    background-color: #4285F4;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: background-color 0.3s;
                ">
                    🔵 Sign in with Google
                </button>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "⚠️ Click the button to continue with Google authentication. Make sure Google OAuth is configured on the backend."
    )