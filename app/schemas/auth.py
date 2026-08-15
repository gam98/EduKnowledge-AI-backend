from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.db.models.identity import Role


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12)
    organization_name: str = Field(min_length=2, max_length=200)
    organization_slug: str = Field(pattern=r"^[a-z0-9-]+$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    organization_id: UUID
    role: Role
