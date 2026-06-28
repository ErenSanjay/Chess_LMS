from secrets import token_urlsafe
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.security import hash_token
from app.modules.classrooms.models import (
    Classroom,
    ClassroomMemberRole,
    ClassroomMembership,
    ClassroomMembershipStatus,
    ClassroomStatus,
)
from app.modules.classrooms.repository import ClassroomRepository
from app.modules.users.models import User, UserRole


class ClassroomError(Exception):
    pass


class ClassroomPermissionError(ClassroomError):
    pass


class ClassroomNotFoundError(ClassroomError):
    pass


class ClassroomAlreadyJoinedError(ClassroomError):
    pass


class InvalidJoinCodeError(ClassroomError):
    pass


class ClassroomService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.repository = ClassroomRepository(session)

    def create_classroom(
        self,
        *,
        teacher: User,
        name: str,
        description: str | None,
    ) -> tuple[Classroom, str]:
        if teacher.role != UserRole.teacher and teacher.role != UserRole.admin:
            raise ClassroomPermissionError("Only teachers can create classrooms")

        join_code = self._new_join_code()
        classroom = Classroom(
            teacher_id=teacher.id,
            name=name.strip(),
            description=description.strip() if description else None,
            join_code_hash=hash_token(join_code, self.settings),
            status=ClassroomStatus.active,
        )
        self.repository.add_classroom(classroom)
        self.repository.add_membership(
            ClassroomMembership(
                classroom_id=classroom.id,
                user_id=teacher.id,
                role=ClassroomMemberRole.teacher,
                status=ClassroomMembershipStatus.active,
            )
        )
        self.session.commit()
        return classroom, join_code

    def list_classrooms(self, user: User) -> list[Classroom]:
        return self.repository.list_classrooms_for_user(user.id)

    def get_classroom_for_user(self, classroom_id: UUID, user: User) -> Classroom:
        classroom = self.repository.get_classroom(classroom_id)
        if classroom is None or classroom.status != ClassroomStatus.active:
            raise ClassroomNotFoundError("Classroom not found")
        if self.repository.get_membership(classroom_id, user.id) is None:
            raise ClassroomPermissionError("Classroom access denied")
        return classroom

    def update_classroom(
        self,
        *,
        classroom_id: UUID,
        user: User,
        name: str | None,
        description: str | None,
    ) -> Classroom:
        classroom = self._get_owned_classroom(classroom_id, user)
        if name is not None:
            classroom.name = name.strip()
        if description is not None:
            classroom.description = description.strip() or None
        self.session.commit()
        return classroom

    def archive_classroom(self, classroom_id: UUID, user: User) -> None:
        classroom = self._get_owned_classroom(classroom_id, user)
        classroom.status = ClassroomStatus.archived
        self.session.commit()

    def join_classroom(self, *, student: User, join_code: str) -> tuple[Classroom, ClassroomMembership]:
        if student.role != UserRole.student:
            raise ClassroomPermissionError("Only students can join with a classroom code")

        classroom = self.repository.get_classroom_by_join_code_hash(
            hash_token(join_code.strip(), self.settings)
        )
        if classroom is None:
            raise InvalidJoinCodeError("Classroom code is invalid")

        existing = self.repository.get_membership(classroom.id, student.id)
        if existing is not None and existing.status == ClassroomMembershipStatus.active:
            raise ClassroomAlreadyJoinedError("Student is already enrolled")

        if existing is not None:
            existing.status = ClassroomMembershipStatus.active
            membership = existing
        else:
            membership = ClassroomMembership(
                classroom_id=classroom.id,
                user_id=student.id,
                role=ClassroomMemberRole.student,
                status=ClassroomMembershipStatus.active,
            )
            self.repository.add_membership(membership)

        self.session.commit()
        return classroom, membership

    def list_members(self, classroom_id: UUID, user: User) -> list[ClassroomMembership]:
        self.get_classroom_for_user(classroom_id, user)
        return self.repository.list_members(classroom_id)

    def _get_owned_classroom(self, classroom_id: UUID, user: User) -> Classroom:
        classroom = self.repository.get_classroom(classroom_id)
        if classroom is None or classroom.status != ClassroomStatus.active:
            raise ClassroomNotFoundError("Classroom not found")
        if classroom.teacher_id != user.id and user.role != UserRole.admin:
            raise ClassroomPermissionError("Only the classroom teacher can modify it")
        return classroom

    def _new_join_code(self) -> str:
        return token_urlsafe(8).replace("-", "").replace("_", "")[:10].upper()
