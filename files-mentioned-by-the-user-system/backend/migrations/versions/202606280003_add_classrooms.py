"""add classrooms

Revision ID: 202606280003
Revises: 202606280002
Create Date: 2026-06-28 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "202606280003"
down_revision: str | None = "202606280002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    classroom_status = sa.Enum("active", "archived", name="classroom_status")
    classroom_member_role = sa.Enum("teacher", "student", name="classroom_member_role")
    classroom_membership_status = sa.Enum("active", "removed", name="classroom_membership_status")
    classroom_status.create(op.get_bind(), checkfirst=True)
    classroom_member_role.create(op.get_bind(), checkfirst=True)
    classroom_membership_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "classrooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("join_code_hash", sa.String(length=64), nullable=False),
        sa.Column("status", classroom_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["teacher_id"],
            ["users.id"],
            name=op.f("fk_classrooms_teacher_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_classrooms")),
        sa.UniqueConstraint("join_code_hash", name=op.f("uq_classrooms_join_code_hash")),
    )
    op.create_index(op.f("ix_classrooms_join_code_hash"), "classrooms", ["join_code_hash"], unique=False)
    op.create_index(op.f("ix_classrooms_teacher_id"), "classrooms", ["teacher_id"], unique=False)

    op.create_table(
        "classroom_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("classroom_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", classroom_member_role, nullable=False),
        sa.Column("status", classroom_membership_status, nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["classroom_id"],
            ["classrooms.id"],
            name=op.f("fk_classroom_memberships_classroom_id_classrooms"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_classroom_memberships_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_classroom_memberships")),
        sa.UniqueConstraint(
            "classroom_id",
            "user_id",
            name="uq_classroom_memberships_classroom_id_user_id",
        ),
    )
    op.create_index(
        op.f("ix_classroom_memberships_classroom_id"),
        "classroom_memberships",
        ["classroom_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_classroom_memberships_user_id"),
        "classroom_memberships",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_classroom_memberships_user_id"), table_name="classroom_memberships")
    op.drop_index(op.f("ix_classroom_memberships_classroom_id"), table_name="classroom_memberships")
    op.drop_table("classroom_memberships")
    op.drop_index(op.f("ix_classrooms_teacher_id"), table_name="classrooms")
    op.drop_index(op.f("ix_classrooms_join_code_hash"), table_name="classrooms")
    op.drop_table("classrooms")
    sa.Enum(name="classroom_membership_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="classroom_member_role").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="classroom_status").drop(op.get_bind(), checkfirst=True)
