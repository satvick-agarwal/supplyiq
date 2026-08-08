from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import WarehouseCreate, WarehouseUpdate, WarehouseOut, PaginatedResponse
from app.models.warehouse import Warehouse
from app.models.inventory_item import InventoryItem
from app.core.security import require_permission
from app.core.permissions import WAREHOUSE_READ, WAREHOUSE_WRITE, WAREHOUSE_DELETE

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("", response_model=PaginatedResponse)
async def list_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(WAREHOUSE_READ)),
):
    skip = (page - 1) * page_size
    total = (await db.execute(select(func.count()).select_from(Warehouse))).scalar_one()
    result = await db.execute(select(Warehouse).offset(skip).limit(page_size).order_by(Warehouse.name))
    return PaginatedResponse(
        items=[WarehouseOut.model_validate(w) for w in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=WarehouseOut, status_code=201)
async def create_warehouse(
    body: WarehouseCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(WAREHOUSE_WRITE)),
):
    warehouse = Warehouse(**body.model_dump())
    db.add(warehouse)
    await db.flush()
    await db.refresh(warehouse)
    return warehouse


@router.get("/{warehouse_id}", response_model=WarehouseOut)
async def get_warehouse(
    warehouse_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(WAREHOUSE_READ)),
):
    warehouse = await db.get(Warehouse, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.patch("/{warehouse_id}", response_model=WarehouseOut)
async def update_warehouse(
    warehouse_id: UUID,
    body: WarehouseUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(WAREHOUSE_WRITE)),
):
    warehouse = await db.get(Warehouse, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(warehouse, field, value)
    await db.flush()
    await db.refresh(warehouse)
    return warehouse


@router.delete("/{warehouse_id}", status_code=204)
async def delete_warehouse(
    warehouse_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(WAREHOUSE_DELETE)),
):
    warehouse = await db.get(Warehouse, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    await db.delete(warehouse)
    await db.flush()


@router.get("/{warehouse_id}/utilization")
async def get_warehouse_utilization(
    warehouse_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(WAREHOUSE_READ)),
):
    warehouse = await db.get(Warehouse, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    # Sum all quantities in this warehouse
    qty_result = await db.execute(
        select(func.sum(InventoryItem.quantity_on_hand))
        .where(InventoryItem.warehouse_id == warehouse_id)
    )
    total_qty = float(qty_result.scalar_one() or 0)
    capacity = float(warehouse.capacity_units or 0)
    utilization_pct = (total_qty / capacity * 100) if capacity > 0 else 0

    return {
        "warehouse_id": str(warehouse_id),
        "warehouse_name": warehouse.name,
        "total_quantity_on_hand": total_qty,
        "capacity_units": capacity,
        "utilization_percentage": round(utilization_pct, 2),
    }
