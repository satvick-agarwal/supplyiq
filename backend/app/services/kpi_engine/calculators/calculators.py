"""All KPI Calculators — one module per KPI."""
import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kpi_snapshot import KpiSnapshot, KpiScope
from app.models.inventory_item import InventoryItem
from app.models.inventory_movement import InventoryMovement, MovementType
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, POStatus
from app.models.sales_order import SalesOrder, SalesOrderItem, SOStatus
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.supplier import Supplier
from app.models.category import Category
from app.services.kpi_engine.calculators.base import KpiCalculator


def make_snapshot(kpi_code, scope_type, scope_id, value, snapshot_date, metadata=None):
    return KpiSnapshot(
        id=uuid.uuid4(),
        kpi_code=kpi_code,
        scope_type=scope_type,
        scope_id=scope_id,
        value=Decimal(str(value)) if value is not None else None,
        metadata_=metadata,
        snapshot_date=snapshot_date,
    )


# ── 1. Inventory Turnover ──────────────────────────────────────────────────────

class InventoryTurnoverCalculator(KpiCalculator):
    kpi_code = "inventory_turnover"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        period_start = snapshot_date - timedelta(days=30)
        # COGS proxy = sum of OUT movements in period * unit_cost
        result = await self.db.execute(
            select(func.sum(InventoryMovement.quantity))
            .join(InventoryItem, InventoryMovement.inventory_item_id == InventoryItem.id)
            .where(
                and_(
                    InventoryMovement.movement_type == MovementType.OUT,
                    InventoryMovement.created_at >= period_start,
                    InventoryMovement.created_at <= snapshot_date,
                )
            )
        )
        total_out = float(result.scalar_one() or 0)

        # Avg inventory value proxy = sum of current on-hand quantities
        inv_result = await self.db.execute(
            select(func.sum(InventoryItem.quantity_on_hand * Product.unit_cost))
            .join(Product, InventoryItem.product_id == Product.id)
        )
        avg_inv_value = float(inv_result.scalar_one() or 1)
        turnover = round(total_out / avg_inv_value, 4) if avg_inv_value > 0 else 0

        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, turnover, snapshot_date)]


# ── 2. Dead Stock % ────────────────────────────────────────────────────────────

class DeadStockCalculator(KpiCalculator):
    kpi_code = "dead_stock_pct"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        cutoff = snapshot_date - timedelta(days=90)
        # Products with no OUT movement in last 90 days
        active_products = select(InventoryMovement.inventory_item_id).where(
            and_(
                InventoryMovement.movement_type == MovementType.OUT,
                InventoryMovement.created_at >= cutoff,
            )
        ).distinct()

        dead_value_result = await self.db.execute(
            select(func.sum(InventoryItem.quantity_on_hand * Product.unit_cost))
            .join(Product, InventoryItem.product_id == Product.id)
            .where(InventoryItem.id.not_in(active_products), InventoryItem.quantity_on_hand > 0)
        )
        dead_value = float(dead_value_result.scalar_one() or 0)

        total_value_result = await self.db.execute(
            select(func.sum(InventoryItem.quantity_on_hand * Product.unit_cost))
            .join(Product, InventoryItem.product_id == Product.id)
        )
        total_value = float(total_value_result.scalar_one() or 1)
        pct = round(dead_value / total_value * 100, 2) if total_value > 0 else 0

        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, pct, snapshot_date, {"dead_value": dead_value, "total_value": total_value})]


# ── 3. Stockout Prediction (days until zero) ───────────────────────────────────

class StockoutPredictionCalculator(KpiCalculator):
    kpi_code = "stockout_days"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        period_start = snapshot_date - timedelta(days=30)
        # Get all inventory items
        items = (await self.db.execute(
            select(InventoryItem).join(Product, InventoryItem.product_id == Product.id).where(Product.is_active == True)
        )).scalars().all()

        snapshots = []
        for item in items:
            # Avg daily OUT rate in last 30 days
            out_result = await self.db.execute(
                select(func.sum(InventoryMovement.quantity))
                .where(
                    and_(
                        InventoryMovement.inventory_item_id == item.id,
                        InventoryMovement.movement_type == MovementType.OUT,
                        InventoryMovement.created_at >= period_start,
                    )
                )
            )
            total_out_30d = float(out_result.scalar_one() or 0)
            avg_daily = total_out_30d / 30
            days_until_zero = float(item.quantity_on_hand) / avg_daily if avg_daily > 0 else 999
            snapshots.append(make_snapshot(
                self.kpi_code, KpiScope.PRODUCT, item.product_id,
                round(days_until_zero, 1), snapshot_date,
                {"quantity_on_hand": float(item.quantity_on_hand), "avg_daily_out": round(avg_daily, 4)}
            ))
        return snapshots


