from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import SupplierCreate, SupplierUpdate, SupplierOut, PaginatedResponse
from app.models.supplier import Supplier
from app.core.security import require_permission
from app.core.permissions import SUPPLIER_READ, SUPPLIER_WRITE, SUPPLIER_DELETE

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=PaginatedResponse)
async def list_suppliers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SUPPLIER_READ)),
):
    skip = (page - 1) * page_size
    query = select(Supplier)
    if is_active is not None:
        query = query.where(Supplier.is_active == is_active)
    if search:
        query = query.where(Supplier.name.ilike(f"%{search}%"))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size).order_by(Supplier.name))
    return PaginatedResponse(
        items=[SupplierOut.model_validate(s) for s in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=SupplierOut, status_code=201)
async def create_supplier(
    body: SupplierCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SUPPLIER_WRITE)),
):
    supplier = Supplier(**body.model_dump())
    db.add(supplier)
    await db.flush()
    await db.refresh(supplier)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierOut)
async def get_supplier(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SUPPLIER_READ)),
):
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.patch("/{supplier_id}", response_model=SupplierOut)
async def update_supplier(
    supplier_id: UUID,
    body: SupplierUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SUPPLIER_WRITE)),
):
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(supplier, field, value)
    await db.flush()
    await db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=204)
async def delete_supplier(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SUPPLIER_DELETE)),
):
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier.is_active = False
    await db.flush()


@router.get("/{supplier_id}/scorecard")
async def get_supplier_scorecard(
    supplier_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SUPPLIER_READ)),
):
    """Supplier reliability scorecard — computed from KPI snapshots."""
    supplier = await db.get(Supplier, supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    from app.models.kpi_snapshot import KpiSnapshot, KpiScope
    from sqlalchemy import and_, desc
    from datetime import date

    # Pull latest KPI snapshots for this supplier
    kpis = {}
    for kpi_code in ["supplier_reliability", "lead_time_analysis"]:
        result = await db.execute(
            select(KpiSnapshot)
            .where(
                and_(
                    KpiSnapshot.kpi_code == kpi_code,
                    KpiSnapshot.scope_type == KpiScope.SUPPLIER,
                    KpiSnapshot.scope_id == supplier_id,
                )
            )
            .order_by(desc(KpiSnapshot.snapshot_date))
            .limit(1)
        )
        snap = result.scalar_one_or_none()
        if snap:
            kpis[kpi_code] = {"value": float(snap.value or 0), "metadata": snap.metadata_}

    # Count POs for this supplier
    from app.models.purchase_order import PurchaseOrder, POStatus
    po_result = await db.execute(
        select(func.count()).where(PurchaseOrder.supplier_id == supplier_id)
    )
    total_pos = po_result.scalar_one()

    return {
        "supplier_id": str(supplier_id),
        "supplier_name": supplier.name,
        "reliability_score": float(supplier.reliability_score or 0),
        "average_lead_time_days": supplier.average_lead_time_days,
        "total_purchase_orders": total_pos,
        "kpis": kpis,
    }
