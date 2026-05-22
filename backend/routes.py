from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

users_db = {}


class User(BaseModel):
    username: str
    password: str


@router.get("/")
def home():
    return {"message": "Backend working"}


@router.post("/signup")
def signup(user: User):

    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    users_db[user.username] = user.password

    return {"message": "Signup successful"}


@router.post("/login")
def login(user: User):

    saved_password = users_db.get(user.username)

    if not saved_password:
        raise HTTPException(status_code=401, detail="User not found")

    if saved_password != user.password:
        raise HTTPException(status_code=401, detail="Wrong password")

    return {
        "message": "Login successful",
        "token": "demo_token"
    }


@router.get("/auth/google")
def google_auth():
    return {"message": "Google auth working"}


@router.get("/auth/google/callback")
def google_callback():
    return {"message": "Google callback working"}