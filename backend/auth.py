import jwt
import bcrypt
from datetime import datetime, timedelta

SECRET_KEY = "finance_tracker_secret"


def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    # hashed is stored as a UTF-8 string
    return bcrypt.checkpw(password.encode(), hashed.encode("utf-8"))


def create_token(username: str) -> str:
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(days=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> str:
    """Return username if token valid, else raise Exception"""
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data.get("username")
    except Exception:
        return None