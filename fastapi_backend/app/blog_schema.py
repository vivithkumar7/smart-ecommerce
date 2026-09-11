from app.blog_database import BlogBase, blog_engine
from app.models.blog import Comment, Like, Post, User


def create_blog_tables() -> None:
    """Create the SQLite blog tables when the blog feature is initialized."""
    BlogBase.metadata.create_all(bind=blog_engine)


__all__ = ["Comment", "Like", "Post", "User", "create_blog_tables"]