import enum
from sqlalchemy import Column, String, Text, Enum, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from app.db.base import Base, UUIDMixin


class InsightCategory(str, enum.Enum):
    INVENTORY = "inventory"
    SUPPLIER = "supplier"
    WAREHOUSE = "warehouse"
    SALES = "sales"
    FINANCIAL = "financial"


class InsightSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AiInsight(UUIDMixin, Base):
    __tablename__ = "ai_insights"

    category = Column(Enum(InsightCategory), nullable=False, index=True)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    insight_text = Column(Text, nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=True)  # 0.0 - 1.0
    severity = Column(Enum(InsightSeverity), nullable=False, default=InsightSeverity.INFO)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    model_version = Column(String(50), nullable=True, default="template-v1")
