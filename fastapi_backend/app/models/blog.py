from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from passlib.context import CryptContext

from app.blog_database import BlogBase


password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class User(BlogBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        raw_password = kwargs.get("password")
        if raw_password and not raw_password.startswith("$pbkdf2-sha256$"):
            kwargs["password"] = password_context.hash(raw_password)
        super().__init__(**kwargs)

    def verify_password(self, raw_password: str) -> bool:
        return password_context.verify(raw_password, self.password)


class Post(BlogBase):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")


class Comment(BlogBase):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, server_default=func.now(), nullable=False)

    post = relationship("Post", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Like(BlogBase):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_like_post_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    post = relationship("Post", back_populates="likes")
    user = relationship("User", back_populates="likes")