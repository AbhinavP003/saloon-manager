"""
Pydantic schemas for User domain.
"""

from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Fields shared across all User variants."""

    email: EmailStr
    full_name: Annotated[Optional[str], Field(max_length=255, examples=["John Doe"])]


class UserCreate(UserBase):
    """Payload to create a new user account."""

    password: Annotated[str, Field(min_length=8, max_length=100)]
    role: Annotated[UserRole, Field(default=UserRole.CUSTOMER)]


class UserRead(UserBase):
    """User representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    is_active: bool


class Token(BaseModel):
    """Payload for successful login (The "Badge")."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Internal data extracted from the JWT."""

    sub: Optional[str] = None
