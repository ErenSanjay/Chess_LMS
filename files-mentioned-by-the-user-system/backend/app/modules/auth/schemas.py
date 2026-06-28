from datetime import datetime
from uuid import UUID

import re

from pydantic import BaseModel, Field, field_validator

from app.modules.users.models import UserRole, UserStatus


EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=10, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("Invalid email address")
        return normalized


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("Invalid email address")
        return normalized


class RefreshRequest(BaseModel):
    refresh_token: str | None = Field(default=None, min_length=32)


class EmailRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not EMAIL_PATTERN.match(normalized):
            raise ValueError("Invalid email address")
        return normalized


class VerifyEmailRequest(BaseModel):
    token: str = Field(min_length=32)


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(min_length=32)
    new_password: str = Field(min_length=10, max_length=128)


class UserResponse(BaseModel):
    id: UUID
    email: str
    role: UserRole
    display_name: str
    status: UserStatus
    email_verified_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class MessageResponse(BaseModel):
    message: str


class RegistrationResponse(BaseModel):
    message: str
    email: str
    verification_required: bool = True
    verification_token: str | None = None
