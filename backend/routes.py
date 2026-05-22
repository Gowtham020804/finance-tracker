from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel
from passlib.context import CryptContext
import sqlite3
import os

router = APIRouter()

# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# =========================
# DATABASE
# =========================
DATABASE = "local_dev.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# CREATE TABLE
# =========================
conn = get_db_connection()

conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.commit()
conn.close()

# =========================
# Pydantic Models
# =========================
class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# =========================
# SIGNUP ROUTE
# =========================
@router.post("/signup")
def signup(user: UserCreate):

    conn = get_db_connection()

    existing_user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (user.username,)
    ).fetchone()

    if existing_user:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    hashed_password = pwd_context.hash(user.password)

    conn.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (user.username, hashed_password)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Signup successful"
    }


# =========================
# LOGIN ROUTE
# =========================
@router.post("/login")
def login(user: UserLogin):

    conn = get_db_connection()

    db_user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (user.username,)
    ).fetchone()

    conn.close()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid username"
        )

    if not pwd_context.verify(
        user.password,
        db_user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    return {
        "message": "Login successful",
        "token": "dummy_token"
    }


# =========================
# GOOGLE OAUTH
# =========================
oauth = OAuth()

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

# =========================
# GOOGLE LOGIN ROUTE
# =========================
@router.get("/auth/google/login")
async def google_login(request: Request):

    redirect_uri = "https://finance-tracker-mv0i.onrender.com/auth/google/callback"

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


# =========================
# GOOGLE CALLBACK ROUTE
# =========================
@router.get("/auth/google/callback")
async def google_callback(request: Request):

    token = await oauth.google.authorize_access_token(request)

    user_info = token.get("userinfo")

    email = user_info.get("email")

    print("Google Login Success:", email)

    # REDIRECT TO STREAMLIT APP
    return RedirectResponse(
        url="https://finance-expense-tracker.streamlit.app"
    )