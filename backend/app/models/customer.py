import enum
from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin


class CustomerType(str, enum.Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"


class Customer(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customers"

    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    customer_type = Column(Enum(CustomerType), nullable=False, default=CustomerType.RETAIL)

    # Relationships
    sales_orders = relationship("SalesOrder", back_populates="customer")
