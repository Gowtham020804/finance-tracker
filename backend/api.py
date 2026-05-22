from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os

# Load .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Import routes
from backend.routes import router

# Import database init
from backend.database import init_db

# Create FastAPI app
app = FastAPI(
    title="Financial Expense Tracker API"
)

# Session middleware for Google OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "finance_secret")
)

# Include ALL routes
app.include_router(router)

# Root route
@app.get("/")
def home():
    return {"message": "Financial Expense Tracker API Running"}

# Startup event
@app.on_event("startup")
def on_startup():
    print("GOOGLE_CLIENT_ID =", os.getenv("GOOGLE_CLIENT_ID"))
    print("DATABASE_URL =", os.getenv("DATABASE_URL"))

    try:
        init_db()
        print("Database connected successfully")
    except Exception as e:
        print("Database init failed:", e)