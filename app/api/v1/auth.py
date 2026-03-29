"""
Authentication and User registration endpoints.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserRead

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    Public endpoint to create a new user account.
    Checks for email collision before creating.
    """
    # 1. Check for email collision
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    # 2. Hash password and Create User
    new_user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Token:
    """
    Trade email (username) and password for a JWT access token.
    Compatible with standard OAuth2 password bearer flow.
    """
    # 1. Find User
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    # 2. Verify Credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Issue Token
    access_token = create_access_token(subject=user.id)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserRead)
async def get_my_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Return the currently authenticated user's profile information."""
    return current_user
