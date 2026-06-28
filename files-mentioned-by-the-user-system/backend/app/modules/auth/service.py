from dataclasses import dataclass
from datetime import timedelta
from secrets import token_urlsafe
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import (
    create_access_token,
    ensure_active_user,
    hash_password,
    hash_token,
    normalize_email,
    now_utc,
    verify_password,
)
from app.modules.auth.models import AccountToken, AccountTokenPurpose, RefreshToken
from app.modules.auth.repository import AuthRepository
from app.modules.users.models import User, UserRole, UserStatus


class AuthError(Exception):
    pass


class DuplicateEmailError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class AccountNotActiveError(AuthError):
    pass


class InvalidRefreshTokenError(AuthError):
    pass


class InvalidAccountTokenError(AuthError):
    pass


@dataclass(frozen=True)
class AuthResult:
    user: User
    access_token: str
    refresh_token: str
    expires_in: int


@dataclass(frozen=True)
class RegistrationResult:
    user: User
    verification_token: str


class AuthService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.repository = AuthRepository(session)

    def register_user(
        self,
        *,
        email: str,
        password: str,
        display_name: str,
        role: UserRole,
    ) -> RegistrationResult:
        normalized_email = normalize_email(email)
        if self.repository.get_user_by_email(normalized_email) is not None:
            raise DuplicateEmailError("Email is already registered")

        user = User(
            email=normalized_email,
            password_hash=hash_password(password, self.settings),
            display_name=display_name.strip(),
            role=role,
            status=UserStatus.pending_verification,
        )
        self.repository.add_user(user)
        verification_token = self._create_account_token(
            user,
            AccountTokenPurpose.email_verification,
            ttl=timedelta(days=1),
        )
        self.session.commit()
        return RegistrationResult(user=user, verification_token=verification_token)

    def login(self, *, email: str, password: str) -> AuthResult:
        normalized_email = normalize_email(email)
        user = self.repository.get_user_by_email(normalized_email)
        if user is None or not verify_password(password, user.password_hash, self.settings):
            raise InvalidCredentialsError("Invalid email or password")

        try:
            ensure_active_user(user)
        except PermissionError:
            raise AccountNotActiveError("Email verification required") from None

        result = self._issue_token_pair(user)
        self.session.commit()
        return result

    def refresh(self, refresh_token: str) -> AuthResult:
        token_hash = hash_token(refresh_token, self.settings)
        stored_token = self.repository.get_refresh_token_by_hash(token_hash)
        current_time = now_utc()
        if (
            stored_token is None
            or stored_token.revoked_at is not None
            or stored_token.expires_at <= current_time
        ):
            raise InvalidRefreshTokenError("Refresh token is invalid")

        user = self.repository.get_user_by_id(stored_token.user_id)
        if user is None:
            raise InvalidRefreshTokenError("Refresh token user no longer exists")

        ensure_active_user(user)
        self.repository.revoke_refresh_token(stored_token, current_time)
        result = self._issue_token_pair(user, family_id=stored_token.family_id)
        self.session.commit()
        return result

    def logout(self, refresh_token: str) -> None:
        token_hash = hash_token(refresh_token, self.settings)
        stored_token = self.repository.get_refresh_token_by_hash(token_hash)
        if stored_token is not None and stored_token.revoked_at is None:
            self.repository.revoke_refresh_token(stored_token, now_utc())
        self.session.commit()

    def verify_email(self, token: str) -> User:
        account_token = self._get_valid_account_token(
            token,
            AccountTokenPurpose.email_verification,
        )
        user = self.repository.get_user_by_id(account_token.user_id)
        if user is None:
            raise InvalidAccountTokenError("Verification token user no longer exists")

        current_time = now_utc()
        self.repository.activate_user(user, current_time)
        self.repository.mark_account_token_used(account_token, current_time)
        self.session.commit()
        return user

    def request_email_verification(self, email: str) -> str | None:
        user = self.repository.get_user_by_email(normalize_email(email))
        if user is None or user.email_verified_at is not None:
            self.session.commit()
            return None

        token = self._create_account_token(
            user,
            AccountTokenPurpose.email_verification,
            ttl=timedelta(days=1),
        )
        self.session.commit()
        return token

    def request_password_reset(self, email: str) -> str | None:
        user = self.repository.get_user_by_email(normalize_email(email))
        if user is None:
            self.session.commit()
            return None

        token = self._create_account_token(
            user,
            AccountTokenPurpose.password_reset,
            ttl=timedelta(hours=1),
        )
        self.session.commit()
        return token

    def confirm_password_reset(self, token: str, new_password: str) -> None:
        account_token = self._get_valid_account_token(
            token,
            AccountTokenPurpose.password_reset,
        )
        user = self.repository.get_user_by_id(account_token.user_id)
        if user is None:
            raise InvalidAccountTokenError("Reset token user no longer exists")

        current_time = now_utc()
        user.password_hash = hash_password(new_password, self.settings)
        self.repository.mark_account_token_used(account_token, current_time)
        self.repository.revoke_user_refresh_tokens(user.id, current_time)
        self.session.commit()

    def _issue_token_pair(self, user: User, family_id: UUID | None = None) -> AuthResult:
        raw_refresh_token = token_urlsafe(48)
        refresh_token = RefreshToken(
            user_id=user.id,
            family_id=family_id or uuid4(),
            token_hash=hash_token(raw_refresh_token, self.settings),
            expires_at=now_utc() + timedelta(days=self.settings.refresh_token_ttl_days),
        )
        self.repository.add_refresh_token(refresh_token)
        return AuthResult(
            user=user,
            access_token=create_access_token(user, self.settings),
            refresh_token=raw_refresh_token,
            expires_in=self.settings.access_token_ttl_seconds,
        )

    def _create_account_token(
        self,
        user: User,
        purpose: AccountTokenPurpose,
        ttl: timedelta,
    ) -> str:
        raw_token = token_urlsafe(48)
        account_token = AccountToken(
            user_id=user.id,
            purpose=purpose,
            token_hash=hash_token(raw_token, self.settings),
            expires_at=now_utc() + ttl,
        )
        self.repository.add_account_token(account_token)
        return raw_token

    def _get_valid_account_token(
        self,
        token: str,
        purpose: AccountTokenPurpose,
    ) -> AccountToken:
        account_token = self.repository.get_account_token_by_hash(
            hash_token(token, self.settings),
            purpose,
        )
        current_time = now_utc()
        if (
            account_token is None
            or account_token.used_at is not None
            or account_token.expires_at <= current_time
        ):
            raise InvalidAccountTokenError("Token is invalid or expired")
        return account_token
