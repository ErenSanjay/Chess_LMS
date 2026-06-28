from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.modules.auth.dependencies import get_current_user
from app.modules.classrooms.schemas import (
    ClassroomCreateRequest,
    ClassroomJoinResponse,
    ClassroomMemberResponse,
    ClassroomResponse,
    ClassroomUpdateRequest,
    JoinClassroomRequest,
)
from app.modules.classrooms.service import (
    ClassroomAlreadyJoinedError,
    ClassroomNotFoundError,
    ClassroomPermissionError,
    ClassroomService,
    InvalidJoinCodeError,
)
from app.modules.users.models import User


router = APIRouter(prefix="/api/v1", tags=["classrooms"])


def get_classroom_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ClassroomService:
    return ClassroomService(session, settings)


@router.post("/classrooms", response_model=ClassroomResponse, status_code=status.HTTP_201_CREATED)
def create_classroom(
    payload: ClassroomCreateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ClassroomService, Depends(get_classroom_service)],
) -> ClassroomResponse:
    try:
        classroom, join_code = service.create_classroom(
            teacher=current_user,
            name=payload.name,
            description=payload.description,
        )
    except ClassroomPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers can create classrooms") from None

    response = ClassroomResponse.model_validate(classroom)
    response.join_code = join_code
    return response


@router.get("/classrooms", response_model=list[ClassroomResponse])
def list_classrooms(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ClassroomService, Depends(get_classroom_service)],
) -> list[ClassroomResponse]:
    return [ClassroomResponse.model_validate(item) for item in service.list_classrooms(current_user)]


@router.get("/classrooms/{classroom_id}", response_model=ClassroomResponse)
def get_classroom(
    classroom_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ClassroomService, Depends(get_classroom_service)],
) -> ClassroomResponse:
    try:
        return ClassroomResponse.model_validate(service.get_classroom_for_user(classroom_id, current_user))
    except ClassroomNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found") from None
    except ClassroomPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Classroom access denied") from None


@router.patch("/classrooms/{classroom_id}", response_model=ClassroomResponse)
def update_classroom(
    classroom_id: UUID,
    payload: ClassroomUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ClassroomService, Depends(get_classroom_service)],
) -> ClassroomResponse:
    try:
        return ClassroomResponse.model_validate(
            service.update_classroom(
                classroom_id=classroom_id,
                user=current_user,
                name=payload.name,
                description=payload.description,
            )
        )
    except ClassroomNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found") from None
    except ClassroomPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the teacher can update this classroom") from None


@router.delete("/classrooms/{classroom_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_classroom(
    classroom_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ClassroomService, Depends(get_classroom_service)],
) -> None:
    try:
        service.archive_classroom(classroom_id, current_user)
    except ClassroomNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found") from None
    except ClassroomPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the teacher can archive this classroom") from None


@router.post("/classrooms/join", response_model=ClassroomJoinResponse)
def join_classroom(
    payload: JoinClassroomRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ClassroomService, Depends(get_classroom_service)],
) -> ClassroomJoinResponse:
    try:
        classroom, membership = service.join_classroom(
            student=current_user,
            join_code=payload.join_code,
        )
    except InvalidJoinCodeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Classroom code is invalid") from None
    except ClassroomAlreadyJoinedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Student is already enrolled") from None
    except ClassroomPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can join by code") from None

    return ClassroomJoinResponse(
        classroom=ClassroomResponse.model_validate(classroom),
        membership=ClassroomMemberResponse.model_validate(membership),
    )


@router.get("/classrooms/{classroom_id}/members", response_model=list[ClassroomMemberResponse])
def list_members(
    classroom_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ClassroomService, Depends(get_classroom_service)],
) -> list[ClassroomMemberResponse]:
    try:
        return [
            ClassroomMemberResponse.model_validate(member)
            for member in service.list_members(classroom_id, current_user)
        ]
    except ClassroomNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found") from None
    except ClassroomPermissionError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Classroom access denied") from None
