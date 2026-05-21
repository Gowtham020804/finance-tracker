from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

# Read database URL from environment (e.g., .env) - common names: DATABASE_URL or POSTGRES_URI
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URI") or os.getenv("DATABASE_URI")

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
else:
    # Fallback to local SQLite for development when no DATABASE_URL provided
    sqlite_url = f"sqlite:///./local_dev.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    # import models here to ensure they are registered on Base
    from backend import db_models
    global engine, SessionLocal
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # If initial DB is unreachable (networked DB), fall back to local SQLite for development
        print("Primary database unreachable, falling back to local SQLite:", e)
        sqlite_url = f"sqlite:///./local_dev.db"
        engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
