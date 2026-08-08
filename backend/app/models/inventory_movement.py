import enum
from sqlalchemy import Column, ForeignKey, Numeric, String, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.base import Base, UUIDMixin


class MovementType(str, enum.Enum):
    IN = "IN"
    OUT = "OUT"
    TRANSFER = "TRANSFER"
    ADJUSTMENT = "ADJUSTMENT"


class ReferenceType(str, enum.Enum):
    PO = "PO"
    SO = "SO"
    SHIPMENT = "SHIPMENT"
    MANUAL = "MANUAL"


class InventoryMovement(UUIDMixin, Base):
    """Append-only ledger of every stock change. Never updated or deleted."""
    __tablename__ = "inventory_movements"

    inventory_item_id = Column(UUID(as_uuid=True), ForeignKey("inventory_items.id", ondelete="CASCADE"), nullable=False, index=True)
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Numeric(14, 3), nullable=False)  # always positive; direction determined by type
    reference_type = Column(Enum(ReferenceType), nullable=True)
    reference_id = Column(UUID(as_uuid=True), nullable=True)  # PO/SO/Shipment ID
    reason = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    # NO updated_at — this is append-only

    # Relationships
    inventory_item = relationship("InventoryItem", back_populates="movements")
    created_by_user = relationship("User", foreign_keys=[created_by])
