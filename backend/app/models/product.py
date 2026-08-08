from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Numeric, Table, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin

# Association table for Product ↔ Supplier (M:N)
product_suppliers = Table(
    "product_suppliers",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
    Column("supplier_id", UUID(as_uuid=True), ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False),
    Column("supplier_sku", String(100), nullable=True),
    Column("unit_cost", Numeric(14, 2), nullable=True),
    Column("is_preferred", Boolean, default=False),
    UniqueConstraint("product_id", "supplier_id", name="uq_product_supplier"),
)


class Product(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "products"

    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    unit_of_measure = Column(String(50), nullable=False, default="unit")  # unit, kg, liter, etc.
    unit_cost = Column(Numeric(14, 2), nullable=False, default=0)
    unit_price = Column(Numeric(14, 2), nullable=False, default=0)
    reorder_point = Column(Numeric(14, 3), nullable=False, default=0)
    reorder_quantity = Column(Numeric(14, 3), nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="products")
    suppliers = relationship("Supplier", secondary=product_suppliers, back_populates="products")
    inventory_items = relationship("InventoryItem", back_populates="product")
    purchase_order_items = relationship("PurchaseOrderItem", back_populates="product")
    sales_order_items = relationship("SalesOrderItem", back_populates="product")
