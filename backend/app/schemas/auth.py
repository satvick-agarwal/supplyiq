from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ── Auth Schemas ───────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str = ""
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


# ── Permission / Role Schemas ──────────────────────────────────────────────────

class PermissionOut(BaseModel):
    id: UUID
    code: str
    description: Optional[str] = None

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    permissions: List[PermissionOut] = []

    model_config = {"from_attributes": True}


# ── User Schemas ───────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str
    role_id: UUID


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    last_login_at: Optional[datetime] = None
    role: RoleOut
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserMe(UserOut):
    pass
