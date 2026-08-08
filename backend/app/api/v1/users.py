from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.auth import UserCreate, UserUpdate, UserOut
from app.schemas.schemas import PaginatedResponse
from app.models.user import User
from app.models.role import Role
from app.repositories.user_repo import UserRepository
from app.core.security import hash_password, get_current_user, require_permission
from app.core.permissions import USER_READ, USER_WRITE, USER_DELETE

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=PaginatedResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(USER_READ)),
):
    skip = (page - 1) * page_size
    query = select(User)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size))
    users = result.scalars().all()
    return PaginatedResponse(
        items=[UserOut.model_validate(u) for u in users],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(USER_WRITE)),
):
    repo = UserRepository(db)
    existing = await repo.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    # Verify role exists
    role = await db.get(Role, body.role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role_id=body.role_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(USER_READ)),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(USER_WRITE)),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(USER_DELETE)),
):
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    user.is_active = False  # Soft delete
    await db.flush()
