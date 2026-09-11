from datetime import datetime

from pydantic import BaseModel, Field


class BlogRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class BlogPostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class BlogCommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class BlogCommentResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    text: str
    created_at: datetime

    class Config:
        from_attributes = True


class BlogLikeResponse(BaseModel):
    liked: bool
    like_count: int