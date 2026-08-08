"""
KPI Engine — Orchestrator
=========================
Runs all calculators and persists KpiSnapshot rows.
"""
import logging
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from app.models.kpi_snapshot import KpiSnapshot
from app.services.kpi_engine.calculators.calculators import (
    InventoryTurnoverCalculator,
    DeadStockCalculator,
    StockoutPredictionCalculator,
    SupplierReliabilityCalculator,
    WarehouseUtilizationCalculator,
    RevenueAnalyticsCalculator,
    CostAnalyticsCalculator,
    ProfitAnalysisCalculator,
    OrderFulfillmentRateCalculator,
    MonthlyGrowthCalculator,
    DemandTrendsCalculator,
    PurchaseTrendsCalculator,
    LeadTimeAnalysisCalculator,
    InventoryAgingCalculator,
    BusinessHealthScoreCalculator,
    SupplyChainEfficiencyCalculator,
)

logger = logging.getLogger("supplyiq.kpi")

ALL_CALCULATORS = [
    InventoryTurnoverCalculator,
    DeadStockCalculator,
    StockoutPredictionCalculator,
    SupplierReliabilityCalculator,
    WarehouseUtilizationCalculator,
    RevenueAnalyticsCalculator,
    CostAnalyticsCalculator,
    ProfitAnalysisCalculator,
    OrderFulfillmentRateCalculator,
    MonthlyGrowthCalculator,
    DemandTrendsCalculator,
    PurchaseTrendsCalculator,
    LeadTimeAnalysisCalculator,
    InventoryAgingCalculator,
    BusinessHealthScoreCalculator,
    SupplyChainEfficiencyCalculator,
]


class KpiEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_all(self, snapshot_date: date = None) -> int:
        """Run all calculators and persist snapshots. Returns count of snapshots created."""
        if snapshot_date is None:
            snapshot_date = date.today()

        total = 0
        for CalculatorClass in ALL_CALCULATORS:
            calculator = CalculatorClass(self.db)
            try:
                snapshots = await calculator.calculate(snapshot_date)
                for snap in snapshots:
                    self.db.add(snap)
                total += len(snapshots)
                logger.info(f"KPI '{calculator.kpi_code}': {len(snapshots)} snapshots computed")
            except Exception as e:
                logger.error(f"KPI '{calculator.kpi_code}' failed: {e}")

        await self.db.flush()
        return total

    async def run_one(self, kpi_code: str, snapshot_date: date = None) -> int:
        if snapshot_date is None:
            snapshot_date = date.today()
        for CalculatorClass in ALL_CALCULATORS:
            if CalculatorClass.kpi_code == kpi_code:
                calc = CalculatorClass(self.db)
                snapshots = await calc.calculate(snapshot_date)
                for snap in snapshots:
                    self.db.add(snap)
                await self.db.flush()
                return len(snapshots)
        return 0
