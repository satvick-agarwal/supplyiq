"""
KPI Calculator Base
===================
All calculators implement this interface.
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.kpi_snapshot import KpiSnapshot


class KpiCalculator(ABC):
    """Base for all KPI calculators."""

    kpi_code: str
    description: str

    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def calculate(self, snapshot_date: date) -> List[KpiSnapshot]:
        """Compute and return KpiSnapshot objects (not yet persisted)."""
        ...
