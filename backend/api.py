from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os

# FORCE LOAD .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

from backend.routes import router
from backend.database import init_db

app = FastAPI(
    title="Financial Expense Tracker API"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "finance_secret")
)

app.include_router(router)


@app.on_event("startup")
def on_startup():
    print("GOOGLE_CLIENT_ID =", os.getenv("GOOGLE_CLIENT_ID"))
    print("DATABASE_URL =", os.getenv("DATABASE_URL"))

    try:
        init_db()
        print("Database connected successfully")
    except Exception as e:
        print("Database init failed:", e)