from typing import Annotated

from fastapi import APIRouter, Body, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import (
    AccessTokenResponse,
    EmailRequest,
    AuthTokenResponse,
    LoginRequest,
    MessageResponse,
    PasswordResetConfirmRequest,
    RefreshRequest,
    RegisterRequest,
    RegistrationResponse,
    VerifyEmailRequest,
    UserResponse,
)
from app.modules.auth.service import (
    AccountNotActiveError,
    AuthResult,
    AuthService,
    DuplicateEmailError,
    InvalidCredentialsError,
    InvalidAccountTokenError,
    InvalidRefreshTokenError,
)
from app.modules.users.models import User, UserRole


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_auth_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(session, settings)


def set_refresh_cookie(response: Response, result: AuthResult, settings: Settings) -> None:
    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token,
        httponly=True,
        secure=not settings.is_development,
        samesite="lax",
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def token_response(result: AuthResult) -> AuthTokenResponse:
    return AuthTokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        expires_in=result.expires_in,
        user=UserResponse.model_validate(result.user),
    )


@router.post("/register/teacher", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_teacher(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationResponse:
    try:
        result = service.register_user(
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
            role=UserRole.teacher,
        )
    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        ) from None

    return RegistrationResponse(
        message="Registration created. Verify your email before logging in.",
        email=result.user.email,
        verification_token=result.verification_token if settings.is_development else None,
    )


@router.post("/register/student", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
def register_student(
    payload: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationResponse:
    try:
        result = service.register_user(
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
            role=UserRole.student,
        )
    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        ) from None

    return RegistrationResponse(
        message="Registration created. Verify your email before logging in.",
        email=result.user.email,
        verification_token=result.verification_token if settings.is_development else None,
    )


@router.post("/login", response_model=AuthTokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthTokenResponse:
    try:
        result = service.login(email=payload.email, password=payload.password)
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from None
    except AccountNotActiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required",
        ) from None

    set_refresh_cookie(response, result, settings)
    return token_response(result)


@router.post("/verify-email", response_model=MessageResponse)
def verify_email(
    payload: VerifyEmailRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    try:
        service.verify_email(payload.token)
    except InvalidAccountTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token is invalid or expired",
        ) from None

    return MessageResponse(message="Email verified")


@router.post("/resend-verification", response_model=RegistrationResponse)
def resend_verification(
    payload: EmailRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationResponse:
    token = service.request_email_verification(payload.email)
    return RegistrationResponse(
        message="If the account requires verification, a new email has been queued.",
        email=payload.email,
        verification_token=token if settings.is_development else None,
    )


@router.post("/password-reset/request", response_model=RegistrationResponse)
def request_password_reset(
    payload: EmailRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationResponse:
    token = service.request_password_reset(payload.email)
    return RegistrationResponse(
        message="If the account exists, a password reset email has been queued.",
        email=payload.email,
        verification_required=False,
        verification_token=token if settings.is_development else None,
    )


@router.post("/password-reset/confirm", response_model=MessageResponse)
def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> MessageResponse:
    try:
        service.confirm_password_reset(payload.token, payload.new_password)
    except InvalidAccountTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is invalid or expired",
        ) from None

    return MessageResponse(message="Password reset complete")


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
    payload: Annotated[RefreshRequest | None, Body()] = None,
    refresh_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> AccessTokenResponse:
    refresh_token = payload.refresh_token if payload is not None else refresh_cookie
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    try:
        result = service.refresh(refresh_token)
    except (InvalidRefreshTokenError, PermissionError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from None

    set_refresh_cookie(response, result, settings)
    return AccessTokenResponse(
        access_token=result.access_token,
        expires_in=result.expires_in,
    )


@router.post("/logout", response_model=MessageResponse)
def logout(
    response: Response,
    service: Annotated[AuthService, Depends(get_auth_service)],
    payload: Annotated[RefreshRequest | None, Body()] = None,
    refresh_cookie: Annotated[str | None, Cookie(alias="refresh_token")] = None,
) -> MessageResponse:
    refresh_token = payload.refresh_token if payload is not None else refresh_cookie
    if refresh_token is not None:
        service.logout(refresh_token)

    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(current_user)
