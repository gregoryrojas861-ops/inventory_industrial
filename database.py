import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_PATH = BASE_DIR / "inventario.db"


def build_database_url() -> str:
    return os.getenv("DATABASE_URL") or f"sqlite:///{DB_PATH}"


DATABASE_URL = build_database_url()
APP_ENV = os.getenv("APP_ENV", "development")


def is_demo_mode() -> bool:
    app_env = (os.getenv("APP_ENV", APP_ENV) or "development").strip().lower()
    demo_mode = (os.getenv("DEMO_MODE", "false") or "false").strip().lower()
    return app_env != "production" and demo_mode not in {"0", "false", "no", "off", ""}


SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if APP_ENV == "production":
        raise RuntimeError("SECRET_KEY must be configured in production environments.")
    SECRET_KEY = "development-secret-change-me"

class Base(DeclarativeBase):
    pass

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

def init_db():
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
