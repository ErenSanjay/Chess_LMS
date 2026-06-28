from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.classrooms.models import (
    Classroom,
    ClassroomMembership,
    ClassroomMembershipStatus,
    ClassroomStatus,
)


class ClassroomRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_classroom(self, classroom: Classroom) -> Classroom:
        self.session.add(classroom)
        self.session.flush()
        return classroom

    def add_membership(self, membership: ClassroomMembership) -> ClassroomMembership:
        self.session.add(membership)
        self.session.flush()
        return membership

    def get_classroom(self, classroom_id: UUID) -> Classroom | None:
        return self.session.get(Classroom, classroom_id)

    def get_classroom_by_join_code_hash(self, join_code_hash: str) -> Classroom | None:
        return self.session.scalar(
            select(Classroom)
            .where(Classroom.join_code_hash == join_code_hash)
            .where(Classroom.status == ClassroomStatus.active)
        )

    def get_membership(self, classroom_id: UUID, user_id: UUID) -> ClassroomMembership | None:
        return self.session.scalar(
            select(ClassroomMembership)
            .where(ClassroomMembership.classroom_id == classroom_id)
            .where(ClassroomMembership.user_id == user_id)
        )

    def list_classrooms_for_user(self, user_id: UUID) -> list[Classroom]:
        return list(
            self.session.scalars(
                select(Classroom)
                .join(ClassroomMembership, ClassroomMembership.classroom_id == Classroom.id)
                .where(ClassroomMembership.user_id == user_id)
                .where(ClassroomMembership.status == ClassroomMembershipStatus.active)
                .where(Classroom.status == ClassroomStatus.active)
                .order_by(Classroom.created_at.desc())
            )
        )

    def list_members(self, classroom_id: UUID) -> list[ClassroomMembership]:
        return list(
            self.session.scalars(
                select(ClassroomMembership)
                .where(ClassroomMembership.classroom_id == classroom_id)
                .where(ClassroomMembership.status == ClassroomMembershipStatus.active)
                .order_by(ClassroomMembership.joined_at.asc())
            )
        )
