from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from uuid import UUID
from datetime import date
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import KpiSnapshotOut, PaginatedResponse
from app.models.kpi_snapshot import KpiSnapshot, KpiScope
from app.services.kpi_engine.engine import KpiEngine
from app.core.security import require_permission
from app.core.permissions import KPI_READ, KPI_RECOMPUTE

router = APIRouter(prefix="/kpis", tags=["KPI Engine"])


@router.get("", response_model=PaginatedResponse)
async def list_kpis(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    kpi_code: Optional[str] = None,
    scope_type: Optional[str] = None,
    scope_id: Optional[UUID] = None,
    snapshot_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(KPI_READ)),
):
    skip = (page - 1) * page_size
    query = select(KpiSnapshot)
    if kpi_code:
        query = query.where(KpiSnapshot.kpi_code == kpi_code)
    if scope_type:
        query = query.where(KpiSnapshot.scope_type == scope_type)
    if scope_id:
        query = query.where(KpiSnapshot.scope_id == scope_id)
    if snapshot_date:
        query = query.where(KpiSnapshot.snapshot_date == snapshot_date)
    else:
        # Default: latest snapshot for each kpi_code + scope
        pass  # Return all, let client filter
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(desc(KpiSnapshot.snapshot_date)).offset(skip).limit(page_size))
    return PaginatedResponse(
        items=[KpiSnapshotOut.model_validate(s) for s in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.get("/latest")
async def get_latest_kpis(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(KPI_READ)),
):
    """Get the most recent snapshot for each global KPI."""
    global_kpi_codes = [
        "inventory_turnover", "dead_stock_pct", "revenue_mtd", "cost_mtd",
        "profit_margin_pct", "order_fulfillment_rate", "monthly_growth_pct",
        "demand_30d", "purchase_spend_30d", "inventory_aging_over_90d_pct",
        "business_health_score", "supply_chain_efficiency",
    ]
    result = {}
    for code in global_kpi_codes:
        r = await db.execute(
            select(KpiSnapshot)
            .where(and_(KpiSnapshot.kpi_code == code, KpiSnapshot.scope_type == KpiScope.GLOBAL))
            .order_by(desc(KpiSnapshot.snapshot_date))
            .limit(1)
        )
        snap = r.scalar_one_or_none()
        result[code] = KpiSnapshotOut.model_validate(snap) if snap else None
    return result


@router.get("/{kpi_code}/history")
async def get_kpi_history(
    kpi_code: str,
    scope_type: str = "GLOBAL",
    scope_id: Optional[UUID] = None,
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(KPI_READ)),
):
    from datetime import timedelta
    cutoff = date.today() - timedelta(days=days)
    query = select(KpiSnapshot).where(
        and_(
            KpiSnapshot.kpi_code == kpi_code,
            KpiSnapshot.scope_type == scope_type,
            KpiSnapshot.snapshot_date >= cutoff,
        )
    )
    if scope_id:
        query = query.where(KpiSnapshot.scope_id == scope_id)
    result = await db.execute(query.order_by(KpiSnapshot.snapshot_date))
    return [KpiSnapshotOut.model_validate(s) for s in result.scalars().all()]


@router.post("/recompute")
async def recompute_kpis(
    background_tasks: BackgroundTasks,
    snapshot_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(KPI_RECOMPUTE)),
):
    """Trigger on-demand KPI recomputation (Admin only)."""
    target_date = snapshot_date or date.today()

    async def _run():
        engine = KpiEngine(db)
        count = await engine.run_all(target_date)
        await db.commit()

    background_tasks.add_task(_run)
    return {"message": f"KPI recomputation triggered for {target_date}", "status": "running"}
