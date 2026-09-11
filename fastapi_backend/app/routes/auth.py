from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field, model_validator
from passlib.context import CryptContext
from jose import jwt
from sqlalchemy.orm import Session
import time

from app.core.database import get_db
from app.blog_database import get_blog_db
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import User
from app.models.blog import User as BlogUser

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
    username: str | None = Field(None, min_length=3, max_length=255)
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def require_login_identifier(self):
        if not self.username and not self.email:
            raise ValueError("username or email is required")
        return self


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class BlogRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


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
    , blog_db: Session = Depends(get_blog_db)
):
    login_identifier = request.username or request.email
    blog_user = blog_db.query(BlogUser).filter(
        (BlogUser.email == login_identifier) | (BlogUser.username == login_identifier),
    ).first()
    if blog_user:
        if not blog_user.verify_password(request.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {
            "access_token": create_access_token(data={"sub": str(blog_user.id), "blog_user": True}),
            "token_type": "bearer",
            "user_id": blog_user.id,
            "username": blog_user.username,
            "email": blog_user.email,
        }

    # Try to find user by email
    user = db.query(User).filter(
        User.email == login_identifier
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


@router.post("/register")
def register_blog_user(
    request: BlogRegisterRequest,
    db: Session = Depends(get_blog_db),
):
    existing_user = db.query(BlogUser).filter(
        (BlogUser.email == request.email) | (BlogUser.username == request.username),
    ).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already registered")

    user = BlogUser(
        username=request.username,
        email=request.email,
        password=request.password,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "access_token": create_access_token(data={"sub": str(user.id), "blog_user": True}),
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
    }
