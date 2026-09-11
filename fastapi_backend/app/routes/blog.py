import re
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.blog_post import BlogComment, BlogLike, BlogPost
from app.schemas.blog import (
    BlogCommentCreate,
    BlogCommentResponse,
    BlogLikeResponse,
    BlogPostCreate,
    BlogPostResponse,
    BlogPostUpdate,
)
from app.services.notifications import create_notification


router = APIRouter(tags=["Blog"])


def make_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "post"


def unique_slug(title: str, db: Session, post_id: int | None = None) -> str:
    base_slug = make_slug(title)
    slug = base_slug
    suffix = 2
    while db.query(BlogPost.id).filter(
        BlogPost.slug == slug,
        BlogPost.id != post_id if post_id is not None else True,
    ).first():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


def can_manage(post: BlogPost, current_user) -> bool:
    return post.author_id == current_user.id


def get_published_post(post_id: int, db: Session) -> BlogPost:
    post = db.query(BlogPost).filter(
        BlogPost.id == post_id,
        BlogPost.status == "published",
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post


@router.get("", response_model=list[BlogPostResponse])
def list_posts(
    search: str | None = None,
    category: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(BlogPost).filter(BlogPost.status == "published")
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(BlogPost.title.ilike(term) | BlogPost.content.ilike(term))
    if category:
        query = query.filter(BlogPost.category == category)
    return query.order_by(BlogPost.published_at.desc(), BlogPost.id.desc()).offset(skip).limit(limit).all()


@router.get("/mine", response_model=list[BlogPostResponse])
def list_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(BlogPost).filter(
        BlogPost.author_id == current_user.id,
    ).order_by(BlogPost.updated_at.desc(), BlogPost.id.desc()).offset(skip).limit(limit).all()


@router.get("/manage", response_model=list[BlogPostResponse])
def list_managed_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(BlogPost)
    if current_user.role.lower() != "admin":
        query = query.filter(BlogPost.author_id == current_user.id)
    return query.order_by(BlogPost.updated_at.desc(), BlogPost.id.desc()).offset(skip).limit(limit).all()


@router.get("/{post_id}/comments", response_model=list[BlogCommentResponse])
def list_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    get_published_post(post_id, db)
    return db.query(BlogComment).filter(
        BlogComment.post_id == post_id,
    ).order_by(BlogComment.created_at.asc()).offset(skip).limit(limit).all()


@router.post("/{post_id}/comments", response_model=BlogCommentResponse, status_code=status.HTTP_201_CREATED)
def add_comment(
    post_id: int,
    comment_data: BlogCommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = get_published_post(post_id, db)
    comment = BlogComment(
        post_id=post.id,
        user_id=current_user.id,
        content=comment_data.content.strip(),
    )
    if not comment.content:
        raise HTTPException(status_code=422, detail="Comment content cannot be empty")
    db.add(comment)
    db.commit()
    db.refresh(comment)

    if post.author_id != current_user.id:
        create_notification(
            db,
            post.author,
            "blog_comment",
            f"{current_user.email} commented on your post '{post.title}'.",
            event_key=f"blog-comment-{comment.id}",
            event_name="blog_comment_created",
            background_tasks=background_tasks,
        )
    return comment


@router.delete("/{post_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    comment = db.query(BlogComment).filter(
        BlogComment.id == comment_id,
        BlogComment.post_id == post_id,
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id and current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="You cannot delete this comment")
    db.delete(comment)
    db.commit()


@router.post("/{post_id}/like", response_model=BlogLikeResponse)
def like_post(
    post_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = get_published_post(post_id, db)
    existing_like = db.query(BlogLike).filter(
        BlogLike.post_id == post.id,
        BlogLike.user_id == current_user.id,
    ).first()
    if not existing_like:
        new_like = BlogLike(post_id=post.id, user_id=current_user.id)
        db.add(new_like)
        db.commit()
        db.refresh(new_like)
        if post.author_id != current_user.id:
            create_notification(
                db,
                post.author,
                "blog_like",
                f"{current_user.email} liked your post '{post.title}'.",
                event_key=f"blog-like-{new_like.id}",
                event_name="blog_post_liked",
                background_tasks=background_tasks,
            )
    return BlogLikeResponse(
        liked=True,
        like_count=db.query(BlogLike).filter(BlogLike.post_id == post.id).count(),
    )


@router.delete("/{post_id}/like", response_model=BlogLikeResponse)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = get_published_post(post_id, db)
    like = db.query(BlogLike).filter(
        BlogLike.post_id == post.id,
        BlogLike.user_id == current_user.id,
    ).first()
    if like:
        db.delete(like)
        db.commit()
    return BlogLikeResponse(
        liked=False,
        like_count=db.query(BlogLike).filter(BlogLike.post_id == post.id).count(),
    )


@router.get("/{slug}", response_model=BlogPostResponse)
def get_post(slug: str, db: Session = Depends(get_db)):
    post = db.query(BlogPost).filter(
        BlogPost.slug == slug,
        BlogPost.status == "published",
    ).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post


@router.post("", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = BlogPost(
        author_id=current_user.id,
        title=post_data.title,
        slug=unique_slug(post_data.title, db),
        excerpt=post_data.excerpt,
        content=post_data.content,
        category=post_data.category,
        status=post_data.status,
        published_at=datetime.utcnow() if post_data.status == "published" else None,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.patch("/{post_id}", response_model=BlogPostResponse)
def update_post(
    post_id: int,
    post_data: BlogPostUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    if not can_manage(post, current_user):
        raise HTTPException(status_code=403, detail="You cannot manage this blog post")

    changes = post_data.model_dump(exclude_unset=True)
    if "title" in changes and changes["title"] != post.title:
        post.slug = unique_slug(changes["title"], db, post.id)
    if "status" in changes:
        post.published_at = datetime.utcnow() if changes["status"] == "published" else None
    for field, value in changes.items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    if not can_manage(post, current_user):
        raise HTTPException(status_code=403, detail="You cannot manage this blog post")
    db.delete(post)
    db.commit()