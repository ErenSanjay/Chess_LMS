from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.modules.auth.models import AccountToken, AccountTokenPurpose, RefreshToken
from app.modules.users.models import User, UserStatus


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_user_by_id(self, user_id: UUID) -> User | None:
        return self.session.get(User, user_id)

    def add_user(self, user: User) -> User:
        self.session.add(user)
        self.session.flush()
        return user

    def add_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        self.session.add(refresh_token)
        self.session.flush()
        return refresh_token

    def add_account_token(self, account_token: AccountToken) -> AccountToken:
        self.session.add(account_token)
        self.session.flush()
        return account_token

    def get_refresh_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.session.scalar(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )

    def get_account_token_by_hash(
        self,
        token_hash: str,
        purpose: AccountTokenPurpose,
    ) -> AccountToken | None:
        return self.session.scalar(
            select(AccountToken)
            .where(AccountToken.token_hash == token_hash)
            .where(AccountToken.purpose == purpose)
        )

    def revoke_refresh_token(self, refresh_token: RefreshToken, revoked_at: datetime) -> None:
        refresh_token.revoked_at = revoked_at
        self.session.flush()

    def revoke_refresh_token_family(self, family_id: UUID, revoked_at: datetime) -> None:
        self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )

    def revoke_user_refresh_tokens(self, user_id: UUID, revoked_at: datetime) -> None:
        self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )

    def activate_user(self, user: User, verified_at: datetime) -> None:
        user.status = UserStatus.active
        user.email_verified_at = verified_at
        self.session.flush()

    def mark_account_token_used(self, account_token: AccountToken, used_at: datetime) -> None:
        account_token.used_at = used_at
        self.session.flush()
