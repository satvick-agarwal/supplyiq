from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import POCreate, POUpdate, POOut, POReceiveRequest, PaginatedResponse
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.services.purchase_order_service import PurchaseOrderService
from app.core.security import require_permission
from app.core.permissions import PO_READ, PO_WRITE, PO_APPROVE, PO_DELETE

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])


@router.get("", response_model=PaginatedResponse)
async def list_pos(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    supplier_id: Optional[UUID] = None,
    warehouse_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PO_READ)),
):
    skip = (page - 1) * page_size
    query = select(PurchaseOrder)
    if status:
        query = query.where(PurchaseOrder.status == status)
    if supplier_id:
        query = query.where(PurchaseOrder.supplier_id == supplier_id)
    if warehouse_id:
        query = query.where(PurchaseOrder.warehouse_id == warehouse_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(
        query.offset(skip).limit(page_size).order_by(PurchaseOrder.created_at.desc())
    )
    items = result.scalars().all()
    return PaginatedResponse(
        items=[POOut.model_validate(po) for po in items],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=POOut, status_code=201)
async def create_po(
    body: POCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(PO_WRITE)),
):
    service = PurchaseOrderService(db)
    data = body.model_dump()
    items = data.pop("items")
    po = await service.create_po({**data, "items": items}, current_user.id)
    return po


@router.get("/{po_id}", response_model=POOut)
async def get_po(
    po_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PO_READ)),
):
    po = await db.get(PurchaseOrder, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.patch("/{po_id}", response_model=POOut)
async def update_po(
    po_id: UUID,
    body: POUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PO_WRITE)),
):
    po = await db.get(PurchaseOrder, po_id)
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(po, field, value)
    await db.flush()
    await db.refresh(po)
    return po


@router.post("/{po_id}/approve", response_model=POOut)
async def approve_po(
    po_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(PO_APPROVE)),
):
    service = PurchaseOrderService(db)
    return await service.approve(po_id, current_user.id)


@router.post("/{po_id}/send", response_model=POOut)
async def send_po(
    po_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(PO_WRITE)),
):
    service = PurchaseOrderService(db)
    return await service.send(po_id)


@router.post("/{po_id}/receive", response_model=POOut)
async def receive_po(
    po_id: UUID,
    body: POReceiveRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(PO_WRITE)),
):
    service = PurchaseOrderService(db)
    return await service.receive_items(po_id, [i.model_dump() for i in body.items], current_user.id)


@router.post("/{po_id}/cancel", response_model=POOut)
async def cancel_po(
    po_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PO_WRITE)),
):
    service = PurchaseOrderService(db)
    return await service.cancel(po_id)


@router.post("/{po_id}/close", response_model=POOut)
async def close_po(
    po_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(PO_WRITE)),
):
    service = PurchaseOrderService(db)
    return await service.close(po_id)
