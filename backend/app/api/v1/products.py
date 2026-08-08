from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductOut, PaginatedResponse
from app.models.product import Product
from app.core.security import require_permission
from app.core.permissions import PRODUCT_READ, PRODUCT_WRITE, PRODUCT_DELETE

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=PaginatedResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PRODUCT_READ)),
):
    skip = (page - 1) * page_size
    query = select(Product)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size).order_by(Product.name))
    return PaginatedResponse(
        items=[ProductOut.model_validate(p) for p in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ProductOut, status_code=201)
async def create_product(
    body: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PRODUCT_WRITE)),
):
    existing = await db.execute(select(Product).where(Product.sku == body.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"SKU '{body.sku}' already exists")
    product = Product(**body.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PRODUCT_READ)),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: UUID,
    body: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PRODUCT_WRITE)),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    await db.flush()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PRODUCT_DELETE)),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False  # Soft delete
    await db.flush()
