from __future__ import annotations

import os
import time

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.knowledge_component import KnowledgeComponent
from app.models.diagnostic_attempt import DiagnosticAttempt
from app.models.mastery_event import MasteryEvent
from app.models.student_mastery import StudentMastery
from app.models.submission import Submission
from app.models.user import User
from app.schemas.student_auth import (
    StudentAuthResponse,
    StudentLoginRequest,
    StudentRegisterRequest,
    StudentUser,
)
from app.services.session_service import (
    create_token,
    encode_base64url,
    find_active_user_by_student_id,
    find_active_user_by_username,
    find_user_by_username,
    hash_password,
    is_access_token_revoked,
    revoke_access_token,
    verify_password,
)
from app.services.bkt_service import INITIAL_STUDENT_MASTERY


def authenticate_student(
    db: Session,
    request: StudentLoginRequest,
) -> StudentAuthResponse | None:
    user = find_active_user_by_username(db, request.email.strip().lower())

    if (
        user is None
        or user.role != "student"
        or not verify_password(request.password, user.password_salt, user.password_hash)
    ):
        return None

    return to_student_auth_response(user)


def authenticate_teacher(
    db: Session,
    request: StudentLoginRequest,
) -> StudentAuthResponse | None:
    user = find_active_user_by_username(db, request.email.strip().lower())

    if (
        user is None
        or user.role != "teacher"
        or not verify_password(request.password, user.password_salt, user.password_hash)
    ):
        return None

    return to_student_auth_response(user)


def register_student(
    db: Session,
    request: StudentRegisterRequest,
) -> StudentAuthResponse | None:
    email = request.email.strip().lower()
    name = request.name.strip()

    if not email or not name or not request.password:
        return None

    if find_user_by_username(db, email) is not None:
        return None

    salt = os.urandom(16)
    user = User(
        student_id=generate_frontend_student_id(db),
        username=email,
        name=name,
        role="student",
        password_salt=encode_base64url(salt),
        password_hash=hash_password(request.password, salt),
    )

    db.add(user)
    db.flush()
    ensure_student_mastery_rows(db, user.student_id)
    db.commit()
    db.refresh(user)

    return to_student_auth_response(user)


def get_student_from_token(db: Session, token: str) -> StudentUser | None:
    if is_access_token_revoked(token):
        return None

    # The backend returns a normal JWT access token so the same token works with
    # authenticated dashboard/mastery/submission endpoints. This fallback also
    # accepts the frontend mock token shape documented in API.md.
    if token.startswith("student_"):
        user = find_active_user_by_student_id(db, token.removeprefix("student_"))
    else:
        from app.services.session_service import get_user_from_access_token

        profile = get_user_from_access_token(db, token)
        user = None if profile is None else find_active_user_by_student_id(db, profile.student_id)

    if user is None:
        return None

    return to_student_user(user)


def logout_student(db: Session, token: str) -> bool:
    if is_access_token_revoked(token):
        return False

    if get_user_model_from_token(db, token) is None:
        return False

    revoke_access_token(token)
    return True


def delete_student_account(db: Session, token: str) -> bool:
    if is_access_token_revoked(token):
        return False

    user = get_user_model_from_token(db, token)

    if user is None or user.role != "student":
        return False

    db.execute(delete(MasteryEvent).where(MasteryEvent.student_id == user.student_id))
    db.execute(delete(DiagnosticAttempt).where(DiagnosticAttempt.student_id == user.student_id))
    db.execute(delete(Submission).where(Submission.student_id == user.student_id))
    db.execute(delete(StudentMastery).where(StudentMastery.student_id == user.student_id))
    db.delete(user)
    revoke_access_token(token)
    db.commit()

    return True


def get_user_model_from_token(db: Session, token: str) -> User | None:
    if token.startswith("student_"):
        return find_active_user_by_student_id(db, token.removeprefix("student_"))

    from app.services.session_service import get_user_from_access_token

    profile = get_user_from_access_token(db, token)

    if profile is None:
        return None

    return find_active_user_by_student_id(db, profile.student_id)


def to_student_auth_response(user: User) -> StudentAuthResponse:
    return StudentAuthResponse(
        token=create_token(user, token_type="access"),
        user=to_student_user(user),
    )


def to_student_user(user: User) -> StudentUser:
    return StudentUser(
        id=user.student_id,
        name=user.name,
        email=user.username,
        avatarInitials=avatar_initials(user.name),
        needsDiagnostic=not user.diagnostic_completed,
        role=user.role,
    )


def avatar_initials(name: str) -> str:
    parts = [part for part in name.strip().split() if part]

    if not parts:
        return "ST"

    if len(parts) == 1:
        return parts[0][:2].upper()

    return f"{parts[0][0]}{parts[-1][0]}".upper()


def generate_frontend_student_id(db: Session) -> str:
    while True:
        student_id = f"stu_local_{int(time.time() * 1000)}"

        if find_active_user_by_student_id(db, student_id) is None:
            return student_id


def ensure_student_mastery_rows(db: Session, student_id: str) -> None:
    kc_ids = db.scalars(select(KnowledgeComponent.id).order_by(KnowledgeComponent.id)).all()

    for kc_id in kc_ids:
        if db.get(StudentMastery, (student_id, kc_id)) is None:
            db.add(
                StudentMastery(
                    student_id=student_id,
                    kc_id=kc_id,
                    mastery=INITIAL_STUDENT_MASTERY,
                )
            )
