import enum
from sqlalchemy import Column, String, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base, UUIDMixin


class AlertSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, enum.Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert(UUIDMixin, Base):
    __tablename__ = "alerts"

    alert_type = Column(String(100), nullable=False)  # e.g. "low_stock", "warehouse_capacity"
    severity = Column(Enum(AlertSeverity), nullable=False)
    entity_type = Column(String(100), nullable=True)  # e.g. "product", "warehouse"
    entity_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    message = Column(Text, nullable=False)
    status = Column(Enum(AlertStatus), nullable=False, default=AlertStatus.OPEN)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    notifications = relationship("Notification", back_populates="alert")
