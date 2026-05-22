from fastapi import APIRouter, HTTPException, Request, Header
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

import logging
import traceback
import os

# LOAD .env FILE
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

import backend.database as database
from backend.db_models import UserDB, ExpenseDB
from backend.models import User, Expense
from backend.auth import (
    hash_password,
    verify_password,
    create_token,
    verify_token
)

router = APIRouter()

# ENV VARIABLES
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:8501"
)

# GOOGLE OAUTH
oauth = OAuth()

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

# =====================================================
# SIGNUP
# =====================================================

@router.post("/signup")
def signup(user: User):

    db = database.SessionLocal()

    try:

        existing = db.query(UserDB).filter(
            UserDB.username == user.username
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        new_user = UserDB(
            username=user.username,
            password=hash_password(user.password)
        )

        db.add(new_user)
        db.commit()

        return {
            "message": "Signup successful"
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.exception("Signup error")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()


# =====================================================
# LOGIN
# =====================================================

@router.post("/login")
def login(user: User):

    db = database.SessionLocal()

    try:

        existing = db.query(UserDB).filter(
            UserDB.username == user.username
        ).first()

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if not verify_password(
            user.password,
            existing.password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid password"
            )

        token = create_token(user.username)

        return {
            "token": token
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.exception("Login error")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()


# =====================================================
# ADD EXPENSE
# =====================================================

@router.post("/expense")
def add_expense(
    expense: Expense,
    authorization: str = Header(None)
):

    db = database.SessionLocal()

    try:

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization header"
            )

        token = authorization.split(" ")[-1]

        token_user = verify_token(token)

        if not token_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = db.query(UserDB).filter(
            UserDB.username == token_user
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        try:
            date_val = datetime.fromisoformat(expense.date)
        except Exception:
            date_val = None

        new_expense = ExpenseDB(
            user_id=user.id,
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            date=date_val,
        )

        db.add(new_expense)
        db.commit()

        return {
            "message": "Expense added successfully"
        }

    except HTTPException:
        raise

    except Exception as e:
        logging.exception("Expense error")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()


# =====================================================
# GET EXPENSES
# =====================================================

@router.get("/expenses/{username}")
def get_expenses(
    username: str,
    authorization: str = Header(None)
):

    db = database.SessionLocal()

    try:

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Missing Authorization header"
            )

        token = authorization.split(" ")[-1]

        token_user = verify_token(token)

        if not token_user:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        if token_user != username:
            raise HTTPException(
                status_code=403,
                detail="Forbidden"
            )

        user = db.query(UserDB).filter(
            UserDB.username == username
        ).first()

        if not user:
            return []

        expenses = db.query(ExpenseDB).filter(
            ExpenseDB.user_id == user.id
        ).all()

        result = []

        for exp in expenses:
            result.append({
                "username": username,
                "amount": exp.amount,
                "category": exp.category,
                "description": exp.description,
                "date": exp.date.isoformat() if exp.date else None,
            })

        return result

    finally:
        db.close()


# =====================================================
# GOOGLE LOGIN
# =====================================================

@router.get("/auth/google/login")
async def google_login(request: Request):

    try:

        if not GOOGLE_CLIENT_ID:
            raise HTTPException(
                status_code=500,
                detail="Google Client ID missing"
            )

        if not GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=500,
                detail="Google Client Secret missing"
            )

        redirect_uri = request.url_for(
            "google_callback"
        )

        return await oauth.google.authorize_redirect(
            request,
            redirect_uri
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================================
# GOOGLE CALLBACK
# =====================================================

@router.get("/auth/google/callback")
async def google_callback(request: Request):

    db = database.SessionLocal()

    try:

        token = await oauth.google.authorize_access_token(
            request
        )

        # GET USER INFO
        user_info = token.get("userinfo")

        # FALLBACK IF userinfo MISSING
        if not user_info:

            resp = await oauth.google.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                token=token
            )

            user_info = resp.json()

        email = user_info.get("email")

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Google email not found"
            )

        # CHECK USER
        user = db.query(UserDB).filter(
            UserDB.username == email
        ).first()

        # CREATE USER IF NOT EXISTS
        if not user:

            random_password = os.urandom(16).hex()

            user = UserDB(
                username=email,
                password=hash_password(random_password)
            )

            db.add(user)
            db.commit()

        # CREATE JWT TOKEN
        app_token = create_token(email)

        # REDIRECT TO STREAMLIT DASHBOARD
        redirect_url = (
            f"{FRONTEND_URL}"
            f"/?auth_token={app_token}"
            f"&username={email}"
        )

        return RedirectResponse(
            url=redirect_url
        )

    except Exception as e:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        db.close()


# =====================================================
# HEALTH CHECK
# =====================================================

@router.get("/health")
def health():

    from backend.database import engine

    try:

        conn = engine.connect()
        conn.close()

        return {
            "database": "ok"
        }

    except Exception as e:

        return {
            "database": "unreachable",
            "error": str(e)
        }