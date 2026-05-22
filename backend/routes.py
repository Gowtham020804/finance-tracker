from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# -----------------------------
# Request Models
# -----------------------------
class UserAuth(BaseModel):
    username: str
    password: str


# -----------------------------
# Signup Route
# -----------------------------
@router.post("/signup")
def signup(user: UserAuth):
    return {
        "message": f"User {user.username} created successfully"
    }


# -----------------------------
# Login Route
# -----------------------------
@router.post("/login")
def login(user: UserAuth):
    return {
        "token": "demo_token",
        "username": user.username
    }


# -----------------------------
# Google Auth Routes
# -----------------------------
@router.get("/auth/google")
def google_auth():
    return {"message": "Google auth route working"}


@router.get("/auth/google/callback")
def google_callback():
    return {"message": "Google callback working"}