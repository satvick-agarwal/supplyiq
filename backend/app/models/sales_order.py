import enum
from sqlalchemy import Column, ForeignKey, Numeric, String, Enum, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class SOStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    FULFILLED = "fulfilled"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class SalesOrder(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sales_orders"

    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False, index=True)
    status = Column(Enum(SOStatus), nullable=False, default=SOStatus.DRAFT)
    order_date = Column(Date, nullable=True)
    notes = Column(String(1000), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="sales_orders")
    warehouse = relationship("Warehouse", back_populates="sales_orders")
    items = relationship("SalesOrderItem", back_populates="sales_order", cascade="all, delete-orphan")
    created_by_user = relationship("User", foreign_keys=[created_by])


class SalesOrderItem(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sales_order_items"

    sales_order_id = Column(UUID(as_uuid=True), ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity_ordered = Column(Numeric(14, 3), nullable=False)
    quantity_fulfilled = Column(Numeric(14, 3), nullable=False, default=0)
    unit_price = Column(Numeric(14, 2), nullable=False)

    # Relationships
    sales_order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product", back_populates="sales_order_items")
