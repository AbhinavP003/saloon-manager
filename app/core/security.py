"""
Core security utilities for authentication and authorization.

Includes logic for password hashing (Argon2), JWT token generation,
and credential verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# --- Setup Password Hashing (Argon2 is highly recommended) ---
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare a plain-text password with its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a high-security hash from a plain-text password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any], expires_delta: Union[timedelta, None] = None
) -> str:
    """
    Generate a JWT access token for a specific subject (usually User ID).
    Includes an expiration time to enhance security.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
