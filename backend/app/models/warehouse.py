from sqlalchemy import Column, String, Text, ForeignKey, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class Warehouse(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "warehouses"

    name = Column(String(255), nullable=False, index=True)
    address = Column(Text, nullable=True)
    capacity_units = Column(Numeric(14, 3), nullable=True)  # max stock units
    manager_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    manager = relationship("User", foreign_keys=[manager_id])
    inventory_items = relationship("InventoryItem", back_populates="warehouse")
    purchase_orders = relationship("PurchaseOrder", back_populates="warehouse")
    sales_orders = relationship("SalesOrder", back_populates="warehouse")
