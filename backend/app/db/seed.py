"""
SupplyIQ Seed Data Script
=========================
Creates realistic demo data for all entities:
- Roles, permissions, users
- Categories (hierarchical), products, suppliers
- Warehouses with inventory
- Purchase orders (various stages)
- Sales orders (various stages)
- Shipments
- KPI snapshots (30 days history)
- Alerts and AI insights

Run: python -m app.db.seed
"""
import asyncio
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.base import Base
from app.models.role import Role, Permission, role_permissions
from app.models.user import User
from app.models.category import Category
from app.models.product import Product, product_suppliers
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse
from app.models.inventory_item import InventoryItem
from app.models.inventory_movement import InventoryMovement, MovementType, ReferenceType
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, POStatus
from app.models.customer import Customer, CustomerType
from app.models.sales_order import SalesOrder, SalesOrderItem, SOStatus
from app.models.shipment import Shipment, ShipmentType, ShipmentReferenceType, ShipmentStatus
from app.models.kpi_snapshot import KpiSnapshot, KpiScope
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.notification import Notification
from app.models.ai_insight import AiInsight, InsightCategory, InsightSeverity
from app.core.security import hash_password
from app.core.permissions import ADMIN_PERMISSIONS, MANAGER_PERMISSIONS, EMPLOYEE_PERMISSIONS


