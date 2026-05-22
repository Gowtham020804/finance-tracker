from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class UserAuth(BaseModel):
    username: str
    password: str


@router.get("/")
def home():
    return {"message": "Financial Expense Tracker API Running"}


@router.post("/signup")
def signup(user: UserAuth):
    return {
        "message": "Signup successful",
        "username": user.username
    }


@router.post("/login")
def login(user: UserAuth):
    return {
        "message": "Login successful",
        "token": "dummy_token",
        "username": user.username
    }


@router.get("/auth/google")
def google_auth():
    return {"message": "Google auth route working"}


@router.get("/auth/google/callback")
def google_callback():
    return {"message": "Google callback working"}