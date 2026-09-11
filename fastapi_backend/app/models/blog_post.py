from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BlogPost(Base):
    __tablename__ = "blog_posts"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(220), unique=True, nullable=False, index=True)
    excerpt = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="draft", server_default="draft", index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    published_at = Column(DateTime, nullable=True)

    author = relationship("User")
    comments = relationship("BlogComment", cascade="all, delete-orphan", back_populates="post")
    likes = relationship("BlogLike", cascade="all, delete-orphan", back_populates="post")


class BlogComment(Base):
    __tablename__ = "blog_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    post = relationship("BlogPost", back_populates="comments")
    user = relationship("User")


class BlogLike(Base):
    __tablename__ = "blog_likes"
    __table_args__ = (
        UniqueConstraint("post_id", "user_id", name="uq_blog_like_post_user"),
    )

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("blog_posts.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    post = relationship("BlogPost", back_populates="likes")
    user = relationship("User")