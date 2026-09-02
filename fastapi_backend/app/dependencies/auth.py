from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import (
    SECRET_KEY,
    ALGORITHM
)
from app.models.user import User


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    if not credentials:
        return None

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
    except (JWTError, ValueError, TypeError):
        return None

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()
    if not user:
        return None

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="This account is deactivated.",
        )

    return user


def get_current_user(
    user: User | None = Depends(get_current_user_optional),
):
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user