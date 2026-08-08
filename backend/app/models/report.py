import enum
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base, UUIDMixin


class ReportFormat(str, enum.Enum):
    CSV = "csv"
    XLSX = "xlsx"
    PDF = "pdf"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class Report(UUIDMixin, Base):
    __tablename__ = "reports"

    report_type = Column(String(100), nullable=False)
    format = Column(Enum(ReportFormat), nullable=False)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    file_path = Column(String(500), nullable=True)
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    requested_by_user = relationship("User", back_populates="reports")
