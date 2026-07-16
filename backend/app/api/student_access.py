from typing import NoReturn

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.sessions import UserProfile
from app.services.session_service import get_user_from_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def require_student_user(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserProfile:
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    current_user = get_user_from_access_token(db, auth_credentials.credentials)

    if current_user is None:
        raise_unauthorized("Invalid or expired access token")

    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student role required",
        )

    return current_user


def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
