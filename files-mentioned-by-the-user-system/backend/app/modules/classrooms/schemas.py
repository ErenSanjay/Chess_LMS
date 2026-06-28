from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.modules.classrooms.models import ClassroomMemberRole, ClassroomStatus


class ClassroomCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)


class ClassroomUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)


class JoinClassroomRequest(BaseModel):
    join_code: str = Field(min_length=6, max_length=32)


class ClassroomResponse(BaseModel):
    id: UUID
    teacher_id: UUID
    name: str
    description: str | None
    status: ClassroomStatus
    created_at: datetime
    updated_at: datetime
    join_code: str | None = None

    model_config = {"from_attributes": True}


class ClassroomMemberResponse(BaseModel):
    id: UUID
    classroom_id: UUID
    user_id: UUID
    role: ClassroomMemberRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class ClassroomJoinResponse(BaseModel):
    classroom: ClassroomResponse
    membership: ClassroomMemberResponse
