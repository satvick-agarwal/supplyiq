# Permission codes matching the Permissions Matrix (Section 25 of PRD)

# Products
PRODUCT_READ = "product:read"
PRODUCT_WRITE = "product:write"
PRODUCT_DELETE = "product:delete"

# Categories
CATEGORY_READ = "category:read"
CATEGORY_WRITE = "category:write"
CATEGORY_DELETE = "category:delete"

# Suppliers
SUPPLIER_READ = "supplier:read"
SUPPLIER_WRITE = "supplier:write"
SUPPLIER_DELETE = "supplier:delete"

# Warehouses
WAREHOUSE_READ = "warehouse:read"
WAREHOUSE_WRITE = "warehouse:write"
WAREHOUSE_DELETE = "warehouse:delete"

# Inventory
INVENTORY_READ = "inventory:read"
INVENTORY_WRITE = "inventory:write"  # adjust stock

# Inventory Movements
MOVEMENT_READ = "movement:read"
MOVEMENT_WRITE = "movement:write"  # transfer

# Purchase Orders
PO_READ = "po:read"
PO_WRITE = "po:write"
PO_APPROVE = "po:approve"
PO_DELETE = "po:delete"

# Sales Orders
SO_READ = "so:read"
SO_WRITE = "so:write"
SO_DELETE = "so:delete"

# Shipments
SHIPMENT_READ = "shipment:read"
SHIPMENT_WRITE = "shipment:write"
SHIPMENT_DELETE = "shipment:delete"

# Customers
CUSTOMER_READ = "customer:read"
CUSTOMER_WRITE = "customer:write"
CUSTOMER_DELETE = "customer:delete"

# Dashboard
DASHBOARD_FINANCIAL = "dashboard:financial"
DASHBOARD_OPERATIONAL = "dashboard:operational"

# KPI
KPI_READ = "kpi:read"
KPI_RECOMPUTE = "kpi:recompute"

# Alerts & Notifications
ALERT_READ = "alert:read"
ALERT_WRITE = "alert:write"

# AI Insights
AI_INSIGHT_READ = "ai_insight:read"
AI_INSIGHT_GENERATE = "ai_insight:generate"

# Reports
REPORT_READ = "report:read"
REPORT_WRITE = "report:write"
REPORT_DELETE = "report:delete"

# User Management (Admin only)
USER_READ = "user:read"
USER_WRITE = "user:write"
USER_DELETE = "user:delete"

# Audit Logs (Admin only)
AUDIT_LOG_READ = "audit_log:read"

# ── Role → Permission Mapping ──────────────────────────────────────────────────

ADMIN_PERMISSIONS = [
    PRODUCT_READ, PRODUCT_WRITE, PRODUCT_DELETE,
    CATEGORY_READ, CATEGORY_WRITE, CATEGORY_DELETE,
    SUPPLIER_READ, SUPPLIER_WRITE, SUPPLIER_DELETE,
    WAREHOUSE_READ, WAREHOUSE_WRITE, WAREHOUSE_DELETE,
    INVENTORY_READ, INVENTORY_WRITE,
    MOVEMENT_READ, MOVEMENT_WRITE,
    PO_READ, PO_WRITE, PO_APPROVE, PO_DELETE,
    SO_READ, SO_WRITE, SO_DELETE,
    SHIPMENT_READ, SHIPMENT_WRITE, SHIPMENT_DELETE,
    CUSTOMER_READ, CUSTOMER_WRITE, CUSTOMER_DELETE,
    DASHBOARD_FINANCIAL, DASHBOARD_OPERATIONAL,
    KPI_READ, KPI_RECOMPUTE,
    ALERT_READ, ALERT_WRITE,
    AI_INSIGHT_READ, AI_INSIGHT_GENERATE,
    REPORT_READ, REPORT_WRITE, REPORT_DELETE,
    USER_READ, USER_WRITE, USER_DELETE,
    AUDIT_LOG_READ,
]

MANAGER_PERMISSIONS = [
    PRODUCT_READ, PRODUCT_WRITE, PRODUCT_DELETE,
    CATEGORY_READ, CATEGORY_WRITE, CATEGORY_DELETE,
    SUPPLIER_READ, SUPPLIER_WRITE, SUPPLIER_DELETE,
    WAREHOUSE_READ, WAREHOUSE_WRITE,
    INVENTORY_READ, INVENTORY_WRITE,
    MOVEMENT_READ, MOVEMENT_WRITE,
    PO_READ, PO_WRITE, PO_APPROVE,
    SO_READ, SO_WRITE,
    SHIPMENT_READ, SHIPMENT_WRITE,
    CUSTOMER_READ, CUSTOMER_WRITE, CUSTOMER_DELETE,
    DASHBOARD_FINANCIAL, DASHBOARD_OPERATIONAL,
    KPI_READ,
    ALERT_READ, ALERT_WRITE,
    AI_INSIGHT_READ,
    REPORT_READ, REPORT_WRITE,
]

EMPLOYEE_PERMISSIONS = [
    PRODUCT_READ,
    CATEGORY_READ,
    SUPPLIER_READ,
    WAREHOUSE_READ,
    INVENTORY_READ, INVENTORY_WRITE,
    MOVEMENT_READ,
    PO_READ,
    SO_READ, SO_WRITE,
    SHIPMENT_READ, SHIPMENT_WRITE,
    CUSTOMER_READ,
    DASHBOARD_OPERATIONAL,
    KPI_READ,
    ALERT_READ,
    AI_INSIGHT_READ,
    REPORT_READ,
]
