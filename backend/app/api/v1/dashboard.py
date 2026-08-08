from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from datetime import date

from app.db.session import get_db
from app.core.security import require_permission
from app.core.permissions import DASHBOARD_OPERATIONAL, DASHBOARD_FINANCIAL, KPI_READ
from app.models.kpi_snapshot import KpiSnapshot, KpiScope
from app.models.alert import Alert, AlertStatus, AlertSeverity
from app.models.ai_insight import AiInsight
from app.models.purchase_order import PurchaseOrder, POStatus
from app.models.sales_order import SalesOrder, SOStatus
from app.models.warehouse import Warehouse
from app.models.inventory_item import InventoryItem
from app.schemas.schemas import AiInsightOut, AlertOut, KpiSnapshotOut

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


async def get_latest_kpi(db: AsyncSession, code: str, scope=KpiScope.GLOBAL, scope_id=None):
    query = select(KpiSnapshot).where(
        and_(KpiSnapshot.kpi_code == code, KpiSnapshot.scope_type == scope)
    )
    if scope_id:
        query = query.where(KpiSnapshot.scope_id == scope_id)
    result = await db.execute(query.order_by(desc(KpiSnapshot.snapshot_date)).limit(1))
    snap = result.scalar_one_or_none()
    return float(snap.value or 0) if snap else 0, snap.metadata_ if snap else {}


@router.get("/executive")
async def executive_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_permission(DASHBOARD_OPERATIONAL)),
):
    """
    Aggregated executive dashboard response.
    Combines: KPIs, alerts, AI insights, PO/SO summaries, warehouse utilization.
    """
    # ── KPI Strip ──────────────────────────────────────────────────────────────
    health_score, _ = await get_latest_kpi(db, "business_health_score")
    efficiency_score, _ = await get_latest_kpi(db, "supply_chain_efficiency")
    revenue_mtd, _ = await get_latest_kpi(db, "revenue_mtd")
    profit_margin, margin_meta = await get_latest_kpi(db, "profit_margin_pct")
    monthly_growth, growth_meta = await get_latest_kpi(db, "monthly_growth_pct")
    inventory_turnover, _ = await get_latest_kpi(db, "inventory_turnover")
    dead_stock_pct, dead_meta = await get_latest_kpi(db, "dead_stock_pct")
    fulfillment_rate, _ = await get_latest_kpi(db, "order_fulfillment_rate")
    cost_mtd, _ = await get_latest_kpi(db, "cost_mtd")

    # ── Open Alerts ────────────────────────────────────────────────────────────
    alerts_result = await db.execute(
        select(Alert)
        .where(Alert.status == AlertStatus.OPEN)
        .order_by(Alert.created_at.desc())
        .limit(10)
    )
    open_alerts = [AlertOut.model_validate(a) for a in alerts_result.scalars().all()]

    critical_count = sum(1 for a in open_alerts if a.severity == "critical")
    warning_count = sum(1 for a in open_alerts if a.severity == "warning")

    # ── AI Insights ────────────────────────────────────────────────────────────
    from app.models.ai_insight import InsightSeverity
    insights_result = await db.execute(
        select(AiInsight).order_by(desc(AiInsight.generated_at)).limit(10)
    )
    all_insights = insights_result.scalars().all()
    sev_order = {InsightSeverity.CRITICAL: 0, InsightSeverity.WARNING: 1, InsightSeverity.INFO: 2}
    sorted_insights = sorted(all_insights, key=lambda x: (sev_order.get(x.severity, 3), -x.generated_at.timestamp()))
    top_insights = [AiInsightOut.model_validate(i) for i in sorted_insights[:5]]

    # ── Open POs ───────────────────────────────────────────────────────────────
    open_po_count_result = await db.execute(
        select(func.count()).where(
            PurchaseOrder.status.in_([POStatus.DRAFT, POStatus.APPROVED, POStatus.SENT, POStatus.PARTIALLY_RECEIVED])
        )
    )
    open_pos = int(open_po_count_result.scalar_one() or 0)

    # ── Open SOs ───────────────────────────────────────────────────────────────
    open_so_count_result = await db.execute(
        select(func.count()).where(
            SalesOrder.status.in_([SOStatus.DRAFT, SOStatus.CONFIRMED, SOStatus.FULFILLED])
        )
    )
    open_sos = int(open_so_count_result.scalar_one() or 0)

    # ── Warehouse Utilization ──────────────────────────────────────────────────
    warehouses = (await db.execute(select(Warehouse))).scalars().all()
    warehouse_utilization = []
    for wh in warehouses:
        pct, meta = await get_latest_kpi(db, "warehouse_utilization", KpiScope.WAREHOUSE, wh.id)
        warehouse_utilization.append({
            "id": str(wh.id),
            "name": wh.name,
            "utilization_pct": pct,
            "total_qty": meta.get("total_qty", 0) if meta else 0,
            "capacity": meta.get("capacity", 0) if meta else 0,
        })

    # ── Inventory summary ──────────────────────────────────────────────────────
    low_stock_count_result = await db.execute(
        select(func.count()).select_from(InventoryItem).join(
            __import__('app.models.product', fromlist=['Product']).Product,
            InventoryItem.product_id == __import__('app.models.product', fromlist=['Product']).Product.id
        ).where(
            InventoryItem.quantity_on_hand <= __import__('app.models.product', fromlist=['Product']).Product.reorder_point
        )
    )
    low_stock_count = int(low_stock_count_result.scalar_one() or 0)

    return {
        "kpis": {
            "business_health_score": health_score,
            "supply_chain_efficiency": efficiency_score,
            "revenue_mtd": revenue_mtd,
            "cost_mtd": cost_mtd,
            "profit_margin_pct": profit_margin,
            "monthly_growth_pct": monthly_growth,
            "monthly_growth_meta": growth_meta,
            "inventory_turnover": inventory_turnover,
            "dead_stock_pct": dead_stock_pct,
            "dead_stock_meta": dead_meta,
            "order_fulfillment_rate": fulfillment_rate,
        },
        "alerts_summary": {
            "total_open": len(open_alerts),
            "critical": critical_count,
            "warning": warning_count,
            "top_alerts": open_alerts[:5],
        },
        "ai_insights": top_insights,
        "operational": {
            "open_purchase_orders": open_pos,
            "open_sales_orders": open_sos,
            "low_stock_items": low_stock_count,
            "warehouse_utilization": warehouse_utilization,
        },
    }
