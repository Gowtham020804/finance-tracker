from fastapi import APIRouter, HTTPException, Request
from starlette.responses import RedirectResponse
import logging
import traceback
import os
import backend.database as database
from backend.db_models import UserDB, ExpenseDB
from backend.models import User, Expense
from backend.auth import hash_password, verify_password, create_token, verify_token
from datetime import datetime
from fastapi import Header
from authlib.integrations.starlette_client import OAuth

router = APIRouter()

oauth = OAuth()
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.post("/signup")
def signup(user: User):
    db = database.SessionLocal()
    try:
        existing = db.query(UserDB).filter(UserDB.username == user.username).first()
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = UserDB(username=user.username, password=hash_password(user.password))
        db.add(new_user)
        db.commit()
        return {"message": "Signup successful"}
    except HTTPException:
        db.close()
        raise
    except Exception as e:
        logging.exception("Error in signup")
        db.close()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            db.close()
        except Exception:
            pass


@router.post("/login")
def login(user: User):
    db = database.SessionLocal()
    try:
        existing = db.query(UserDB).filter(UserDB.username == user.username).first()
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(user.password, existing.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        token = create_token(user.username)
        return {"token": token}
    except HTTPException:
        db.close()
        raise
    except Exception as e:
        logging.exception("Error in login")
        db.close()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            db.close()
        except Exception:
            pass


@router.post("/expense")
def add_expense(expense: Expense, authorization: str = Header(None)):
    db = database.SessionLocal()
    try:
        # Require Authorization header
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        token = authorization.split(" ")[-1]
        token_user = verify_token(token)
        if not token_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Use username from token to avoid spoofing
        user = db.query(UserDB).filter(UserDB.username == token_user).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        try:
            date_val = datetime.fromisoformat(expense.date)
        except Exception:
            date_val = None

        new_exp = ExpenseDB(
            user_id=user.id,
            amount=expense.amount,
            category=expense.category,
            description=expense.description,
            date=date_val,
        )
        db.add(new_exp)
        db.commit()
        return {"message": "Expense added"}
    finally:
        db.close()


@router.get("/expenses/{username}")
def get_expenses(username: str, authorization: str = Header(None)):
    db = database.SessionLocal()
    try:
        # Require Authorization header and ensure user matches token
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        token = authorization.split(" ")[-1]
        token_user = verify_token(token)
        if not token_user:
            raise HTTPException(status_code=401, detail="Invalid token")

        if token_user != username:
            raise HTTPException(status_code=403, detail="Forbidden")

        user = db.query(UserDB).filter(UserDB.username == username).first()
        if not user:
            return []

        rows = db.query(ExpenseDB).filter(ExpenseDB.user_id == user.id).all()
        out = []
        for r in rows:
            out.append({
                "username": username,
                "amount": r.amount,
                "category": r.category,
                "description": r.description,
                "date": r.date.isoformat() if r.date else None,
            })
        return out
    finally:
        db.close()



@router.get("/auth/google/login")
async def google_login(request: Request):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth client ID/secret not configured")
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(request, token)
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google login failed: email not provided")

        db = database.SessionLocal()
        user = db.query(UserDB).filter(UserDB.username == email).first()
        if not user:
            user = UserDB(username=email, password=hash_password(os.urandom(16).hex()))
            db.add(user)
            db.commit()
        db.close()

        app_token = create_token(email)
        redirect_to = f"{FRONTEND_URL}/?auth_token={app_token}&username={email}"
        return RedirectResponse(url=redirect_to)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
def health():
    from backend.database import engine
    try:
        conn = engine.connect()
        conn.close()
        return {"database": "ok"}
    except Exception as e:
        return {"database": "unreachable", "error": str(e)}