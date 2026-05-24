from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel
from passlib.context import CryptContext
import sqlite3
import os
import hashlib

router = APIRouter()

# =========================
# PASSWORD HASHING
# =========================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password_sha256(password: str) -> str:
    """Pre-hash password with SHA256 before bcrypt to handle long passwords"""
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# DATABASE
# =========================
DATABASE = "local_dev.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# CREATE USERS TABLE
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

    # Validate input
    if not user.username or not user.username.strip():
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty"
        )

    if not user.password or len(user.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

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

    try:
        # Pre-hash password with SHA256 before bcrypt to avoid 72-byte limit
        sha256_password = hash_password_sha256(user.password)
        hashed_password = pwd_context.hash(sha256_password)

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (user.username, hashed_password)
        )

        conn.commit()
        conn.close()

        return {
            "message": "Signup successful"
        }
    except Exception as e:
        conn.close()
        raise HTTPException(
            status_code=500,
            detail=f"Signup failed: {str(e)}"
        )


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
        hash_password_sha256(user.password),
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

BACKEND_URL = os.getenv("BACKEND_URL", "https://finance-tracker-mv0i.onrender.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://finance-tracker-nsh5huggmvarbbzappy2w.streamlit.app")

oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
    redirect_uri=f"{BACKEND_URL}/auth/google/callback"
)

# =========================
# GOOGLE LOGIN ROUTE
# =========================
@router.get("/auth/google/login")
async def google_login(request: Request):

    redirect_uri = f"{BACKEND_URL}/auth/google/callback"

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )

# =========================
# GOOGLE CALLBACK ROUTE
# =========================
@router.get("/auth/google/callback")
async def google_callback(request: Request):

    try:
        token = await oauth.google.authorize_access_token(request)
        user = token.get("userinfo")
        email = user.get("email")

        print("Google Login Success:", email)

        # Redirect to Streamlit with auth params
        return RedirectResponse(
            url=f"{FRONTEND_URL}/?auth_token=google_{email}&username={email}"
        )
    except Exception as e:
        print("Google OAuth Error:", e)
        return RedirectResponse(url=f"{FRONTEND_URL}/?error=oauth_failed")