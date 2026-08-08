import enum
from sqlalchemy import Column, String, Enum, Numeric, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin


class KpiScope(str, enum.Enum):
    GLOBAL = "GLOBAL"
    WAREHOUSE = "WAREHOUSE"
    CATEGORY = "CATEGORY"
    SUPPLIER = "SUPPLIER"
    PRODUCT = "PRODUCT"


class KpiSnapshot(UUIDMixin, Base):
    """Versioned KPI snapshots. One row per (kpi_code, scope_type, scope_id, snapshot_date)."""
    __tablename__ = "kpi_snapshots"

    kpi_code = Column(String(100), nullable=False, index=True)  # e.g. "inventory_turnover"
    scope_type = Column(Enum(KpiScope), nullable=False, default=KpiScope.GLOBAL)
    scope_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # warehouse/category/supplier/product id
    value = Column(Numeric(20, 4), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)  # additional context
    snapshot_date = Column(Date, nullable=False, index=True)
