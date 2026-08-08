import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Adds created_at and updated_at to any model."""
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class UUIDMixin:
    """Adds a UUID primary key."""
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
