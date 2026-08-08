from sqlalchemy import Column, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class InventoryItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "inventory_items"
    __table_args__ = (UniqueConstraint("product_id", "warehouse_id", name="uq_inventory_item"),)

    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=False, index=True)
    # CRITICAL: quantity_on_hand is NEVER written directly by API.
    # It is only updated as a side effect of inventory_movements inserts within the same transaction.
    quantity_on_hand = Column(Numeric(14, 3), nullable=False, default=0)
    quantity_reserved = Column(Numeric(14, 3), nullable=False, default=0)
    safety_stock = Column(Numeric(14, 3), nullable=False, default=0)

    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    movements = relationship("InventoryMovement", back_populates="inventory_item")
