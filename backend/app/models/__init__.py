# Import all models to ensure they are registered with SQLAlchemy's metadata
# This file must be imported before any Alembic migration or DB init

from app.db.base import Base  # noqa: F401
from app.models.role import Role, Permission, role_permissions  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.product import Product, product_suppliers  # noqa: F401
from app.models.supplier import Supplier  # noqa: F401
from app.models.warehouse import Warehouse  # noqa: F401
from app.models.inventory_item import InventoryItem  # noqa: F401
from app.models.inventory_movement import InventoryMovement  # noqa: F401
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem  # noqa: F401
from app.models.customer import Customer  # noqa: F401
from app.models.sales_order import SalesOrder, SalesOrderItem  # noqa: F401
from app.models.shipment import Shipment  # noqa: F401
from app.models.kpi_snapshot import KpiSnapshot  # noqa: F401
from app.models.alert import Alert  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.ai_insight import AiInsight  # noqa: F401
from app.models.report import Report  # noqa: F401
from app.models.audit_log import AuditLog  # noqa: F401
