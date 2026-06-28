import enum
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ClassroomStatus(str, enum.Enum):
    active = "active"
    archived = "archived"


class ClassroomMemberRole(str, enum.Enum):
    teacher = "teacher"
    student = "student"


class ClassroomMembershipStatus(str, enum.Enum):
    active = "active"
    removed = "removed"


class Classroom(Base):
    __tablename__ = "classrooms"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    teacher_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    join_code_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    status: Mapped[ClassroomStatus] = mapped_column(
        Enum(ClassroomStatus, name="classroom_status"),
        nullable=False,
        default=ClassroomStatus.active,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class ClassroomMembership(Base):
    __tablename__ = "classroom_memberships"
    __table_args__ = (
        UniqueConstraint("classroom_id", "user_id", name="uq_classroom_memberships_classroom_id_user_id"),
    )

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    classroom_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("classrooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ClassroomMemberRole] = mapped_column(
        Enum(ClassroomMemberRole, name="classroom_member_role"),
        nullable=False,
    )
    status: Mapped[ClassroomMembershipStatus] = mapped_column(
        Enum(ClassroomMembershipStatus, name="classroom_membership_status"),
        nullable=False,
        default=ClassroomMembershipStatus.active,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
