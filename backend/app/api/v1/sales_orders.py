from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import SOCreate, SOUpdate, SOOut, PaginatedResponse
from app.models.sales_order import SalesOrder
from app.services.sales_order_service import SalesOrderService
from app.core.security import require_permission
from app.core.permissions import SO_READ, SO_WRITE, SO_DELETE

router = APIRouter(prefix="/sales-orders", tags=["Sales Orders"])


@router.get("", response_model=PaginatedResponse)
async def list_sales_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    warehouse_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SO_READ)),
):
    skip = (page - 1) * page_size
    query = select(SalesOrder)
    if status:
        query = query.where(SalesOrder.status == status)
    if customer_id:
        query = query.where(SalesOrder.customer_id == customer_id)
    if warehouse_id:
        query = query.where(SalesOrder.warehouse_id == warehouse_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(
        query.offset(skip).limit(page_size).order_by(SalesOrder.created_at.desc())
    )
    return PaginatedResponse(
        items=[SOOut.model_validate(o) for o in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=SOOut, status_code=201)
async def create_sales_order(
    body: SOCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(SO_WRITE)),
):
    service = SalesOrderService(db)
    data = body.model_dump()
    items = data.pop("items")
    so = await service.create_so({**data, "items": items}, current_user.id)
    return so


@router.get("/{so_id}", response_model=SOOut)
async def get_sales_order(
    so_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SO_READ)),
):
    so = await db.get(SalesOrder, so_id)
    if not so:
        raise HTTPException(status_code=404, detail="Sales order not found")
    return so


@router.patch("/{so_id}", response_model=SOOut)
async def update_sales_order(
    so_id: UUID,
    body: SOUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SO_WRITE)),
):
    so = await db.get(SalesOrder, so_id)
    if not so:
        raise HTTPException(status_code=404, detail="Sales order not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(so, field, value)
    await db.flush()
    await db.refresh(so)
    return so


@router.post("/{so_id}/confirm", response_model=SOOut)
async def confirm_so(so_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission(SO_WRITE))):
    return await SalesOrderService(db).confirm(so_id)


@router.post("/{so_id}/fulfill", response_model=SOOut)
async def fulfill_so(so_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(require_permission(SO_WRITE))):
    return await SalesOrderService(db).fulfill(so_id, current_user.id)


@router.post("/{so_id}/ship", response_model=SOOut)
async def ship_so(so_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission(SO_WRITE))):
    return await SalesOrderService(db).ship(so_id)


@router.post("/{so_id}/cancel", response_model=SOOut)
async def cancel_so(so_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(require_permission(SO_WRITE))):
    return await SalesOrderService(db).cancel(so_id)
