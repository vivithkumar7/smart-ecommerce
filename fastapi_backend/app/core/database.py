from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

