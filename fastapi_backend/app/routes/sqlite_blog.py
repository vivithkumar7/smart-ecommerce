from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from jose import jwt
from sqlalchemy.orm import Session

from app.blog_database import get_blog_db
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.dependencies.blog_auth import get_blog_current_user
from app.models.blog import Comment, Like, Post, User
from app.schemas.sqlite_blog import (
    BlogCommentCreate,
    BlogCommentResponse,
    BlogLikeResponse,
    BlogPostCreate,
    BlogPostResponse,
)
from app.services.notifications import send_notification_email


router = APIRouter(prefix="/posts", tags=["SQLite Blog"])


def blog_token(user: User) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user.id), "blog_user": True, "exp": int(expires.timestamp())},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def get_post(post_id: int, db: Session) -> Post:
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


def notify_author(background_tasks: BackgroundTasks, post: Post, subject: str, message: str):
    if post.author:
        background_tasks.add_task(send_notification_email, post.author.email, subject, message)


@router.get("", response_model=list[BlogPostResponse])
def list_posts(db: Session = Depends(get_blog_db)):
    return db.query(Post).order_by(Post.created_at.desc(), Post.id.desc()).all()


@router.get("/mine", response_model=list[BlogPostResponse])
def list_my_posts(
    current_user=Depends(get_blog_current_user),
    db: Session = Depends(get_blog_db),
):
    return db.query(Post).filter(Post.author_id == current_user.id).order_by(Post.created_at.desc()).all()


@router.get("/{post_id}", response_model=BlogPostResponse)
def read_post(post_id: int, db: Session = Depends(get_blog_db)):
    return get_post(post_id, db)


@router.post("", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: BlogPostCreate,
    current_user=Depends(get_blog_current_user),
    db: Session = Depends(get_blog_db),
):
    post = Post(title=post_data.title.strip(), content=post_data.content.strip(), author_id=current_user.id)
    if not post.title or not post.content:
        raise HTTPException(status_code=422, detail="Title and content cannot be empty")
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=BlogPostResponse)
@router.patch("/{post_id}", response_model=BlogPostResponse)
def update_post(
    post_id: int,
    post_data: BlogPostCreate,
    current_user=Depends(get_blog_current_user),
    db: Session = Depends(get_blog_db),
):
    post = get_post(post_id, db)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the post owner can update this post")
    post.title = post_data.title.strip()
    post.content = post_data.content.strip()
    if not post.title or not post.content:
        raise HTTPException(status_code=422, detail="Title and content cannot be empty")
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user=Depends(get_blog_current_user),
    db: Session = Depends(get_blog_db),
):
    post = get_post(post_id, db)
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the post owner can delete this post")
    db.delete(post)
    db.commit()


@router.get("/{post_id}/comments", response_model=list[BlogCommentResponse])
def list_comments(post_id: int, db: Session = Depends(get_blog_db)):
    get_post(post_id, db)
    return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()


@router.post("/{post_id}/comments", response_model=BlogCommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: int,
    comment_data: BlogCommentCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_blog_current_user),
    db: Session = Depends(get_blog_db),
):
    post = get_post(post_id, db)
    text = comment_data.text.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Comment cannot be empty")
    comment = Comment(post_id=post.id, user_id=current_user.id, text=text)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    if post.author_id != current_user.id:
        notify_author(background_tasks, post, "New blog comment", f"{current_user.username} commented on '{post.title}'.")
    return comment


@router.post("/{post_id}/like", response_model=BlogLikeResponse)
def like_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_blog_current_user),
    db: Session = Depends(get_blog_db),
):
    post = get_post(post_id, db)
    like = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first()
    if not like:
        db.add(Like(post_id=post.id, user_id=current_user.id))
        db.commit()
        if post.author_id != current_user.id:
            notify_author(background_tasks, post, "New blog like", f"{current_user.username} liked '{post.title}'.")
    return BlogLikeResponse(liked=True, like_count=db.query(Like).filter(Like.post_id == post.id).count())


@router.delete("/{post_id}/like", response_model=BlogLikeResponse)
def unlike_post(
    post_id: int,
    current_user=Depends(get_blog_current_user),
    db: Session = Depends(get_blog_db),
):
    post = get_post(post_id, db)
    like = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.id).first()
    if like:
        db.delete(like)
        db.commit()
    return BlogLikeResponse(liked=False, like_count=db.query(Like).filter(Like.post_id == post.id).count())