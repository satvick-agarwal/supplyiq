from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import ShipmentCreate, ShipmentStatusUpdate, ShipmentOut, PaginatedResponse
from app.models.shipment import Shipment, ShipmentStatus
from app.core.security import require_permission
from app.core.permissions import SHIPMENT_READ, SHIPMENT_WRITE, SHIPMENT_DELETE

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("", response_model=PaginatedResponse)
async def list_shipments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    shipment_type: Optional[str] = None,
    status: Optional[str] = None,
    reference_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SHIPMENT_READ)),
):
    skip = (page - 1) * page_size
    query = select(Shipment)
    if shipment_type:
        query = query.where(Shipment.shipment_type == shipment_type)
    if status:
        query = query.where(Shipment.status == status)
    if reference_id:
        query = query.where(Shipment.reference_id == reference_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size).order_by(Shipment.created_at.desc()))
    return PaginatedResponse(
        items=[ShipmentOut.model_validate(s) for s in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=ShipmentOut, status_code=201)
async def create_shipment(
    body: ShipmentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SHIPMENT_WRITE)),
):
    shipment = Shipment(**body.model_dump())
    db.add(shipment)
    await db.flush()
    await db.refresh(shipment)
    return shipment


@router.get("/{shipment_id}", response_model=ShipmentOut)
async def get_shipment(
    shipment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SHIPMENT_READ)),
):
    shipment = await db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.patch("/{shipment_id}", response_model=ShipmentOut)
async def update_shipment(
    shipment_id: UUID,
    body: ShipmentCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SHIPMENT_WRITE)),
):
    shipment = await db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(shipment, field, value)
    await db.flush()
    await db.refresh(shipment)
    return shipment


@router.post("/{shipment_id}/status", response_model=ShipmentOut)
async def update_shipment_status(
    shipment_id: UUID,
    body: ShipmentStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SHIPMENT_WRITE)),
):
    shipment = await db.get(Shipment, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    new_status = ShipmentStatus(body.status)
    shipment.status = new_status
    if new_status == ShipmentStatus.DELIVERED:
        shipment.delivered_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(shipment)
    return shipment
