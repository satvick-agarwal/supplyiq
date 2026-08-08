from pydantic import BaseModel
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
import enum


# ── Pagination ─────────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int


# ── Category Schemas ───────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[UUID] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None


class CategoryOut(BaseModel):
    id: UUID
    name: str
    parent_id: Optional[UUID] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class CategoryTree(CategoryOut):
    children: List["CategoryTree"] = []


# ── Product Schemas ────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    unit_of_measure: str = "unit"
    unit_cost: Decimal = Decimal("0")
    unit_price: Decimal = Decimal("0")
    reorder_point: Decimal = Decimal("0")
    reorder_quantity: Decimal = Decimal("0")
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    unit_of_measure: Optional[str] = None
    unit_cost: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    reorder_point: Optional[Decimal] = None
    reorder_quantity: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ProductOut(BaseModel):
    id: UUID
    sku: str
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    unit_of_measure: str
    unit_cost: Decimal
    unit_price: Decimal
    reorder_point: Decimal
    reorder_quantity: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Supplier Schemas ───────────────────────────────────────────────────────────

class SupplierCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    average_lead_time_days: Optional[int] = None
    is_active: bool = True


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    average_lead_time_days: Optional[int] = None
    is_active: Optional[bool] = None


class SupplierOut(BaseModel):
    id: UUID
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    address: Optional[str] = None
    payment_terms: Optional[str] = None
    average_lead_time_days: Optional[int] = None
    reliability_score: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Warehouse Schemas ──────────────────────────────────────────────────────────

class WarehouseCreate(BaseModel):
    name: str
    address: Optional[str] = None
    capacity_units: Optional[Decimal] = None
    manager_id: Optional[UUID] = None


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    capacity_units: Optional[Decimal] = None
    manager_id: Optional[UUID] = None


class WarehouseOut(BaseModel):
    id: UUID
    name: str
    address: Optional[str] = None
    capacity_units: Optional[Decimal] = None
    manager_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Inventory Schemas ──────────────────────────────────────────────────────────

class InventoryItemOut(BaseModel):
    id: UUID
    product_id: UUID
    warehouse_id: UUID
    quantity_on_hand: Decimal
    quantity_reserved: Decimal
    safety_stock: Decimal
    product: Optional[ProductOut] = None
    model_config = {"from_attributes": True}


class StockAdjustRequest(BaseModel):
    product_id: UUID
    warehouse_id: UUID
    quantity: Decimal  # positive = add, negative = remove
    reason: Optional[str] = None


class TransferRequest(BaseModel):
    product_id: UUID
    from_warehouse_id: UUID
    to_warehouse_id: UUID
    quantity: Decimal
    reason: Optional[str] = None


# ── Inventory Movement Schemas ─────────────────────────────────────────────────

class MovementOut(BaseModel):
    id: UUID
    inventory_item_id: UUID
    movement_type: str
    quantity: Decimal
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    reason: Optional[str] = None
    created_by: Optional[UUID] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── Customer Schemas ───────────────────────────────────────────────────────────

class CustomerCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    customer_type: str = "retail"


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    customer_type: Optional[str] = None


class CustomerOut(BaseModel):
    id: UUID
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    customer_type: str
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Purchase Order Schemas ─────────────────────────────────────────────────────

class POItemCreate(BaseModel):
    product_id: UUID
    quantity_ordered: Decimal
    unit_cost: Decimal


class POItemOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity_ordered: Decimal
    quantity_received: Decimal
    unit_cost: Decimal
    product: Optional[ProductOut] = None
    model_config = {"from_attributes": True}


class POCreate(BaseModel):
    supplier_id: UUID
    warehouse_id: UUID
    order_date: Optional[date] = None
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[POItemCreate]


class POUpdate(BaseModel):
    expected_date: Optional[date] = None
    notes: Optional[str] = None


class POReceiveItem(BaseModel):
    product_id: UUID
    quantity_received: Decimal


class POReceiveRequest(BaseModel):
    items: List[POReceiveItem]


class POOut(BaseModel):
    id: UUID
    supplier_id: UUID
    warehouse_id: UUID
    status: str
    order_date: Optional[date] = None
    expected_date: Optional[date] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    items: List[POItemOut] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Sales Order Schemas ────────────────────────────────────────────────────────

class SOItemCreate(BaseModel):
    product_id: UUID
    quantity_ordered: Decimal
    unit_price: Decimal


class SOItemOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity_ordered: Decimal
    quantity_fulfilled: Decimal
    unit_price: Decimal
    product: Optional[ProductOut] = None
    model_config = {"from_attributes": True}


class SOCreate(BaseModel):
    customer_id: UUID
    warehouse_id: UUID
    order_date: Optional[date] = None
    notes: Optional[str] = None
    items: List[SOItemCreate]


class SOUpdate(BaseModel):
    notes: Optional[str] = None


class SOOut(BaseModel):
    id: UUID
    customer_id: UUID
    warehouse_id: UUID
    status: str
    order_date: Optional[date] = None
    notes: Optional[str] = None
    created_by: Optional[UUID] = None
    items: List[SOItemOut] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Shipment Schemas ───────────────────────────────────────────────────────────

class ShipmentCreate(BaseModel):
    shipment_type: str
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    expected_date: Optional[date] = None
    notes: Optional[str] = None


class ShipmentStatusUpdate(BaseModel):
    status: str
    notes: Optional[str] = None


class ShipmentOut(BaseModel):
    id: UUID
    shipment_type: str
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    status: str
    expected_date: Optional[date] = None
    delivered_at: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


# ── Alert Schemas ──────────────────────────────────────────────────────────────

class AlertUpdate(BaseModel):
    status: str


class AlertOut(BaseModel):
    id: UUID
    alert_type: str
    severity: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    message: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ── Notification Schemas ───────────────────────────────────────────────────────

class NotificationOut(BaseModel):
    id: UUID
    title: str
    body: Optional[str] = None
    is_read: bool
    alert_id: Optional[UUID] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── AI Insight Schemas ─────────────────────────────────────────────────────────

class AiInsightOut(BaseModel):
    id: UUID
    category: str
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    insight_text: str
    confidence_score: Optional[Decimal] = None
    severity: str
    generated_at: datetime
    model_version: Optional[str] = None
    model_config = {"from_attributes": True}


# ── KPI Schemas ────────────────────────────────────────────────────────────────

class KpiSnapshotOut(BaseModel):
    id: UUID
    kpi_code: str
    scope_type: str
    scope_id: Optional[UUID] = None
    value: Optional[Decimal] = None
    metadata_: Optional[dict] = None
    snapshot_date: date
    model_config = {"from_attributes": True}