# ── 4. Supplier Reliability ────────────────────────────────────────────────────

class SupplierReliabilityCalculator(KpiCalculator):
    kpi_code = "supplier_reliability"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        suppliers = (await self.db.execute(
            select(Supplier).where(Supplier.is_active == True)
        )).scalars().all()

        snapshots = []
        for supplier in suppliers:
            # Count POs: total, on-time (received by expected_date)
            from app.models.purchase_order import PurchaseOrder, POStatus
            total_result = await self.db.execute(
                select(func.count()).where(
                    and_(PurchaseOrder.supplier_id == supplier.id, PurchaseOrder.status.in_([POStatus.RECEIVED, POStatus.CLOSED]))
                )
            )
            total = int(total_result.scalar_one() or 0)

            # Simple heuristic: use existing reliability_score or default 75
            score = float(supplier.reliability_score or 75)
            snapshots.append(make_snapshot(
                self.kpi_code, KpiScope.SUPPLIER, supplier.id, score, snapshot_date,
                {"total_pos": total}
            ))
        return snapshots


# ── 5. Warehouse Utilization ───────────────────────────────────────────────────

class WarehouseUtilizationCalculator(KpiCalculator):
    kpi_code = "warehouse_utilization"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        warehouses = (await self.db.execute(select(Warehouse))).scalars().all()
        snapshots = []
        for wh in warehouses:
            qty_result = await self.db.execute(
                select(func.sum(InventoryItem.quantity_on_hand)).where(InventoryItem.warehouse_id == wh.id)
            )
            total_qty = float(qty_result.scalar_one() or 0)
            capacity = float(wh.capacity_units or 1)
            pct = round(total_qty / capacity * 100, 2) if capacity > 0 else 0
            snapshots.append(make_snapshot(
                self.kpi_code, KpiScope.WAREHOUSE, wh.id, pct, snapshot_date,
                {"total_qty": total_qty, "capacity": capacity}
            ))
        return snapshots


# ── 6. Revenue Analytics ───────────────────────────────────────────────────────

class RevenueAnalyticsCalculator(KpiCalculator):
    kpi_code = "revenue_mtd"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        mtd_start = snapshot_date.replace(day=1)
        result = await self.db.execute(
            select(func.sum(SalesOrderItem.quantity_ordered * SalesOrderItem.unit_price))
            .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
            .where(
                and_(
                    SalesOrder.order_date >= mtd_start,
                    SalesOrder.order_date <= snapshot_date,
                    SalesOrder.status.not_in([SOStatus.CANCELLED]),
                )
            )
        )
        revenue = float(result.scalar_one() or 0)
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, revenue, snapshot_date)]


# ── 7. Cost Analytics ──────────────────────────────────────────────────────────

class CostAnalyticsCalculator(KpiCalculator):
    kpi_code = "cost_mtd"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        mtd_start = snapshot_date.replace(day=1)
        result = await self.db.execute(
            select(func.sum(PurchaseOrderItem.quantity_ordered * PurchaseOrderItem.unit_cost))
            .join(PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id)
            .where(
                and_(
                    PurchaseOrder.order_date >= mtd_start,
                    PurchaseOrder.order_date <= snapshot_date,
                    PurchaseOrder.status.not_in([POStatus.CANCELLED]),
                )
            )
        )
        cost = float(result.scalar_one() or 0)
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, cost, snapshot_date)]


# ── 8. Profit Analysis ─────────────────────────────────────────────────────────

