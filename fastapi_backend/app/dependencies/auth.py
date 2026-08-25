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


bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except (JWTError, ValueError, TypeError):

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.id == int(user_id)
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Session expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="This account is deactivated.",
        )

    return user