from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base, UUIDMixin, TimestampMixin

# Association table for Role ↔ Permission (M:N)
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Role(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "roles"

    name = Column(String(50), unique=True, nullable=False)  # Admin | Manager | Employee
    description = Column(Text, nullable=True)

    # Relationships
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles", lazy="selectin")
    users = relationship("User", back_populates="role")


class Permission(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "permissions"

    code = Column(String(100), unique=True, nullable=False)  # e.g. "inventory:write"
    description = Column(Text, nullable=True)

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
