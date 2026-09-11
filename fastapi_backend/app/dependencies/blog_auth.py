from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.blog_database import get_blog_db
from app.core.config import ALGORITHM, SECRET_KEY
from app.models.blog import User


blog_bearer = HTTPBearer(auto_error=False)


def get_blog_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(blog_bearer),
    db: Session = Depends(get_blog_db),
):
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("blog_user") is not True or not payload.get("sub"):
            raise ValueError
        user_id = int(payload["sub"])
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid blog token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Blog user not found")
    return user