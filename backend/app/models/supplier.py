from sqlalchemy import Column, String, Text, Boolean, Numeric, Integer
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin
from app.models.product import product_suppliers


class Supplier(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "suppliers"

    name = Column(String(255), nullable=False, index=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    payment_terms = Column(String(100), nullable=True)  # e.g. "NET30"
    average_lead_time_days = Column(Integer, nullable=True)
    reliability_score = Column(Numeric(5, 2), nullable=True)  # cached, 0-100
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    products = relationship("Product", secondary=product_suppliers, back_populates="suppliers")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