class ProfitAnalysisCalculator(KpiCalculator):
    kpi_code = "profit_margin_pct"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        mtd_start = snapshot_date.replace(day=1)
        rev_result = await self.db.execute(
            select(func.sum(SalesOrderItem.quantity_ordered * SalesOrderItem.unit_price))
            .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
            .where(
                and_(
                    SalesOrder.order_date >= mtd_start,
                    SalesOrder.status.not_in([SOStatus.CANCELLED]),
                )
            )
        )
        revenue = float(rev_result.scalar_one() or 0)
        # COGS from SO items matched with product unit_cost
        cogs_result = await self.db.execute(
            select(func.sum(SalesOrderItem.quantity_ordered * Product.unit_cost))
            .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
            .join(Product, SalesOrderItem.product_id == Product.id)
            .where(
                and_(
                    SalesOrder.order_date >= mtd_start,
                    SalesOrder.status.not_in([SOStatus.CANCELLED]),
                )
            )
        )
        cogs = float(cogs_result.scalar_one() or 0)
        margin_pct = round((revenue - cogs) / revenue * 100, 2) if revenue > 0 else 0
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, margin_pct, snapshot_date, {"revenue": revenue, "cogs": cogs})]


# ── 9. Order Fulfillment Rate ──────────────────────────────────────────────────

class OrderFulfillmentRateCalculator(KpiCalculator):
    kpi_code = "order_fulfillment_rate"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        period_start = snapshot_date - timedelta(days=30)
        ordered_result = await self.db.execute(
            select(func.sum(SalesOrderItem.quantity_ordered))
            .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
            .where(
                and_(
                    SalesOrder.order_date >= period_start,
                    SalesOrder.status.not_in([SOStatus.CANCELLED]),
                )
            )
        )
        fulfilled_result = await self.db.execute(
            select(func.sum(SalesOrderItem.quantity_fulfilled))
            .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
            .where(SalesOrder.order_date >= period_start)
        )
        ordered = float(ordered_result.scalar_one() or 1)
        fulfilled = float(fulfilled_result.scalar_one() or 0)
        rate = round(fulfilled / ordered * 100, 2) if ordered > 0 else 0
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, rate, snapshot_date)]


# ── 10. Monthly Growth ─────────────────────────────────────────────────────────

class MonthlyGrowthCalculator(KpiCalculator):
    kpi_code = "monthly_growth_pct"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        this_month_start = snapshot_date.replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        async def get_revenue(start, end):
            result = await self.db.execute(
                select(func.sum(SalesOrderItem.quantity_ordered * SalesOrderItem.unit_price))
                .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
                .where(
                    and_(
                        SalesOrder.order_date >= start,
                        SalesOrder.order_date <= end,
                        SalesOrder.status.not_in([SOStatus.CANCELLED]),
                    )
                )
            )
            return float(result.scalar_one() or 0)

        this_month_rev = await get_revenue(this_month_start, snapshot_date)
        last_month_rev = await get_revenue(last_month_start, last_month_end)
        growth = round((this_month_rev - last_month_rev) / last_month_rev * 100, 2) if last_month_rev > 0 else 0
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, growth, snapshot_date, {"this_month": this_month_rev, "last_month": last_month_rev})]


# ── 11. Demand Trends ──────────────────────────────────────────────────────────

class DemandTrendsCalculator(KpiCalculator):
    kpi_code = "demand_30d"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        period_start = snapshot_date - timedelta(days=30)
        result = await self.db.execute(
            select(func.sum(SalesOrderItem.quantity_ordered))
            .join(SalesOrder, SalesOrderItem.sales_order_id == SalesOrder.id)
            .where(
                and_(
                    SalesOrder.order_date >= period_start,
                    SalesOrder.status.not_in([SOStatus.CANCELLED]),
                )
            )
        )
        demand = float(result.scalar_one() or 0)
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, demand, snapshot_date)]


# ── 12. Purchase Trends ────────────────────────────────────────────────────────

class PurchaseTrendsCalculator(KpiCalculator):
    kpi_code = "purchase_spend_30d"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        period_start = snapshot_date - timedelta(days=30)
        result = await self.db.execute(
            select(func.sum(PurchaseOrderItem.quantity_ordered * PurchaseOrderItem.unit_cost))
            .join(PurchaseOrder, PurchaseOrderItem.purchase_order_id == PurchaseOrder.id)
            .where(
                and_(
                    PurchaseOrder.order_date >= period_start,
                    PurchaseOrder.status.not_in([POStatus.CANCELLED]),
                )
            )
        )
        spend = float(result.scalar_one() or 0)
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, spend, snapshot_date)]


# ── 13. Lead Time Analysis ─────────────────────────────────────────────────────

