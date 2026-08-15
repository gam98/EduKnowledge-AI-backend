from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Settings
from app.core.security import decode_access_token
from app.db.models.identity import Role

bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class RequestContext:
    user_id: UUID
    organization_id: UUID
    role: Role


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings


async def current_context(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    settings: Settings = Depends(get_settings_dep),
) -> RequestContext:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    claims = decode_access_token(
        credentials.credentials, settings.jwt_secret_key.get_secret_value()
    )
    try:
        return RequestContext(UUID(claims["sub"]), UUID(claims["org"]), Role(claims["role"]))
    except (KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication token") from None


def require_roles(*roles: Role):
    async def dependency(context: RequestContext = Depends(current_context)) -> RequestContext:
        if context.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return context

    return dependency
