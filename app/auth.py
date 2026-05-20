import streamlit as st
import bcrypt
import jwt
import datetime

SECRET_KEY = "finance_secret"

users = {}


def generate_token(username):
    payload = {
        "user": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def signup_user():
    st.title("Signup")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Create Account"):
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        users[username] = hashed
        st.success("Account Created Successfully")


def login_user():
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users:
            if bcrypt.checkpw(password.encode(), users[username]):
                token = generate_token(username)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.token = token
                st.success("Login Successful")
            else:
                st.error("Invalid Password")
        else:
            st.error("User Not Found")
