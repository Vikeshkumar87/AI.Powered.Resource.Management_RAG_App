"""
Authentication routes for role-based access in the UI.
"""
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=2, max_length=100)


class LoginResponse(BaseModel):
    username: str
    role: str
    display_name: str
    message: str


def get_current_role(x_user_role: str | None = Header(default=None, alias="X-User-Role")) -> str:
    """Return the caller role from request headers."""
    if not x_user_role:
        return "user"
    normalized = x_user_role.strip().lower()
    if normalized not in {"admin", "user"}:
        return "user"
    return normalized


def require_admin(x_user_role: str | None = Header(default=None, alias="X-User-Role")) -> str:
    """Require admin role for protected endpoints."""
    role = get_current_role(x_user_role)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required for phase validation endpoints.")
    return role


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    """Simple credential-based login returning user role."""
    username = payload.username.strip()
    password = payload.password

    if username == settings.admin_username and password == settings.admin_password:
        return LoginResponse(
            username=username,
            role="admin",
            display_name=settings.admin_display_name,
            message="Admin login successful.",
        )

    if username == settings.user_username and password == settings.user_password:
        return LoginResponse(
            username=username,
            role="user",
            display_name=settings.user_display_name,
            message="User login successful.",
        )

    raise HTTPException(status_code=401, detail="Invalid username or password.")