from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    status: str = Field("draft", pattern="^(draft|published)$")


class BlogPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    excerpt: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, pattern="^(draft|published)$")


class BlogPostResponse(BaseModel):
    id: int
    author_id: int
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    category: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogCommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class BlogCommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogLikeResponse(BaseModel):
    liked: bool
    like_count: int