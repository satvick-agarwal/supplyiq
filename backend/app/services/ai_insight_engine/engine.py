"""
AI Insight Engine — Template-Based (Mock) Implementation
=========================================================
Architecture: Rules-first, template narration-second.
1. Rule-based candidate detection identifies observations (metric crossed threshold)
2. Template-based narration formats them into natural language
3. Clean provider interface allows real LLM to be swapped in later
"""
import uuid
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.kpi_snapshot import KpiSnapshot, KpiScope
from app.models.ai_insight import AiInsight, InsightCategory, InsightSeverity
from app.models.inventory_item import InventoryItem
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.supplier import Supplier

logger = logging.getLogger("supplyiq.ai_insights")


class TemplateInsightProvider:
    """Mock LLM provider — uses pre-written templates."""

    def narrate(self, template_key: str, context: dict) -> str:
        templates = {
            "low_stock_warning": (
                "⚠️ {product_name} (SKU: {sku}) has only {qty:.0f} units remaining in {warehouse_name}, "
                "with an estimated {days:.0f} days of stock left at the current sell-through rate. "
                "Consider reordering {reorder_qty:.0f} units from the preferred supplier."
            ),
            "stockout_critical": (
                "🚨 STOCKOUT: {product_name} (SKU: {sku}) has zero stock in {warehouse_name}. "
                "This is causing fulfillment failures. Immediate replenishment action required."
            ),
            "dead_stock_high": (
                "📦 Dead stock is at {pct:.1f}% of total inventory value (${value:,.0f}), "
                "exceeding the healthy threshold of 10%. Consider a clearance promotion "
                "or return-to-supplier agreement for aging SKUs with no movement in 90+ days."
            ),
            "warehouse_capacity": (
                "🏭 {warehouse_name} is at {pct:.1f}% capacity ({qty:,.0f}/{capacity:,.0f} units). "
                "{action}"
            ),
            "supplier_delay": (
                "⏰ {supplier_name} has a reliability score of {score:.0f}/100, "
                "with an average lead time of {lead_time} days. "
                "Consider qualifying a backup supplier for critical SKUs."
            ),
            "revenue_growth": (
                "📈 Revenue grew {growth:+.1f}% month-over-month (${this_month:,.0f} vs ${last_month:,.0f}). "
                "{commentary}"
            ),
            "margin_low": (
                "💰 Profit margin is at {margin:.1f}%, below the healthy threshold of 20%. "
                "Review pricing on high-volume SKUs and negotiate better terms with suppliers."
            ),
            "fulfillment_low": (
                "📋 Order fulfillment rate dropped to {rate:.1f}% in the last 30 days. "
                "Low stock on key SKUs is likely causing fulfillment failures. "
                "Review low-stock alerts and prioritize restocking."
            ),
            "inventory_turnover_low": (
                "🔄 Inventory turnover is {turnover:.2f}x, below the industry benchmark of 4x. "
                "Capital is being tied up in slow-moving inventory. "
                "Identify and liquidate dead stock to improve cash flow."
            ),
        }
        template = templates.get(template_key, "{template_key}: {context}")
        try:
            return template.format(**context)
        except (KeyError, ValueError):
            return f"Insight: {template_key}"


class AiInsightEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = TemplateInsightProvider()

    async def generate_all(self, target_date: date = None) -> int:
        if target_date is None:
            target_date = date.today()

        insights = []
        insights += await self._inventory_insights(target_date)
        insights += await self._warehouse_insights(target_date)
        insights += await self._supplier_insights(target_date)
        insights += await self._financial_insights(target_date)

        for insight in insights:
            self.db.add(insight)
        await self.db.flush()
        logger.info(f"Generated {len(insights)} AI insights for {target_date}")
        return len(insights)

    async def _get_kpi(self, code: str, scope=KpiScope.GLOBAL, scope_id=None):
        query = select(KpiSnapshot).where(
            and_(KpiSnapshot.kpi_code == code, KpiSnapshot.scope_type == scope)
        )
        if scope_id:
            query = query.where(KpiSnapshot.scope_id == scope_id)
        result = await self.db.execute(query.order_by(desc(KpiSnapshot.snapshot_date)).limit(1))
        snap = result.scalar_one_or_none()
        return float(snap.value or 0) if snap else None, snap.metadata_ if snap else {}

    async def _inventory_insights(self, target_date: date) -> List[AiInsight]:
        insights = []
        # Dead stock
        pct, meta = await self._get_kpi("dead_stock_pct")
        if pct is not None and pct > 10:
            text = self.provider.narrate("dead_stock_high", {
                "pct": pct, "value": meta.get("dead_value", 0) if meta else 0
            })
            insights.append(AiInsight(
                id=uuid.uuid4(),
                category=InsightCategory.INVENTORY,
                insight_text=text,
                confidence_score=Decimal("0.90"),
                severity=InsightSeverity.WARNING if pct < 20 else InsightSeverity.CRITICAL,
                model_version="template-v1",
            ))

        # Stockout prediction — flag items with < 7 days
        stockout_snaps = (await self.db.execute(
            select(KpiSnapshot).where(
                and_(
                    KpiSnapshot.kpi_code == "stockout_days",
                    KpiSnapshot.scope_type == KpiScope.PRODUCT,
                    KpiSnapshot.value <= 7,
                    KpiSnapshot.value >= 0,
                )
            ).order_by(KpiSnapshot.value).limit(5)
        )).scalars().all()

        for snap in stockout_snaps:
            product = await self.db.get(Product, snap.scope_id)
            if not product:
                continue
            meta = snap.metadata_ or {}
            qty = meta.get("quantity_on_hand", 0)
            is_stockout = float(qty) <= 0
            key = "stockout_critical" if is_stockout else "low_stock_warning"
            text = self.provider.narrate(key, {
                "product_name": product.name,
                "sku": product.sku,
                "qty": float(qty),
                "days": float(snap.value or 0),
                "warehouse_name": "primary warehouse",
                "reorder_qty": float(product.reorder_quantity),
            })
            insights.append(AiInsight(
                id=uuid.uuid4(),
                category=InsightCategory.INVENTORY,
                entity_type="product",
                entity_id=product.id,
                insight_text=text,
                confidence_score=Decimal("0.95"),
                severity=InsightSeverity.CRITICAL if is_stockout else InsightSeverity.WARNING,
                model_version="template-v1",
            ))

        # Inventory turnover
        turnover, _ = await self._get_kpi("inventory_turnover")
        if turnover is not None and turnover < 2:
            text = self.provider.narrate("inventory_turnover_low", {"turnover": turnover})
            insights.append(AiInsight(
                id=uuid.uuid4(),
                category=InsightCategory.INVENTORY,
                insight_text=text,
                confidence_score=Decimal("0.85"),
                severity=InsightSeverity.WARNING,
                model_version="template-v1",
            ))

        return insights

    async def _warehouse_insights(self, target_date: date) -> List[AiInsight]:
        insights = []
        warehouses = (await self.db.execute(select(Warehouse))).scalars().all()
        for wh in warehouses:
            pct, meta = await self._get_kpi("warehouse_utilization", KpiScope.WAREHOUSE, wh.id)
            if pct is None:
                continue
            if pct >= 85:
                action = "Plan stock redistribution immediately." if pct >= 95 else "Consider redistributing slow-moving stock to other warehouses."
                text = self.provider.narrate("warehouse_capacity", {
                    "warehouse_name": wh.name, "pct": pct,
                    "qty": meta.get("total_qty", 0) if meta else 0,
                    "capacity": meta.get("capacity", 1) if meta else 1,
                    "action": action,
                })
                insights.append(AiInsight(
                    id=uuid.uuid4(),
                    category=InsightCategory.WAREHOUSE,
                    entity_type="warehouse",
                    entity_id=wh.id,
                    insight_text=text,
                    confidence_score=Decimal("0.92"),
                    severity=InsightSeverity.CRITICAL if pct >= 95 else InsightSeverity.WARNING,
                    model_version="template-v1",
                ))
        return insights

    async def _supplier_insights(self, target_date: date) -> List[AiInsight]:
        insights = []
        suppliers = (await self.db.execute(select(Supplier).where(Supplier.is_active == True))).scalars().all()
        for supplier in suppliers:
            score, _ = await self._get_kpi("supplier_reliability", KpiScope.SUPPLIER, supplier.id)
            if score is not None and score < 70:
                text = self.provider.narrate("supplier_delay", {
                    "supplier_name": supplier.name,
                    "score": score,
                    "lead_time": supplier.average_lead_time_days or "unknown",
                })
                insights.append(AiInsight(
                    id=uuid.uuid4(),
                    category=InsightCategory.SUPPLIER,
                    entity_type="supplier",
                    entity_id=supplier.id,
                    insight_text=text,
                    confidence_score=Decimal("0.88"),
                    severity=InsightSeverity.WARNING,
                    model_version="template-v1",
                ))
        return insights

    async def _financial_insights(self, target_date: date) -> List[AiInsight]:
        insights = []
        # Revenue growth
        growth, meta = await self._get_kpi("monthly_growth_pct")
        if growth is not None:
            meta = meta or {}
            commentary = "Strong performance — maintain momentum." if growth > 10 else (
                "Growth is slowing. Review pricing and sales strategies." if growth > 0 else
                "Revenue is declining. Immediate strategic review needed."
            )
            text = self.provider.narrate("revenue_growth", {
                "growth": growth, "commentary": commentary,
                "this_month": meta.get("this_month", 0),
                "last_month": meta.get("last_month", 0),
            })
            insights.append(AiInsight(
                id=uuid.uuid4(),
                category=InsightCategory.FINANCIAL,
                insight_text=text,
                confidence_score=Decimal("0.95"),
                severity=InsightSeverity.CRITICAL if growth < -10 else (InsightSeverity.WARNING if growth < 0 else InsightSeverity.INFO),
                model_version="template-v1",
            ))

        # Profit margin
        margin, _ = await self._get_kpi("profit_margin_pct")
        if margin is not None and margin < 20:
            text = self.provider.narrate("margin_low", {"margin": margin})
            insights.append(AiInsight(
                id=uuid.uuid4(),
                category=InsightCategory.FINANCIAL,
                insight_text=text,
                confidence_score=Decimal("0.90"),
                severity=InsightSeverity.WARNING,
                model_version="template-v1",
            ))

        # Fulfillment rate
        fulfillment, _ = await self._get_kpi("order_fulfillment_rate")
        if fulfillment is not None and fulfillment < 90:
            text = self.provider.narrate("fulfillment_low", {"rate": fulfillment})
            insights.append(AiInsight(
                id=uuid.uuid4(),
                category=InsightCategory.SALES,
                insight_text=text,
                confidence_score=Decimal("0.92"),
                severity=InsightSeverity.WARNING,
                model_version="template-v1",
            ))

        return insights
