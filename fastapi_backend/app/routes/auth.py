from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.orm import Session
import time

from app.core.database import get_db
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import User

# Password hashing
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# =====================================================
# MODELS
# =====================================================

class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    email: str
    password: str


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Convert datetime to Unix timestamp (seconds since epoch)
    expire_timestamp = int(expire.timestamp())
    to_encode.update({"exp": expire_timestamp})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    return encoded_jwt


# =====================================================
# LOGIN
# =====================================================

@router.post("/login")
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    # Try to find user by email
    user = db.query(User).filter(
        User.email == request.username
    ).first()

    # If user doesn't exist, create a new one (simple auto-registration)
    if not user:
        hashed_password = get_password_hash(
            request.password
        )
        
        user = User(
            email=request.username,
            password=hashed_password
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)

    # Verify password
    elif not verify_password(
        request.password,
        user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email
    }


# =====================================================
# SIGNUP
# =====================================================

@router.post("/signup")
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        if verify_password(request.password, existing_user.password):
            access_token = create_access_token(
                data={"sub": str(existing_user.id)}
            )
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "user_id": existing_user.id,
                "email": existing_user.email,
                "message": "Account already exists. Signed in successfully.",
            }
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(request.password)
    
    new_user = User(
        email=request.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create access token
    access_token = create_access_token(
        data={"sub": str(new_user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": new_user.id,
        "email": new_user.email
    }
