import hashlib
import secrets
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.swasthyaai.models.auth import Session, User
from backend.swasthyaai.services.db import connect


_SESSION_LIFETIME = timedelta(hours=12)
_BEARER = HTTPBearer(auto_error=False)


def _password_hash(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_user(email: str, password: str, role: Literal["patient", "clinician"]) -> User:
    user_id = str(uuid.uuid4())
    salt = secrets.token_bytes(16)
    password_hash = _password_hash(password, salt)
    created_at = datetime.now(timezone.utc).isoformat()
    try:
        with connect() as connection:
            connection.execute(
                "INSERT INTO users(user_id, email, password_salt, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, email, salt, password_hash, role, created_at),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError("Email already registered") from error
    return User(user_id=user_id, email=email, role=role)


def authenticate(email: str, password: str) -> Session | None:
    with connect() as connection:
        row = connection.execute(
            "SELECT user_id, email, password_salt, password_hash, role FROM users WHERE email = ?",
            (email,),
        ).fetchone()
        if row is None or not secrets.compare_digest(_password_hash(password, row["password_salt"]), row["password_hash"]):
            return None
        token = secrets.token_urlsafe(32)
        now = datetime.now(timezone.utc)
        expires_at = now + _SESSION_LIFETIME
        connection.execute(
            "INSERT INTO sessions(token_digest, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (token_digest(token), row["user_id"], now.isoformat(), expires_at.isoformat()),
        )
    return Session(
        access_token=token,
        expires_at=expires_at,
        user=User(user_id=row["user_id"], email=row["email"], role=row["role"]),
    )


def get_user_for_token(token: str) -> User | None:
    now = datetime.now(timezone.utc)
    with connect() as connection:
        row = connection.execute(
            "SELECT users.user_id, users.email, users.role, sessions.expires_at "
            "FROM sessions JOIN users USING(user_id) WHERE sessions.token_digest = ?",
            (token_digest(token),),
        ).fetchone()
        if row is None or datetime.fromisoformat(row["expires_at"]) <= now:
            if row is not None:
                connection.execute("DELETE FROM sessions WHERE token_digest = ?", (token_digest(token),))
            return None
        return User(user_id=row["user_id"], email=row["email"], role=row["role"])


def revoke_token(token: str) -> None:
    with connect() as connection:
        connection.execute("DELETE FROM sessions WHERE token_digest = ?", (token_digest(token),))


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_BEARER),
) -> User:
    user = get_user_for_token(credentials.credentials) if credentials else None
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_role(*roles: Literal["patient", "clinician"]):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="This account cannot access that resource")
        return user
    return dependency