class LeadTimeAnalysisCalculator(KpiCalculator):
    kpi_code = "lead_time_analysis"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        suppliers = (await self.db.execute(select(Supplier).where(Supplier.is_active == True))).scalars().all()
        snapshots = []
        for supplier in suppliers:
            # Avg lead time from order_date to receive date for received POs
            avg_lead = supplier.average_lead_time_days or 14
            snapshots.append(make_snapshot(
                self.kpi_code, KpiScope.SUPPLIER, supplier.id, avg_lead, snapshot_date
            ))
        return snapshots


# ── 14. Inventory Aging ────────────────────────────────────────────────────────

class InventoryAgingCalculator(KpiCalculator):
    kpi_code = "inventory_aging_over_90d_pct"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        # Items with no inbound movement in 90+ days are "aged"
        cutoff = snapshot_date - timedelta(days=90)
        recent = select(InventoryMovement.inventory_item_id).where(
            and_(
                InventoryMovement.movement_type == MovementType.IN,
                InventoryMovement.created_at >= cutoff,
            )
        ).distinct()
        aged_result = await self.db.execute(
            select(func.count()).select_from(InventoryItem).where(InventoryItem.id.not_in(recent))
        )
        total_result = await self.db.execute(select(func.count()).select_from(InventoryItem))
        aged = int(aged_result.scalar_one() or 0)
        total = int(total_result.scalar_one() or 1)
        pct = round(aged / total * 100, 2) if total > 0 else 0
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, pct, snapshot_date, {"aged_items": aged, "total_items": total})]


# ── 15. Business Health Score ──────────────────────────────────────────────────

class BusinessHealthScoreCalculator(KpiCalculator):
    kpi_code = "business_health_score"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        # Weighted composite: revenue_growth (30%) + margin (30%) + fulfillment (25%) + inventory turnover (15%)
        # Pull from latest snapshots
        from sqlalchemy import desc

        async def get_latest(code, scope=KpiScope.GLOBAL):
            r = await self.db.execute(
                select(KpiSnapshot).where(
                    and_(KpiSnapshot.kpi_code == code, KpiSnapshot.scope_type == scope)
                ).order_by(desc(KpiSnapshot.snapshot_date)).limit(1)
            )
            s = r.scalar_one_or_none()
            return float(s.value or 0) if s else 0

        growth = await get_latest("monthly_growth_pct")
        margin = await get_latest("profit_margin_pct")
        fulfillment = await get_latest("order_fulfillment_rate")
        turnover = await get_latest("inventory_turnover")

        # Normalize each to 0-100 scale
        growth_norm = min(max((growth + 20) / 40 * 100, 0), 100)  # -20% to +20% → 0-100
        margin_norm = min(max(margin / 40 * 100, 0), 100)  # 0-40% margin → 0-100
        fulfillment_norm = min(max(fulfillment, 0), 100)
        turnover_norm = min(max(turnover / 12 * 100, 0), 100)  # 0-12x → 0-100

        score = round(
            growth_norm * 0.30 +
            margin_norm * 0.30 +
            fulfillment_norm * 0.25 +
            turnover_norm * 0.15,
            1
        )
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, score, snapshot_date, {
            "growth_score": growth_norm, "margin_score": margin_norm,
            "fulfillment_score": fulfillment_norm, "turnover_score": turnover_norm
        })]


# ── 16. Supply Chain Efficiency Score ─────────────────────────────────────────

class SupplyChainEfficiencyCalculator(KpiCalculator):
    kpi_code = "supply_chain_efficiency"

    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        from sqlalchemy import desc

        async def get_latest(code):
            r = await self.db.execute(
                select(KpiSnapshot).where(
                    and_(KpiSnapshot.kpi_code == code, KpiSnapshot.scope_type == KpiScope.GLOBAL)
                ).order_by(desc(KpiSnapshot.snapshot_date)).limit(1)
            )
            s = r.scalar_one_or_none()
            return float(s.value or 0) if s else 0

        turnover = await get_latest("inventory_turnover")
        fulfillment = await get_latest("order_fulfillment_rate")
        dead_stock = await get_latest("dead_stock_pct")

        turnover_norm = min(turnover / 12 * 100, 100)
        dead_stock_norm = max(100 - dead_stock * 2, 0)

        score = round(
            turnover_norm * 0.40 +
            fulfillment * 0.40 +
            dead_stock_norm * 0.20,
            1
        )
        return [make_snapshot(self.kpi_code, KpiScope.GLOBAL, None, score, snapshot_date)]
