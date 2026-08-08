from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryOut, CategoryTree, PaginatedResponse
from app.models.category import Category
from app.core.security import require_permission
from app.core.permissions import CATEGORY_READ, CATEGORY_WRITE, CATEGORY_DELETE

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=PaginatedResponse)
async def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    parent_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CATEGORY_READ)),
):
    skip = (page - 1) * page_size
    query = select(Category)
    if parent_id is not None:
        query = query.where(Category.parent_id == parent_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size))
    return PaginatedResponse(
        items=[CategoryOut.model_validate(c) for c in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=CategoryOut, status_code=201)
async def create_category(
    body: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CATEGORY_WRITE)),
):
    if body.parent_id:
        parent = await db.get(Category, body.parent_id)
        if not parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
    cat = Category(**body.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return cat


@router.get("/{category_id}", response_model=CategoryOut)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CATEGORY_READ)),
):
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat


@router.patch("/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: UUID,
    body: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CATEGORY_WRITE)),
):
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(cat, field, value)
    await db.flush()
    await db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CATEGORY_DELETE)),
):
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.flush()
