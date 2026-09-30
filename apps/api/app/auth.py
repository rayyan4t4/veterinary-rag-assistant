from dataclasses import dataclass
from fastapi import Depends, Header, HTTPException
import jwt
from jwt import PyJWKClient
from .config import get_settings


@dataclass(frozen=True)
class CurrentUser:
    id: str
    role: str = "user"


async def current_user(authorization: str | None = Header(default=None)) -> CurrentUser:
    settings = get_settings()
    if settings.app_env == "test" and authorization and authorization.startswith("Bearer test:"):
        parts = authorization.removeprefix("Bearer test:").split(":", 1)
        return CurrentUser(parts[0], parts[1] if len(parts) > 1 else "user")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Authentication required")
    if not settings.supabase_url:
        raise HTTPException(503, "Authentication provider is not configured")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        jwks = PyJWKClient(f"{settings.supabase_url}/auth/v1/.well-known/jwks.json")
        key = jwks.get_signing_key_from_jwt(token).key
        claims = jwt.decode(token, key, algorithms=["RS256", "ES256"], audience="authenticated")
        return CurrentUser(claims["sub"], claims.get("app_metadata", {}).get("role", "user"))
    except Exception as exc:
        raise HTTPException(401, "Invalid or expired access token") from exc


async def admin_user(user: CurrentUser = Depends(current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(403, "Administrator access required")
    return user
