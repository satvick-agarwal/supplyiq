from fastapi import APIRouter

from app.api.v1 import (
    auth, users, categories, products, suppliers,
    warehouses, inventory, purchase_orders, sales_orders,
    customers, shipments, kpis, alerts, notifications,
    ai_insights, dashboard,
)
from app.api.v1.inventory import inventory_router, movements_router

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)
api_router.include_router(suppliers.router)
api_router.include_router(warehouses.router)
api_router.include_router(inventory_router)
api_router.include_router(movements_router)
api_router.include_router(purchase_orders.router)
api_router.include_router(sales_orders.router)
api_router.include_router(customers.router)
api_router.include_router(shipments.router)
api_router.include_router(kpis.router)
api_router.include_router(alerts.router)
api_router.include_router(notifications.router)
api_router.include_router(ai_insights.router)
api_router.include_router(dashboard.router)