async def seed(db: AsyncSession):
    print("[+] Starting seed...")

    # ── 1. Permissions ─────────────────────────────────────────────────────────
    print("   Creating permissions...")
    all_perm_codes = list(set(ADMIN_PERMISSIONS + MANAGER_PERMISSIONS + EMPLOYEE_PERMISSIONS))
    perm_objects = {}
    for code in all_perm_codes:
        p = Permission(id=uuid.uuid4(), code=code, description=f"Permission: {code}")
        db.add(p)
        perm_objects[code] = p
    await db.flush()

    # ── 2. Roles ───────────────────────────────────────────────────────────────
    print("   Creating roles...")
    admin_role = Role(id=uuid.uuid4(), name="Admin", description="Full system access")
    manager_role = Role(id=uuid.uuid4(), name="Manager", description="Operational management access")
    employee_role = Role(id=uuid.uuid4(), name="Employee", description="Day-to-day operational access")
    db.add_all([admin_role, manager_role, employee_role])
    await db.flush()

    # Assign permissions to roles
    for code in ADMIN_PERMISSIONS:
        await db.execute(role_permissions.insert().values(role_id=admin_role.id, permission_id=perm_objects[code].id))
    for code in MANAGER_PERMISSIONS:
        await db.execute(role_permissions.insert().values(role_id=manager_role.id, permission_id=perm_objects[code].id))
    for code in EMPLOYEE_PERMISSIONS:
        await db.execute(role_permissions.insert().values(role_id=employee_role.id, permission_id=perm_objects[code].id))
    await db.flush()

    # ── 3. Users ───────────────────────────────────────────────────────────────
    print("   Creating users...")
    admin = User(id=uuid.uuid4(), email="admin@supplyiq.com", password_hash=hash_password("Admin@123"), full_name="Alex Administrator", role_id=admin_role.id, is_active=True)
    manager = User(id=uuid.uuid4(), email="manager@supplyiq.com", password_hash=hash_password("Manager@123"), full_name="Marcus Manager", role_id=manager_role.id, is_active=True)
    sc_manager = User(id=uuid.uuid4(), email="scm@supplyiq.com", password_hash=hash_password("Manager@123"), full_name="Sarah Supply Chain", role_id=manager_role.id, is_active=True)
    employee1 = User(id=uuid.uuid4(), email="warehouse@supplyiq.com", password_hash=hash_password("Emp@12345"), full_name="Will Warehouse", role_id=employee_role.id, is_active=True)
    employee2 = User(id=uuid.uuid4(), email="ops@supplyiq.com", password_hash=hash_password("Emp@12345"), full_name="Olivia Ops", role_id=employee_role.id, is_active=True)
    db.add_all([admin, manager, sc_manager, employee1, employee2])
    await db.flush()

    # ── 4. Categories (hierarchical) ───────────────────────────────────────────
    print("   Creating categories...")
    electronics = Category(id=uuid.uuid4(), name="Electronics")
    db.add(electronics)
    await db.flush()
    components = Category(id=uuid.uuid4(), name="Components", parent_id=electronics.id)
    accessories = Category(id=uuid.uuid4(), name="Accessories", parent_id=electronics.id)
    db.add_all([components, accessories])
    industrial = Category(id=uuid.uuid4(), name="Industrial")
    db.add(industrial)
    await db.flush()
    fasteners = Category(id=uuid.uuid4(), name="Fasteners", parent_id=industrial.id)
    tools = Category(id=uuid.uuid4(), name="Tools", parent_id=industrial.id)
    db.add_all([fasteners, tools])
    consumables = Category(id=uuid.uuid4(), name="Consumables")
    office = Category(id=uuid.uuid4(), name="Office Supplies")
    db.add_all([consumables, office])
    await db.flush()

    # ── 5. Suppliers ───────────────────────────────────────────────────────────
    print("   Creating suppliers...")
    sup1 = Supplier(id=uuid.uuid4(), name="Acme Components Ltd", contact_email="orders@acme.com", contact_phone="+1-555-0101", payment_terms="NET30", average_lead_time_days=10, reliability_score=Decimal("88.5"), is_active=True)
    sup2 = Supplier(id=uuid.uuid4(), name="TechCore Supply", contact_email="supply@techcore.io", contact_phone="+1-555-0202", payment_terms="NET45", average_lead_time_days=14, reliability_score=Decimal("72.0"), is_active=True)
    sup3 = Supplier(id=uuid.uuid4(), name="Industrial Masters", contact_email="b2b@indmasters.com", contact_phone="+1-555-0303", payment_terms="NET30", average_lead_time_days=7, reliability_score=Decimal("94.0"), is_active=True)
    sup4 = Supplier(id=uuid.uuid4(), name="Global Parts Inc", contact_email="sales@globalparts.com", contact_phone="+1-555-0404", payment_terms="NET60", average_lead_time_days=21, reliability_score=Decimal("61.5"), is_active=True)
    sup5 = Supplier(id=uuid.uuid4(), name="QuickShip Wholesale", contact_email="orders@quickship.com", contact_phone="+1-555-0505", payment_terms="COD", average_lead_time_days=3, reliability_score=Decimal("91.0"), is_active=True)
    sup6 = Supplier(id=uuid.uuid4(), name="Precision Parts Co", contact_email="info@precisionparts.com", contact_phone="+1-555-0606", payment_terms="NET30", average_lead_time_days=12, reliability_score=Decimal("83.0"), is_active=True)
    db.add_all([sup1, sup2, sup3, sup4, sup5, sup6])
    await db.flush()

    # ── 6. Products ────────────────────────────────────────────────────────────
    print("   Creating products...")
    products_data = [
        {"sku": "MICRO-328P", "name": "ATmega328P Microcontroller", "category_id": components.id, "unit_cost": Decimal("2.50"), "unit_price": Decimal("6.99"), "reorder_point": Decimal("500"), "reorder_quantity": Decimal("2000")},
        {"sku": "CAP-100UF", "name": "Capacitor 100µF Electrolytic", "category_id": components.id, "unit_cost": Decimal("0.08"), "unit_price": Decimal("0.35"), "reorder_point": Decimal("2000"), "reorder_quantity": Decimal("10000")},
        {"sku": "RES-10K", "name": "Resistor 10KΩ 1/4W", "category_id": components.id, "unit_cost": Decimal("0.02"), "unit_price": Decimal("0.10"), "reorder_point": Decimal("5000"), "reorder_quantity": Decimal("20000")},
        {"sku": "LED-5MM-RED", "name": "LED 5mm Red", "category_id": components.id, "unit_cost": Decimal("0.05"), "unit_price": Decimal("0.25"), "reorder_point": Decimal("1000"), "reorder_quantity": Decimal("5000")},
        {"sku": "USB-C-CABLE-1M", "name": "USB-C Cable 1m Premium", "category_id": accessories.id, "unit_cost": Decimal("3.20"), "unit_price": Decimal("12.99"), "reorder_point": Decimal("100"), "reorder_quantity": Decimal("500")},
        {"sku": "HDMI-2M", "name": "HDMI Cable 2m 4K", "category_id": accessories.id, "unit_cost": Decimal("4.50"), "unit_price": Decimal("19.99"), "reorder_point": Decimal("50"), "reorder_quantity": Decimal("200")},
        {"sku": "BOLT-M6x20", "name": "Bolt M6x20mm Stainless", "category_id": fasteners.id, "unit_of_measure": "pack", "unit_cost": Decimal("1.20"), "unit_price": Decimal("4.50"), "reorder_point": Decimal("200"), "reorder_quantity": Decimal("1000")},
        {"sku": "NUT-M6", "name": "Hex Nut M6 Stainless", "category_id": fasteners.id, "unit_of_measure": "pack", "unit_cost": Decimal("0.80"), "unit_price": Decimal("3.20"), "reorder_point": Decimal("200"), "reorder_quantity": Decimal("1000")},
        {"sku": "DRILL-10MM", "name": "HSS Drill Bit 10mm", "category_id": tools.id, "unit_cost": Decimal("2.80"), "unit_price": Decimal("8.99"), "reorder_point": Decimal("50"), "reorder_quantity": Decimal("200")},
        {"sku": "WIRE-AWG22", "name": "Hook-up Wire AWG22 Red (30m)", "category_id": components.id, "unit_cost": Decimal("3.50"), "unit_price": Decimal("9.99"), "reorder_point": Decimal("30"), "reorder_quantity": Decimal("150")},
        {"sku": "SOLDER-60-40", "name": "Solder Wire 60/40 250g", "category_id": consumables.id, "unit_cost": Decimal("5.20"), "unit_price": Decimal("14.99"), "reorder_point": Decimal("20"), "reorder_quantity": Decimal("100")},
        {"sku": "TAPE-KAPTON", "name": "Kapton Tape 20mm", "category_id": consumables.id, "unit_cost": Decimal("1.80"), "unit_price": Decimal("6.50"), "reorder_point": Decimal("50"), "reorder_quantity": Decimal("200")},
        {"sku": "RELAY-5V", "name": "5V SPDT Relay Module", "category_id": components.id, "unit_cost": Decimal("1.50"), "unit_price": Decimal("4.99"), "reorder_point": Decimal("100"), "reorder_quantity": Decimal("500")},
        {"sku": "SENSOR-DHT22", "name": "DHT22 Temp/Humidity Sensor", "category_id": components.id, "unit_cost": Decimal("3.80"), "unit_price": Decimal("9.99"), "reorder_point": Decimal("50"), "reorder_quantity": Decimal("200")},
        {"sku": "MOTOR-STEPPER", "name": "NEMA 17 Stepper Motor", "category_id": components.id, "unit_cost": Decimal("8.50"), "unit_price": Decimal("24.99"), "reorder_point": Decimal("20"), "reorder_quantity": Decimal("100")},
        {"sku": "PAPER-A4-500", "name": "A4 Paper 80gsm 500 sheets", "category_id": office.id, "unit_of_measure": "ream", "unit_cost": Decimal("3.20"), "unit_price": Decimal("7.99"), "reorder_point": Decimal("30"), "reorder_quantity": Decimal("100")},
        {"sku": "BATTERY-AA-8PK", "name": "AA Alkaline Battery 8-pack", "category_id": consumables.id, "unit_cost": Decimal("2.10"), "unit_price": Decimal("7.50"), "reorder_point": Decimal("50"), "reorder_quantity": Decimal("200")},
        {"sku": "RASPBERRY-PI-4B", "name": "Raspberry Pi 4 Model B 4GB", "category_id": components.id, "unit_cost": Decimal("45.00"), "unit_price": Decimal("89.99"), "reorder_point": Decimal("10"), "reorder_quantity": Decimal("50")},
        {"sku": "POWER-SUPPLY-5V", "name": "5V 3A Power Supply Unit", "category_id": accessories.id, "unit_cost": Decimal("6.50"), "unit_price": Decimal("18.99"), "reorder_point": Decimal("25"), "reorder_quantity": Decimal("100")},
        {"sku": "BREADBOARD-830", "name": "Solderless Breadboard 830 Points", "category_id": accessories.id, "unit_cost": Decimal("2.80"), "unit_price": Decimal("8.99"), "reorder_point": Decimal("30"), "reorder_quantity": Decimal("150")},
        {"sku": "WASHER-M6", "name": "Flat Washer M6 Stainless", "category_id": fasteners.id, "unit_of_measure": "pack", "unit_cost": Decimal("0.60"), "unit_price": Decimal("2.50"), "reorder_point": Decimal("300"), "reorder_quantity": Decimal("1500")},
        {"sku": "DISPLAY-LCD-16x2", "name": "16x2 Character LCD Display", "category_id": components.id, "unit_cost": Decimal("4.20"), "unit_price": Decimal("12.99"), "reorder_point": Decimal("20"), "reorder_quantity": Decimal("100")},
        {"sku": "TRANSISTOR-NPN", "name": "NPN Transistor 2N2222 (10-pack)", "category_id": components.id, "unit_cost": Decimal("0.15"), "unit_price": Decimal("0.99"), "reorder_point": Decimal("1000"), "reorder_quantity": Decimal("5000")},
        {"sku": "WIFI-MODULE-ESP8266", "name": "ESP8266 WiFi Module", "category_id": components.id, "unit_cost": Decimal("2.20"), "unit_price": Decimal("6.99"), "reorder_point": Decimal("50"), "reorder_quantity": Decimal("250")},
        {"sku": "HEAT-SHRINK-ASST", "name": "Heat Shrink Tubing Assortment", "category_id": consumables.id, "unit_cost": Decimal("3.50"), "unit_price": Decimal("9.99"), "reorder_point": Decimal("20"), "reorder_quantity": Decimal("100")},
    ]

    product_objs = []
    for pd in products_data:
        prod = Product(
            id=uuid.uuid4(),
            sku=pd["sku"], name=pd["name"],
            category_id=pd["category_id"],
            unit_of_measure=pd.get("unit_of_measure", "unit"),
            unit_cost=pd["unit_cost"], unit_price=pd["unit_price"],
            reorder_point=pd["reorder_point"], reorder_quantity=pd["reorder_quantity"],
            is_active=True,
        )
        db.add(prod)
        product_objs.append(prod)
    await db.flush()

    # ── 7. Warehouses ──────────────────────────────────────────────────────────
    print("   Creating warehouses...")
    wh_east = Warehouse(id=uuid.uuid4(), name="East Distribution Center", address="123 Industrial Blvd, Newark, NJ 07101", capacity_units=Decimal("50000"), manager_id=employee1.id)
    wh_west = Warehouse(id=uuid.uuid4(), name="West Distribution Center", address="456 Logistics Ave, Los Angeles, CA 90001", capacity_units=Decimal("75000"), manager_id=employee2.id)
    wh_central = Warehouse(id=uuid.uuid4(), name="Central Hub", address="789 Commerce Dr, Chicago, IL 60601", capacity_units=Decimal("30000"), manager_id=manager.id)
    db.add_all([wh_east, wh_west, wh_central])
    await db.flush()

    # ── 8. Inventory ───────────────────────────────────────────────────────────
    print("   Creating inventory items and movements...")
    warehouses = [wh_east, wh_west, wh_central]
    # Assign quantities - some below reorder point (to trigger alerts)
    quantities = {
        "MICRO-328P": [1200, 800, 400],
        "CAP-100UF": [8000, 5000, 2000],
        "RES-10K": [15000, 12000, 5000],
        "LED-5MM-RED": [3500, 2000, 800],
        "USB-C-CABLE-1M": [180, 90, 45],
        "HDMI-2M": [30, 20, 0],  # stockout in central
        "BOLT-M6x20": [600, 400, 150],
        "NUT-M6": [500, 350, 80],  # low in central
        "DRILL-10MM": [80, 60, 30],
        "WIRE-AWG22": [45, 25, 8],  # low stock
        "SOLDER-60-40": [35, 20, 5],  # critical low
        "TAPE-KAPTON": [80, 60, 25],
        "RELAY-5V": [200, 150, 60],
        "SENSOR-DHT22": [75, 55, 20],
        "MOTOR-STEPPER": [35, 25, 8],
        "PAPER-A4-500": [60, 45, 20],
        "BATTERY-AA-8PK": [120, 85, 35],
        "RASPBERRY-PI-4B": [25, 15, 5],
        "POWER-SUPPLY-5V": [55, 40, 15],
        "BREADBOARD-830": [70, 50, 20],
        "WASHER-M6": [900, 700, 300],
        "DISPLAY-LCD-16x2": [45, 30, 10],
        "TRANSISTOR-NPN": [3000, 2200, 800],
        "WIFI-MODULE-ESP8266": [120, 90, 35],
        "HEAT-SHRINK-ASST": [40, 28, 10],
    }

    product_by_sku = {p.sku: p for p in product_objs}
    inventory_items = {}
    now = datetime.now(timezone.utc)

    for prod in product_objs:
        qtys = quantities.get(prod.sku, [100, 80, 30])
        for i, wh in enumerate(warehouses):
            qty = Decimal(str(qtys[i]))
            inv_item = InventoryItem(
                id=uuid.uuid4(),
                product_id=prod.id, warehouse_id=wh.id,
                quantity_on_hand=qty,
                quantity_reserved=Decimal("0"),
                safety_stock=prod.reorder_point * Decimal("0.5"),
            )
            db.add(inv_item)
            inventory_items[(prod.id, wh.id)] = inv_item
    await db.flush()

    # Create historical IN movements (simulating past receipts)
    for (prod_id, wh_id), item in inventory_items.items():
        if float(item.quantity_on_hand) > 0:
            movement = InventoryMovement(
                id=uuid.uuid4(),
                inventory_item_id=item.id,
                movement_type=MovementType.IN,
                quantity=item.quantity_on_hand,
                reference_type=ReferenceType.MANUAL,
                reason="Initial stock load",
                created_by=admin.id,
                created_at=now - timedelta(days=random.randint(30, 90)),
            )
            db.add(movement)
    await db.flush()

    # ── 9. Customers ───────────────────────────────────────────────────────────
    print("   Creating customers...")
    customers = [
        Customer(id=uuid.uuid4(), name="TechBuilders Inc", email="orders@techbuilders.com", phone="+1-555-1001", address="100 Innovation Way, Austin, TX 78701", customer_type=CustomerType.WHOLESALE),
        Customer(id=uuid.uuid4(), name="Maker Space Hub", email="buy@makerspace.io", phone="+1-555-1002", address="200 Creator St, Portland, OR 97201", customer_type=CustomerType.RETAIL),
        Customer(id=uuid.uuid4(), name="Robotics World LLC", email="procurement@roboticsworld.com", phone="+1-555-1003", address="300 Automation Blvd, Detroit, MI 48201", customer_type=CustomerType.WHOLESALE),
        Customer(id=uuid.uuid4(), name="EduTech Systems", email="orders@edutech.edu", phone="+1-555-1004", address="400 Learning Lane, Boston, MA 02101", customer_type=CustomerType.WHOLESALE),
        Customer(id=uuid.uuid4(), name="DIY Projects Store", email="supply@diystore.com", phone="+1-555-1005", address="500 Hobby Dr, Denver, CO 80201", customer_type=CustomerType.RETAIL),
    ]
    db.add_all(customers)
    await db.flush()

    # ── 10. Purchase Orders ────────────────────────────────────────────────────
    print("   Creating purchase orders...")
    po1 = PurchaseOrder(id=uuid.uuid4(), supplier_id=sup1.id, warehouse_id=wh_east.id, status=POStatus.RECEIVED, order_date=date.today() - timedelta(days=15), expected_date=date.today() - timedelta(days=5), created_by=sc_manager.id)
    po2 = PurchaseOrder(id=uuid.uuid4(), supplier_id=sup2.id, warehouse_id=wh_west.id, status=POStatus.SENT, order_date=date.today() - timedelta(days=7), expected_date=date.today() + timedelta(days=7), created_by=sc_manager.id)
    po3 = PurchaseOrder(id=uuid.uuid4(), supplier_id=sup3.id, warehouse_id=wh_central.id, status=POStatus.APPROVED, order_date=date.today() - timedelta(days=2), expected_date=date.today() + timedelta(days=12), created_by=manager.id)
    po4 = PurchaseOrder(id=uuid.uuid4(), supplier_id=sup5.id, warehouse_id=wh_east.id, status=POStatus.DRAFT, order_date=date.today(), expected_date=date.today() + timedelta(days=5), created_by=sc_manager.id)
    po5 = PurchaseOrder(id=uuid.uuid4(), supplier_id=sup4.id, warehouse_id=wh_west.id, status=POStatus.PARTIALLY_RECEIVED, order_date=date.today() - timedelta(days=20), expected_date=date.today() - timedelta(days=1), created_by=sc_manager.id)
    po6 = PurchaseOrder(id=uuid.uuid4(), supplier_id=sup1.id, warehouse_id=wh_central.id, status=POStatus.CLOSED, order_date=date.today() - timedelta(days=45), expected_date=date.today() - timedelta(days=35), created_by=manager.id)
    db.add_all([po1, po2, po3, po4, po5, po6])
    await db.flush()

    # PO Items
    po_items = [
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po1.id, product_id=product_by_sku["MICRO-328P"].id, quantity_ordered=Decimal("2000"), quantity_received=Decimal("2000"), unit_cost=Decimal("2.50")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po1.id, product_id=product_by_sku["SENSOR-DHT22"].id, quantity_ordered=Decimal("100"), quantity_received=Decimal("100"), unit_cost=Decimal("3.80")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po2.id, product_id=product_by_sku["RASPBERRY-PI-4B"].id, quantity_ordered=Decimal("30"), quantity_received=Decimal("0"), unit_cost=Decimal("45.00")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po2.id, product_id=product_by_sku["USB-C-CABLE-1M"].id, quantity_ordered=Decimal("200"), quantity_received=Decimal("0"), unit_cost=Decimal("3.20")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po3.id, product_id=product_by_sku["BOLT-M6x20"].id, quantity_ordered=Decimal("1000"), quantity_received=Decimal("0"), unit_cost=Decimal("1.20")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po4.id, product_id=product_by_sku["SOLDER-60-40"].id, quantity_ordered=Decimal("100"), quantity_received=Decimal("0"), unit_cost=Decimal("5.20")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po4.id, product_id=product_by_sku["WIRE-AWG22"].id, quantity_ordered=Decimal("100"), quantity_received=Decimal("0"), unit_cost=Decimal("3.50")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po5.id, product_id=product_by_sku["CAP-100UF"].id, quantity_ordered=Decimal("10000"), quantity_received=Decimal("6000"), unit_cost=Decimal("0.08")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po5.id, product_id=product_by_sku["RES-10K"].id, quantity_ordered=Decimal("20000"), quantity_received=Decimal("10000"), unit_cost=Decimal("0.02")),
        PurchaseOrderItem(id=uuid.uuid4(), purchase_order_id=po6.id, product_id=product_by_sku["HDMI-2M"].id, quantity_ordered=Decimal("100"), quantity_received=Decimal("100"), unit_cost=Decimal("4.50")),
    ]
    db.add_all(po_items)
    await db.flush()

    # ── 11. Sales Orders ───────────────────────────────────────────────────────
    print("   Creating sales orders...")
    so1 = SalesOrder(id=uuid.uuid4(), customer_id=customers[0].id, warehouse_id=wh_east.id, status=SOStatus.DELIVERED, order_date=date.today() - timedelta(days=10), created_by=manager.id)
    so2 = SalesOrder(id=uuid.uuid4(), customer_id=customers[1].id, warehouse_id=wh_west.id, status=SOStatus.SHIPPED, order_date=date.today() - timedelta(days=5), created_by=employee1.id)
    so3 = SalesOrder(id=uuid.uuid4(), customer_id=customers[2].id, warehouse_id=wh_east.id, status=SOStatus.CONFIRMED, order_date=date.today() - timedelta(days=2), created_by=sc_manager.id)
    so4 = SalesOrder(id=uuid.uuid4(), customer_id=customers[3].id, warehouse_id=wh_central.id, status=SOStatus.DRAFT, order_date=date.today(), created_by=employee2.id)
    so5 = SalesOrder(id=uuid.uuid4(), customer_id=customers[4].id, warehouse_id=wh_west.id, status=SOStatus.FULFILLED, order_date=date.today() - timedelta(days=3), created_by=manager.id)
    so6 = SalesOrder(id=uuid.uuid4(), customer_id=customers[0].id, warehouse_id=wh_east.id, status=SOStatus.DELIVERED, order_date=date.today() - timedelta(days=20), created_by=sc_manager.id)
    so7 = SalesOrder(id=uuid.uuid4(), customer_id=customers[2].id, warehouse_id=wh_west.id, status=SOStatus.CANCELLED, order_date=date.today() - timedelta(days=8), created_by=manager.id)
    db.add_all([so1, so2, so3, so4, so5, so6, so7])
    await db.flush()

    so_items = [
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so1.id, product_id=product_by_sku["MICRO-328P"].id, quantity_ordered=Decimal("500"), quantity_fulfilled=Decimal("500"), unit_price=Decimal("6.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so1.id, product_id=product_by_sku["SENSOR-DHT22"].id, quantity_ordered=Decimal("50"), quantity_fulfilled=Decimal("50"), unit_price=Decimal("9.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so2.id, product_id=product_by_sku["RASPBERRY-PI-4B"].id, quantity_ordered=Decimal("10"), quantity_fulfilled=Decimal("10"), unit_price=Decimal("89.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so2.id, product_id=product_by_sku["USB-C-CABLE-1M"].id, quantity_ordered=Decimal("20"), quantity_fulfilled=Decimal("20"), unit_price=Decimal("12.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so3.id, product_id=product_by_sku["RELAY-5V"].id, quantity_ordered=Decimal("200"), quantity_fulfilled=Decimal("0"), unit_price=Decimal("4.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so3.id, product_id=product_by_sku["MOTOR-STEPPER"].id, quantity_ordered=Decimal("30"), quantity_fulfilled=Decimal("0"), unit_price=Decimal("24.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so4.id, product_id=product_by_sku["LED-5MM-RED"].id, quantity_ordered=Decimal("1000"), quantity_fulfilled=Decimal("0"), unit_price=Decimal("0.25")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so5.id, product_id=product_by_sku["CAP-100UF"].id, quantity_ordered=Decimal("3000"), quantity_fulfilled=Decimal("3000"), unit_price=Decimal("0.35")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so5.id, product_id=product_by_sku["RES-10K"].id, quantity_ordered=Decimal("5000"), quantity_fulfilled=Decimal("5000"), unit_price=Decimal("0.10")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so6.id, product_id=product_by_sku["BREADBOARD-830"].id, quantity_ordered=Decimal("40"), quantity_fulfilled=Decimal("40"), unit_price=Decimal("8.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so6.id, product_id=product_by_sku["MICRO-328P"].id, quantity_ordered=Decimal("300"), quantity_fulfilled=Decimal("300"), unit_price=Decimal("6.99")),
        SalesOrderItem(id=uuid.uuid4(), sales_order_id=so7.id, product_id=product_by_sku["HDMI-2M"].id, quantity_ordered=Decimal("50"), quantity_fulfilled=Decimal("0"), unit_price=Decimal("19.99")),
    ]
    db.add_all(so_items)
    await db.flush()

    # ── 12. Shipments ──────────────────────────────────────────────────────────
    print("   Creating shipments...")
    shipments = [
        Shipment(id=uuid.uuid4(), shipment_type=ShipmentType.INBOUND, reference_type=ShipmentReferenceType.PO, reference_id=po1.id, carrier="FedEx Freight", tracking_number="FX123456789", origin="Acme Components Ltd", destination="East DC", status=ShipmentStatus.DELIVERED, expected_date=date.today() - timedelta(days=5), delivered_at=datetime.now(timezone.utc) - timedelta(days=4)),
        Shipment(id=uuid.uuid4(), shipment_type=ShipmentType.INBOUND, reference_type=ShipmentReferenceType.PO, reference_id=po2.id, carrier="UPS Freight", tracking_number="UPS987654321", origin="TechCore Supply", destination="West DC", status=ShipmentStatus.IN_TRANSIT, expected_date=date.today() + timedelta(days=3)),
        Shipment(id=uuid.uuid4(), shipment_type=ShipmentType.OUTBOUND, reference_type=ShipmentReferenceType.SO, reference_id=so1.id, carrier="DHL Express", tracking_number="DHL555444333", origin="East DC", destination="TechBuilders Inc, Austin TX", status=ShipmentStatus.DELIVERED, expected_date=date.today() - timedelta(days=3), delivered_at=datetime.now(timezone.utc) - timedelta(days=2)),
        Shipment(id=uuid.uuid4(), shipment_type=ShipmentType.OUTBOUND, reference_type=ShipmentReferenceType.SO, reference_id=so2.id, carrier="FedEx Ground", tracking_number="FX888777666", origin="West DC", destination="Maker Space Hub, Portland OR", status=ShipmentStatus.IN_TRANSIT, expected_date=date.today() + timedelta(days=1)),
        Shipment(id=uuid.uuid4(), shipment_type=ShipmentType.INBOUND, reference_type=ShipmentReferenceType.PO, reference_id=po5.id, carrier="XPO Logistics", tracking_number="XPO111222333", origin="Global Parts Inc", destination="West DC", status=ShipmentStatus.DELAYED, expected_date=date.today() - timedelta(days=2)),
    ]
    db.add_all(shipments)
    await db.flush()

    # ── 13. KPI Snapshots (30 days history) ────────────────────────────────────
    print("   Creating KPI snapshots (30 days history)...")
    base_date = date.today()
    random.seed(42)

    for days_ago in range(30, -1, -1):
        snap_date = base_date - timedelta(days=days_ago)
        trend = days_ago / 30  # 0 = today, 1 = 30 days ago

        snapshots = [
            KpiSnapshot(id=uuid.uuid4(), kpi_code="revenue_mtd", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(42000 + random.uniform(-3000, 8000) * (1 - trend * 0.3), 2))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="cost_mtd", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(28000 + random.uniform(-2000, 4000) * (1 - trend * 0.3), 2))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="profit_margin_pct", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(33 - trend * 5 + random.uniform(-3, 3), 2))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="order_fulfillment_rate", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(87 + random.uniform(-5, 8), 2))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="inventory_turnover", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(3.8 + random.uniform(-0.5, 0.8), 3))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="dead_stock_pct", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(12 + random.uniform(-3, 5), 2))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="monthly_growth_pct", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(8.5 - trend * 3 + random.uniform(-2, 4), 2))), snapshot_date=snap_date, metadata_={"this_month": 42000, "last_month": 38700}),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="demand_30d", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(15000 + random.uniform(-1500, 3000), 0))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="purchase_spend_30d", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(32000 + random.uniform(-3000, 5000), 2))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="inventory_aging_over_90d_pct", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(8 + random.uniform(-2, 4), 2))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="business_health_score", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(72 + random.uniform(-5, 8), 1))), snapshot_date=snap_date),
            KpiSnapshot(id=uuid.uuid4(), kpi_code="supply_chain_efficiency", scope_type=KpiScope.GLOBAL, value=Decimal(str(round(68 + random.uniform(-6, 10), 1))), snapshot_date=snap_date),
        ]
        # Per-warehouse utilization
        for wh, base_util in [(wh_east, 78), (wh_west, 52), (wh_central, 91)]:
            snapshots.append(KpiSnapshot(id=uuid.uuid4(), kpi_code="warehouse_utilization", scope_type=KpiScope.WAREHOUSE, scope_id=wh.id, value=Decimal(str(round(base_util + random.uniform(-5, 5), 2))), snapshot_date=snap_date, metadata_={"total_qty": base_util * 500, "capacity": 50000 if wh == wh_east else (75000 if wh == wh_west else 30000)}))
        # Per-supplier reliability
        for sup, base_score in [(sup1, 88.5), (sup2, 72), (sup3, 94), (sup4, 61.5), (sup5, 91), (sup6, 83)]:
            snapshots.append(KpiSnapshot(id=uuid.uuid4(), kpi_code="supplier_reliability", scope_type=KpiScope.SUPPLIER, scope_id=sup.id, value=Decimal(str(round(base_score + random.uniform(-3, 3), 2))), snapshot_date=snap_date))

        db.add_all(snapshots)
    await db.flush()

    # ── 14. Alerts ─────────────────────────────────────────────────────────────
    print("   Creating alerts...")
    alerts = [
        Alert(id=uuid.uuid4(), alert_type="low_stock", severity=AlertSeverity.CRITICAL, entity_type="product", entity_id=product_by_sku["SOLDER-60-40"].id, message="Solder Wire 60/40 is critically low (5 units in Central Hub) — stockout imminent within 3 days at current consumption rate.", status=AlertStatus.OPEN),
        Alert(id=uuid.uuid4(), alert_type="low_stock", severity=AlertSeverity.WARNING, entity_type="product", entity_id=product_by_sku["WIRE-AWG22"].id, message="Hook-up Wire AWG22 is below reorder point in East DC (8 units remaining vs reorder point of 30).", status=AlertStatus.OPEN),
        Alert(id=uuid.uuid4(), alert_type="warehouse_capacity", severity=AlertSeverity.WARNING, entity_type="warehouse", entity_id=wh_central.id, message="Central Hub is at 91% capacity (27,300/30,000 units). Stock redistribution to other warehouses recommended.", status=AlertStatus.OPEN),
        Alert(id=uuid.uuid4(), alert_type="supplier_delay", severity=AlertSeverity.WARNING, entity_type="supplier", entity_id=sup4.id, message="Global Parts Inc shipment (PO #5) is 2 days overdue. Supplier reliability score has dropped to 61.5/100.", status=AlertStatus.OPEN),
        Alert(id=uuid.uuid4(), alert_type="low_stock", severity=AlertSeverity.WARNING, entity_type="product", entity_id=product_by_sku["HDMI-2M"].id, message="HDMI Cable 2m is out of stock in Central Hub (0 units).", status=AlertStatus.ACKNOWLEDGED),
        Alert(id=uuid.uuid4(), alert_type="warehouse_capacity", severity=AlertSeverity.INFO, entity_type="warehouse", entity_id=wh_east.id, message="East Distribution Center is at 78% capacity. No action required at this time.", status=AlertStatus.RESOLVED),
    ]
    db.add_all(alerts)
    await db.flush()

    # ── 15. Notifications ──────────────────────────────────────────────────────
    print("   Creating notifications...")
    notifs = [
        Notification(id=uuid.uuid4(), user_id=manager.id, alert_id=alerts[0].id, title="🚨 Critical: Stockout imminent — Solder Wire", body=alerts[0].message, is_read=False),
        Notification(id=uuid.uuid4(), user_id=manager.id, alert_id=alerts[1].id, title="⚠️ Low stock warning — AWG22 Wire", body=alerts[1].message, is_read=False),
        Notification(id=uuid.uuid4(), user_id=employee1.id, alert_id=alerts[2].id, title="⚠️ Warehouse capacity alert — Central Hub", body=alerts[2].message, is_read=True),
        Notification(id=uuid.uuid4(), user_id=sc_manager.id, alert_id=alerts[3].id, title="⏰ Supplier delay — Global Parts Inc", body=alerts[3].message, is_read=False),
        Notification(id=uuid.uuid4(), user_id=admin.id, alert_id=alerts[0].id, title="🚨 Critical: Stockout imminent — Solder Wire", body=alerts[0].message, is_read=False),
    ]
    db.add_all(notifs)
    await db.flush()

    # ── 16. AI Insights ────────────────────────────────────────────────────────
    print("   Creating AI insights...")
    ai_insights = [
        AiInsight(id=uuid.uuid4(), category=InsightCategory.INVENTORY, entity_type="product", entity_id=product_by_sku["SOLDER-60-40"].id, insight_text="🚨 STOCKOUT: Solder Wire 60/40 (SKU: SOLDER-60-40) has only 5 units remaining in Central Hub, with an estimated 3 days of stock left at the current sell-through rate. Consider reordering 100 units from the preferred supplier immediately.", confidence_score=Decimal("0.97"), severity=InsightSeverity.CRITICAL, model_version="template-v1"),
        AiInsight(id=uuid.uuid4(), category=InsightCategory.WAREHOUSE, entity_type="warehouse", entity_id=wh_central.id, insight_text="🏭 Central Hub is at 91.0% capacity (27,300/30,000 units). Plan stock redistribution immediately to avoid capacity breach and potential receiving disruptions.", confidence_score=Decimal("0.92"), severity=InsightSeverity.CRITICAL, model_version="template-v1"),
        AiInsight(id=uuid.uuid4(), category=InsightCategory.SUPPLIER, entity_type="supplier", entity_id=sup4.id, insight_text="⏰ Global Parts Inc has a reliability score of 61/100, with an average lead time of 21 days. Their current shipment is overdue by 2 days. Consider qualifying a backup supplier for critical SKUs sourced from this vendor.", confidence_score=Decimal("0.88"), severity=InsightSeverity.WARNING, model_version="template-v1"),
        AiInsight(id=uuid.uuid4(), category=InsightCategory.FINANCIAL, insight_text="📈 Revenue grew +8.5% month-over-month ($42,000 vs $38,700). Strong performance — maintain momentum. Focus on high-margin SKUs (Raspberry Pi, ESP8266 modules) which are driving disproportionate revenue growth.", confidence_score=Decimal("0.95"), severity=InsightSeverity.INFO, model_version="template-v1"),
        AiInsight(id=uuid.uuid4(), category=InsightCategory.INVENTORY, insight_text="📦 Dead stock is at 12.4% of total inventory value ($8,400), exceeding the healthy threshold of 10%. HDMI cables and certain fasteners show no movement in 90+ days. Consider a clearance promotion or return-to-supplier agreement.", confidence_score=Decimal("0.89"), severity=InsightSeverity.WARNING, model_version="template-v1"),
        AiInsight(id=uuid.uuid4(), category=InsightCategory.SALES, insight_text="📋 Order fulfillment rate is at 87.3% in the last 30 days, slightly below the 90% target. Low stock on Wire AWG22 and Solder Wire is causing fulfillment delays. Prioritize restocking these SKUs to recover the fulfillment rate.", confidence_score=Decimal("0.91"), severity=InsightSeverity.WARNING, model_version="template-v1"),
    ]
    db.add_all(ai_insights)
    await db.flush()

    await db.commit()
    print("[+] Seed complete!")
    print(f"\n[Summary]")
    print(f"   Users: 5 (admin@supplyiq.com / Admin@123)")
    print(f"   Products: {len(product_objs)}")
    print(f"   Suppliers: 6")
    print(f"   Warehouses: 3")
    print(f"   Purchase Orders: 6")
    print(f"   Sales Orders: 7")
    print(f"   Shipments: 5")
    print(f"   KPI Snapshots: ~31 days of history")
    print(f"   Alerts: {len(alerts)}")
    print(f"   AI Insights: {len(ai_insights)}")


async def main():
    async with AsyncSessionLocal() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
