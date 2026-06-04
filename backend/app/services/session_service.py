from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.sessions import LoginResponse, TokenResponse, UserProfile

JWT_ALGORITHM = "HS256"
active_refresh_tokens: dict[str, str] = {}
revoked_access_tokens: set[str] = set()


def authenticate_user(db: Session, username: str, password: str) -> LoginResponse | None:
    user = find_active_user_by_username(db, username)

    if user is None or not verify_password(password, user.password_salt, user.password_hash):
        return None

    return create_login_response(user)


def register_user(db: Session, username: str, password: str, name: str) -> LoginResponse | None:
    normalized_username = username.strip()
    normalized_name = name.strip()

    if not normalized_username or not password or not normalized_name:
        return None

    existing_user = find_user_by_username(db, normalized_username)

    if existing_user is not None:
        return None

    salt = os.urandom(16)
    password_hash = hash_password(password, salt)
    user = User(
        student_id=generate_student_id(db),
        username=normalized_username,
        name=normalized_name,
        role="student",
        password_salt=encode_base64url(salt),
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return create_login_response(user)


def get_user_from_access_token(db: Session, token: str) -> UserProfile | None:
    if token in revoked_access_tokens:
        return None

    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        return None

    user = find_active_user_by_student_id(db, str(payload.get("sub")))

    if user is None:
        return None

    return to_user_profile(user)


def refresh_access_token(db: Session, refresh_token: str) -> TokenResponse | None:
    student_id = active_refresh_tokens.get(refresh_token)

    if student_id is None:
        return None

    payload = decode_token(refresh_token)

    if payload is None or payload.get("type") != "refresh" or payload.get("sub") != student_id:
        active_refresh_tokens.pop(refresh_token, None)
        return None

    user = find_active_user_by_student_id(db, student_id)

    if user is None:
        active_refresh_tokens.pop(refresh_token, None)
        return None

    access_token = create_token(user, token_type="access")

    return TokenResponse(
        access_token=access_token,
        token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expires_seconds,
    )


def logout_user(access_token: str, refresh_token: str | None) -> bool:
    payload = decode_token(access_token)

    if payload is None or payload.get("type") != "access":
        return False

    student_id = str(payload.get("sub"))
    revoked_access_tokens.add(access_token)

    if refresh_token is not None:
        if active_refresh_tokens.get(refresh_token) == student_id:
            active_refresh_tokens.pop(refresh_token, None)
    else:
        remove_refresh_tokens_for_student(student_id)

    return True


def delete_user_account(db: Session, access_token: str) -> bool:
    payload = decode_token(access_token)

    if payload is None or payload.get("type") != "access":
        return False

    student_id = str(payload.get("sub"))
    user = find_active_user_by_student_id(db, student_id)

    if user is None:
        return False

    revoked_access_tokens.add(access_token)
    remove_refresh_tokens_for_student(student_id)
    db.delete(user)
    db.commit()

    return True


def remove_refresh_tokens_for_student(student_id: str) -> None:
    tokens_to_remove = [
        token
        for token, token_student_id in active_refresh_tokens.items()
        if token_student_id == student_id
    ]

    for token in tokens_to_remove:
        active_refresh_tokens.pop(token, None)


def find_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).filter_by(username=username))


def find_active_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).filter_by(username=username, is_active=True))


def find_active_user_by_student_id(db: Session, student_id: str) -> User | None:
    return db.scalar(select(User).filter_by(student_id=student_id, is_active=True))


def create_login_response(user: User) -> LoginResponse:
    access_token = create_token(user, token_type="access")
    refresh_token = create_token(user, token_type="refresh")
    active_refresh_tokens[refresh_token] = user.student_id

    return LoginResponse(
        student_id=user.student_id,
        username=user.username,
        name=user.name,
        role=user.role,
        access_token=access_token,
        refresh_token=refresh_token,
        token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expires_seconds,
    )


def verify_password(password: str, salt: str, expected_hash: str) -> bool:
    salt_bytes = decode_base64url(salt)
    actual_hash = hash_password(password, salt_bytes)

    return hmac.compare_digest(actual_hash, expected_hash)


def hash_password(password: str, salt: bytes) -> str:
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        settings.password_hash_iterations,
    )
    return encode_base64url(password_hash)


def generate_student_id(db: Session) -> str:
    student_ids = db.scalars(select(User.student_id)).all()
    max_student_number = 0

    for student_id in student_ids:
        if not student_id.startswith("s"):
            continue

        try:
            student_number = int(student_id[1:])
        except ValueError:
            continue

        max_student_number = max(max_student_number, student_number)

    return f"s{max_student_number + 1}"


def create_token(user: User, token_type: str) -> str:
    now = int(time.time())
    ttl = (
        settings.access_token_expires_seconds
        if token_type == "access"
        else settings.refresh_token_expires_seconds
    )
    payload = {
        "sub": user.student_id,
        "username": user.username,
        "name": user.name,
        "role": user.role,
        "type": token_type,
        "iat": now,
        "exp": now + ttl,
        "jti": secrets.token_urlsafe(16),
    }

    return encode_jwt(payload)


def encode_jwt(payload: dict[str, Any]) -> str:
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_segment = encode_base64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = encode_base64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    signature = hmac.new(settings.auth_secret.encode("utf-8"), signing_input, hashlib.sha256).digest()

    return f"{header_segment}.{payload_segment}.{encode_base64url(signature)}"


def decode_token(token: str) -> dict[str, Any] | None:
    parts = token.split(".")

    if len(parts) != 3:
        return None

    header_segment, payload_segment, signature_segment = parts
    signing_input = f"{header_segment}.{payload_segment}".encode("utf-8")
    expected_signature = hmac.new(
        settings.auth_secret.encode("utf-8"),
        signing_input,
        hashlib.sha256,
    ).digest()

    if not hmac.compare_digest(encode_base64url(expected_signature), signature_segment):
        return None

    try:
        header = json.loads(decode_base64url(header_segment))
        payload = json.loads(decode_base64url(payload_segment))
    except (json.JSONDecodeError, ValueError):
        return None

    try:
        expires_at = int(payload.get("exp", 0))
    except (TypeError, ValueError):
        return None

    if header.get("alg") != JWT_ALGORITHM or expires_at < int(time.time()):
        return None

    return payload


def to_user_profile(user: User) -> UserProfile:
    return UserProfile(
        student_id=user.student_id,
        username=user.username,
        name=user.name,
        role=user.role,
    )


def encode_base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("utf-8").rstrip("=")


def decode_base64url(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)
