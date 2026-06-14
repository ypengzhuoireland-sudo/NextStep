from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.sessions import UserProfile

JWT_ALGORITHM = "HS256"
revoked_access_tokens: set[str] = set()


def get_user_from_access_token(db: Session, token: str) -> UserProfile | None:
    if is_access_token_revoked(token):
        return None

    payload = decode_token(token)

    if payload is None or payload.get("type") != "access":
        return None

    user = find_active_user_by_student_id(db, str(payload.get("sub")))

    if user is None:
        return None

    return to_user_profile(user)


def revoke_access_token(token: str) -> None:
    revoked_access_tokens.add(token)


def is_access_token_revoked(token: str) -> bool:
    return token in revoked_access_tokens


def find_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).filter_by(username=username))


def find_active_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).filter_by(username=username, is_active=True))


def find_active_user_by_student_id(db: Session, student_id: str) -> User | None:
    return db.scalar(select(User).filter_by(student_id=student_id, is_active=True))


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
