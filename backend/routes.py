from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fake in-memory DB for now
users_db = {}


class User(BaseModel):
    username: str
    password: str


@router.get("/")
def home():
    return {"message": "Backend is running"}


@router.post("/signup")
def signup(user: User):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = pwd_context.hash(user.password)

    users_db[user.username] = {
        "username": user.username,
        "password": hashed_password,
    }

    return {"message": "Account created successfully"}


@router.post("/login")
def login(user: User):
    db_user = users_db.get(user.username)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username")

    if not pwd_context.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "message": "Login successful",
        "token": "demo_token"
    }


@router.get("/auth/google")
def google_login():
    return {"message": "Google login route working"}


@router.get("/auth/google/callback")
def google_callback():
    return {"message": "Google callback working"}