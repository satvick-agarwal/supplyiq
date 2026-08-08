from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import (
    InventoryItemOut, StockAdjustRequest, TransferRequest,
    MovementOut, PaginatedResponse
)
from app.models.inventory_item import InventoryItem
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.services.inventory_service import InventoryService
from app.core.security import require_permission, get_current_user
from app.core.permissions import INVENTORY_READ, INVENTORY_WRITE, MOVEMENT_READ, MOVEMENT_WRITE

router = APIRouter(tags=["Inventory"])
inventory_router = APIRouter(prefix="/inventory")
movements_router = APIRouter(prefix="/inventory-movements")


# ── Inventory Items ────────────────────────────────────────────────────────────

@inventory_router.get("", response_model=PaginatedResponse)
async def list_inventory(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[UUID] = None,
    product_id: Optional[UUID] = None,
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(INVENTORY_READ)),
):
    skip = (page - 1) * page_size
    query = select(InventoryItem)
    if warehouse_id:
        query = query.where(InventoryItem.warehouse_id == warehouse_id)
    if product_id:
        query = query.where(InventoryItem.product_id == product_id)
    if low_stock_only:
        # Join product to compare with reorder_point
        query = query.join(Product, InventoryItem.product_id == Product.id).where(
            InventoryItem.quantity_on_hand <= Product.reorder_point
        )
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size))
    return PaginatedResponse(
        items=[InventoryItemOut.model_validate(i) for i in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@inventory_router.get("/low-stock", response_model=PaginatedResponse)
async def list_low_stock(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    warehouse_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(INVENTORY_READ)),
):
    skip = (page - 1) * page_size
    query = (
        select(InventoryItem)
        .join(Product, InventoryItem.product_id == Product.id)
        .where(
            and_(
                InventoryItem.quantity_on_hand <= Product.reorder_point,
                Product.is_active == True,
            )
        )
    )
    if warehouse_id:
        query = query.where(InventoryItem.warehouse_id == warehouse_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size))
    return PaginatedResponse(
        items=[InventoryItemOut.model_validate(i) for i in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@inventory_router.get("/{inventory_id}", response_model=InventoryItemOut)
async def get_inventory_item(
    inventory_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(INVENTORY_READ)),
):
    item = await db.get(InventoryItem, inventory_id)
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return item


@inventory_router.post("/adjust")
async def adjust_stock(
    body: StockAdjustRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(INVENTORY_WRITE)),
):
    service = InventoryService(db)
    movement = await service.adjust_stock(
        product_id=body.product_id,
        warehouse_id=body.warehouse_id,
        quantity=body.quantity,
        reason=body.reason,
        created_by=current_user.id,
    )
    return {"message": "Stock adjusted", "movement_id": str(movement.id)}


# ── Inventory Movements ────────────────────────────────────────────────────────

@movements_router.get("", response_model=PaginatedResponse)
async def list_movements(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    inventory_item_id: Optional[UUID] = None,
    movement_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(MOVEMENT_READ)),
):
    skip = (page - 1) * page_size
    query = select(InventoryMovement)
    if inventory_item_id:
        query = query.where(InventoryMovement.inventory_item_id == inventory_item_id)
    if movement_type:
        query = query.where(InventoryMovement.movement_type == movement_type)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(
        query.offset(skip).limit(page_size).order_by(InventoryMovement.created_at.desc())
    )
    return PaginatedResponse(
        items=[MovementOut.model_validate(m) for m in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@movements_router.post("/transfer")
async def transfer_stock(
    body: TransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(MOVEMENT_WRITE)),
):
    service = InventoryService(db)
    movement = await service.transfer_stock(
        product_id=body.product_id,
        from_warehouse_id=body.from_warehouse_id,
        to_warehouse_id=body.to_warehouse_id,
        quantity=body.quantity,
        reason=body.reason,
        created_by=current_user.id,
    )
    return {"message": "Stock transferred", "movement_id": str(movement.id)}
