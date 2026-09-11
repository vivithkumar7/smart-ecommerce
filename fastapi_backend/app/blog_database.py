from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


BLOG_DATABASE_URL = f"sqlite:///{Path(__file__).resolve().parents[1] / 'blog.db'}"

blog_engine = create_engine(
    BLOG_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

BlogBase = declarative_base()
BlogSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=blog_engine,
)


def get_blog_db():
    db = BlogSessionLocal()
    try:
        yield db
    finally:
        db.close()