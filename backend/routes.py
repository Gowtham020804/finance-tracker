from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class UserAuth(BaseModel):
    username: str
    password: str


@router.post("/signup")
def signup(user: UserAuth):
    return {
        "message": f"User {user.username} created successfully"
    }


@router.post("/login")
def login(user: UserAuth):
    return {
        "token": "demo_token",
        "username": user.username
    }


@router.get("/")
def home():
    return {
        "message": "Backend working"
    }


@router.get("/auth/google")
def google_auth():
    return {
        "message": "Google auth route working"
    }


@router.get("/auth/google/callback")
def google_callback():
    return {
        "message": "Google callback working"
    }