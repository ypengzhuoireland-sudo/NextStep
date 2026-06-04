from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import NoReturn

from app.db.session import get_db
from app.schemas.sessions import (
    DeleteAccountResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RegisterRequest,
    RefreshRequest,
    TokenResponse,
    UserProfile,
)
from app.services.session_service import (
    authenticate_user,
    delete_user_account,
    get_user_from_access_token,
    logout_user,
    register_user,
    refresh_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, request.username, request.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return user


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, request.username, request.password, request.name)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    return user


@router.get("/me", response_model=UserProfile)
def get_current_user(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    access_token: str = auth_credentials.credentials
    user = get_user_from_access_token(db, access_token)

    if user is None:
        raise_unauthorized("Invalid or expired access token")

    return user


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    tokens = refresh_access_token(db, request.refresh_token)

    if tokens is None:
        raise_unauthorized("Invalid or expired refresh token")

    return tokens


@router.post("/logout", response_model=LogoutResponse)
def logout(
    request: LogoutRequest | None = None,
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    access_token: str = auth_credentials.credentials
    request_refresh_token = request.refresh_token if request is not None else None
    logged_out = logout_user(access_token, request_refresh_token)

    if not logged_out:
        raise_unauthorized("Invalid or expired access token")

    return LogoutResponse(message="Logged out")


@router.delete("/me", response_model=DeleteAccountResponse)
def delete_current_user(
    auth_credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if auth_credentials is None:
        raise_unauthorized("Missing Authorization header")

    access_token: str = auth_credentials.credentials
    deleted = delete_user_account(db, access_token)

    if not deleted:
        raise_unauthorized("Invalid or expired access token")

    return DeleteAccountResponse(message="Account deleted")


def raise_unauthorized(detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
