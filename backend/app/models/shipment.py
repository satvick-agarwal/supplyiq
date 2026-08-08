import enum
from sqlalchemy import Column, ForeignKey, String, Enum, Date, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class ShipmentType(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class ShipmentReferenceType(str, enum.Enum):
    PO = "PO"
    SO = "SO"


class ShipmentStatus(str, enum.Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class Shipment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "shipments"

    shipment_type = Column(Enum(ShipmentType), nullable=False)
    reference_type = Column(Enum(ShipmentReferenceType), nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # PO or SO id
    carrier = Column(String(255), nullable=True)
    tracking_number = Column(String(255), nullable=True)
    origin = Column(Text, nullable=True)
    destination = Column(Text, nullable=True)
    status = Column(Enum(ShipmentStatus), nullable=False, default=ShipmentStatus.PENDING)
    expected_date = Column(Date, nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
