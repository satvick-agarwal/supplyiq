import enum
from sqlalchemy import Column, ForeignKey, Numeric, String, Enum, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class POStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SENT = "sent"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class PurchaseOrder(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "purchase_orders"

    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(Enum(POStatus), nullable=False, default=POStatus.DRAFT)
    order_date = Column(Date, nullable=True)
    expected_date = Column(Date, nullable=True)
    notes = Column(String(1000), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    warehouse = relationship("Warehouse", back_populates="purchase_orders")
    items = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])
    shipments = relationship("Shipment", primaryjoin="and_(Shipment.reference_type=='PO', foreign(Shipment.reference_id)==PurchaseOrder.id)", viewonly=True)


class PurchaseOrderItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "purchase_order_items"

    purchase_order_id = Column(UUID(as_uuid=True), ForeignKey("purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity_ordered = Column(Numeric(14, 3), nullable=False)
    quantity_received = Column(Numeric(14, 3), nullable=False, default=0)
    unit_cost = Column(Numeric(14, 2), nullable=False)

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="items")
    product = relationship("Product", back_populates="purchase_order_items")
