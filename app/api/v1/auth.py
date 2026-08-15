from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import RequestContext, current_context
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.identity import AuditLog, Organization, Role, User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def session(request: Request) -> AsyncSession:
    return request.app.state.session_factory()


def token(user: User, request: Request) -> TokenResponse:
    s = request.app.state.settings
    return TokenResponse(
        access_token=create_access_token(
            str(user.id),
            str(user.organization_id),
            user.role.value,
            s.jwt_secret_key.get_secret_value(),
            s.jwt_access_token_minutes,
        )
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    payload: RegisterRequest, request: Request, db: AsyncSession = Depends(session)
) -> TokenResponse:
    if await db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(409, "Email already registered")
    org = Organization(name=payload.organization_name, slug=payload.organization_slug)
    db.add(org)
    await db.flush()
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        organization_id=org.id,
        role=Role.admin,
    )
    db.add(user)
    db.add(
        AuditLog(
            actor_user_id=user.id,
            organization_id=org.id,
            action="user.registered",
            entity_type="user",
            entity_id=user.id,
        )
    )
    await db.commit()
    return token(user, request)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest, request: Request, db: AsyncSession = Depends(session)
) -> TokenResponse:
    user = await db.scalar(select(User).where(User.email == payload.email))
    if (
        user is None
        or not user.is_active
        or not verify_password(payload.password, user.hashed_password)
    ):
        raise HTTPException(401, "Invalid credentials")
    return token(user, request)


@router.get("/me", response_model=UserResponse)
async def me(
    context: RequestContext = Depends(current_context), db: AsyncSession = Depends(session)
) -> UserResponse:
    user = await db.scalar(
        select(User).where(
            User.id == context.user_id,
            User.organization_id == context.organization_id,
            User.is_active.is_(True),
        )
    )
    if user is None:
        raise HTTPException(401, "Authenticated user is no longer available")
    return UserResponse(
        id=user.id,
        email=user.email,
        organization_id=user.organization_id,
        role=user.role,
    )
