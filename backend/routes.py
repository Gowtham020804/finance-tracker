from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from passlib.context import CryptContext
from authlib.integrations.starlette_client import OAuth
import os

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy user storage
users_db = {}


# -------------------------
# Request Models
# -------------------------

class UserSignup(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


# -------------------------
# Signup Route
# -------------------------

@router.post("/signup")
async def signup(user: UserSignup):

    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(user.password)

    users_db[user.username] = {
        "username": user.username,
        "password": hashed_password
    }

    return {"message": "Signup successful"}


# -------------------------
# Login Route
# -------------------------

@router.post("/login")
async def login(user: UserLogin):

    db_user = users_db.get(user.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "message": "Login successful",
        "token": "dummy_token"
    }


# -------------------------
# Google OAuth Setup
# -------------------------

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


# -------------------------
# Google Login Route
# -------------------------

@router.get("/auth/google")
async def google_login(request: Request):

    redirect_uri = "https://finance-tracker-mv0i.onrender.com/auth/google/callback"

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


# -------------------------
# Google Callback Route
# -------------------------

@router.get("/auth/google/callback")
async def google_callback(request: Request):

    token = await oauth.google.authorize_access_token(request)

    user_info = token.get("userinfo")

    if user_info:
        email = user_info.get("email")

        return {
            "message": "Google login successful",
            "email": email
        }

    raise HTTPException(status_code=400, detail="Google login failed")