"""add account tokens

Revision ID: 202606280002
Revises: 202606280001
Create Date: 2026-06-28 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202606280002"
down_revision: str | None = "202606280001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    account_token_purpose = sa.Enum(
        "email_verification",
        "password_reset",
        name="account_token_purpose",
    )
    account_token_purpose.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "account_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purpose", account_token_purpose, nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_account_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_account_tokens")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_account_tokens_token_hash")),
    )
    op.create_index(op.f("ix_account_tokens_purpose"), "account_tokens", ["purpose"], unique=False)
    op.create_index(op.f("ix_account_tokens_token_hash"), "account_tokens", ["token_hash"], unique=False)
    op.create_index(op.f("ix_account_tokens_user_id"), "account_tokens", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_account_tokens_user_id"), table_name="account_tokens")
    op.drop_index(op.f("ix_account_tokens_token_hash"), table_name="account_tokens")
    op.drop_index(op.f("ix_account_tokens_purpose"), table_name="account_tokens")
    op.drop_table("account_tokens")
    sa.Enum(name="account_token_purpose").drop(op.get_bind(), checkfirst=True)
