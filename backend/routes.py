from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from jose import jwt
import os

router = APIRouter()

# =========================
# ENV VARIABLES
# =========================
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SECRET_KEY", "secret")

# IMPORTANT:
# Replace with your REAL Streamlit URL
FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "https://finance-tracker-nsh5huggmvaarbbzappy2vv.streamlit.app"
)

# IMPORTANT:
# Replace with your REAL Render backend URL
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "https://finance-tracker-mv0i.onrender.com"
)

# =========================
# OAUTH SETUP
# =========================
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

# =========================
# GOOGLE LOGIN
# =========================
@router.get("/auth/google")
async def auth_google(request: Request):

    redirect_uri = f"{BACKEND_URL}/auth/google/callback"

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )

# =========================
# GOOGLE CALLBACK
# =========================
@router.get("/auth/google/callback")
async def auth_google_callback(request: Request):

    try:
        token = await oauth.google.authorize_access_token(request)

        user_info = token.get("userinfo")

        if not user_info:
            raise HTTPException(status_code=400, detail="userinfo missing")

        email = user_info.get("email")

        if not email:
            raise HTTPException(status_code=400, detail="email missing")

        jwt_token = jwt.encode(
            {"sub": email},
            SECRET_KEY,
            algorithm="HS256"
        )

        return RedirectResponse(
            url=f"{FRONTEND_URL}/?auth_token={jwt_token}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))