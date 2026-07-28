"""
Authentication routes for role-based access in the UI.
"""
import base64
import hashlib
import hmac
import json
import time

from fastapi import APIRouter, Header, HTTPException
from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.audit import log_audit_event

router = APIRouter(prefix="/auth", tags=["Auth"])

TOKEN_TTL_SECONDS = 60 * 60 * 8


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=2, max_length=100)


class LoginResponse(BaseModel):
    username: str
    role: str
    display_name: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    message: str


def _base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _base64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign_token(payload_b64: str) -> str:
    return hmac.new(
        settings.auth_secret_key.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_access_token(username: str, role: str, display_name: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "display_name": display_name,
        "iat": int(time.time()),
        "exp": int(time.time()) + TOKEN_TTL_SECONDS,
    }
    payload_b64 = _base64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = _sign_token(payload_b64)
    return f"{payload_b64}.{signature}"


def decode_access_token(token: str) -> dict[str, str | int]:
    try:
        payload_b64, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token.") from exc

    expected_signature = _sign_token(payload_b64)
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

    try:
        payload = json.loads(_base64url_decode(payload_b64).decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication token.") from exc

    if int(payload.get("exp", 0)) < int(time.time()):
        raise HTTPException(status_code=401, detail="Authentication token expired.")

    return payload


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    prefix = "bearer "
    if authorization.lower().startswith(prefix):
        return authorization[len(prefix):].strip()
    return None


def get_current_session(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> dict[str, str]:
    """Return the authenticated session using a bearer token or legacy role header."""
    token = _extract_bearer_token(authorization)
    if token:
        payload = decode_access_token(token)
        return {
            "username": str(payload.get("sub", "user")),
            "role": str(payload.get("role", "user")),
            "display_name": str(payload.get("display_name", "User")),
        }

    role = get_current_role(x_user_role)
    return {
        "username": "guest",
        "role": role,
        "display_name": settings.admin_display_name if role == "admin" else settings.user_display_name,
    }


def get_current_role(x_user_role: str | None = Header(default=None, alias="X-User-Role")) -> str:
    """Return the caller role from request headers."""
    if not x_user_role:
        return "user"
    normalized = x_user_role.strip().lower()
    if normalized not in {"admin", "user"}:
        return "user"
    return normalized


def require_admin(
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_user_role: str | None = Header(default=None, alias="X-User-Role"),
) -> str:
    """Require admin role for protected endpoints."""
    role = get_current_session(authorization=authorization, x_user_role=x_user_role)["role"]
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required for phase validation endpoints.")
    return role


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """Simple credential-based login returning user role."""
    username = payload.username.strip()
    password = payload.password

    if username == settings.admin_username and password == settings.admin_password:
        display_name = settings.admin_display_name
        log_audit_event(
            action="login_success",
            entity_type="auth",
            entity_id=username,
            details={"role": "admin"},
            actor=username,
            actor_role="admin",
            source="auth.login",
            db=db,
        )
        return LoginResponse(
            username=username,
            role="admin",
            display_name=display_name,
            access_token=create_access_token(username=username, role="admin", display_name=display_name),
            expires_in=TOKEN_TTL_SECONDS,
            message="Admin login successful.",
        )

    if username == settings.user_username and password == settings.user_password:
        display_name = settings.user_display_name
        log_audit_event(
            action="login_success",
            entity_type="auth",
            entity_id=username,
            details={"role": "user"},
            actor=username,
            actor_role="user",
            source="auth.login",
            db=db,
        )
        return LoginResponse(
            username=username,
            role="user",
            display_name=display_name,
            access_token=create_access_token(username=username, role="user", display_name=display_name),
            expires_in=TOKEN_TTL_SECONDS,
            message="User login successful.",
        )

    log_audit_event(
        action="login_failed",
        entity_type="auth",
        entity_id=username,
        details={"reason": "invalid_credentials"},
        actor=username,
        source="auth.login",
        db=db,
    )
    raise HTTPException(status_code=401, detail="Invalid username or password.")