from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.sales_order import SalesOrder, SalesOrderItem, SOStatus
from app.models.inventory_movement import ReferenceType
from app.services.inventory_service import InventoryService


VALID_TRANSITIONS = {
    SOStatus.DRAFT: {SOStatus.CONFIRMED, SOStatus.CANCELLED},
    SOStatus.CONFIRMED: {SOStatus.FULFILLED, SOStatus.CANCELLED},
    SOStatus.FULFILLED: {SOStatus.SHIPPED, SOStatus.CANCELLED},
    SOStatus.SHIPPED: {SOStatus.DELIVERED},
    SOStatus.DELIVERED: set(),
    SOStatus.CANCELLED: set(),
}


class SalesOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _assert_transition(self, so: SalesOrder, target: SOStatus):
        if target not in VALID_TRANSITIONS.get(so.status, set()):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition SO from '{so.status}' to '{target}'",
            )

    async def create_so(self, data: dict, created_by: UUID) -> SalesOrder:
        items_data = data.pop("items")
        so = SalesOrder(**data, created_by=created_by)
        self.db.add(so)
        await self.db.flush()

        for item in items_data:
            soi = SalesOrderItem(
                sales_order_id=so.id,
                product_id=item["product_id"],
                quantity_ordered=item["quantity_ordered"],
                quantity_fulfilled=Decimal("0"),
                unit_price=item["unit_price"],
            )
            self.db.add(soi)
        await self.db.flush()
        await self.db.refresh(so)
        return so

    async def confirm(self, so_id: UUID) -> SalesOrder:
        so = await self.db.get(SalesOrder, so_id)
        if not so:
            raise HTTPException(status_code=404, detail="Sales order not found")
        self._assert_transition(so, SOStatus.CONFIRMED)
        so.status = SOStatus.CONFIRMED
        await self.db.flush()
        await self.db.refresh(so)
        return so

    async def fulfill(self, so_id: UUID, user_id: UUID) -> SalesOrder:
        """Fulfill the order — creates OUT inventory movements."""
        so = await self.db.get(SalesOrder, so_id)
        if not so:
            raise HTTPException(status_code=404, detail="Sales order not found")
        self._assert_transition(so, SOStatus.FULFILLED)

        result = await self.db.execute(
            select(SalesOrderItem).where(SalesOrderItem.sales_order_id == so_id)
        )
        items = result.scalars().all()

        inventory_data = []
        for item in items:
            qty_to_fulfill = item.quantity_ordered - item.quantity_fulfilled
            if qty_to_fulfill <= 0:
                continue
            item.quantity_fulfilled += qty_to_fulfill
            inventory_data.append({
                "product_id": item.product_id,
                "warehouse_id": so.warehouse_id,
                "quantity": qty_to_fulfill,
            })

        if inventory_data:
            inv_service = InventoryService(self.db)
            await inv_service.record_outbound(inventory_data, ReferenceType.SO, so_id, user_id)

        so.status = SOStatus.FULFILLED
        await self.db.flush()
        await self.db.refresh(so)
        return so

    async def ship(self, so_id: UUID) -> SalesOrder:
        so = await self.db.get(SalesOrder, so_id)
        if not so:
            raise HTTPException(status_code=404, detail="Sales order not found")
        self._assert_transition(so, SOStatus.SHIPPED)
        so.status = SOStatus.SHIPPED
        await self.db.flush()
        await self.db.refresh(so)
        return so

    async def cancel(self, so_id: UUID) -> SalesOrder:
        so = await self.db.get(SalesOrder, so_id)
        if not so:
            raise HTTPException(status_code=404, detail="Sales order not found")
        self._assert_transition(so, SOStatus.CANCELLED)
        so.status = SOStatus.CANCELLED
        await self.db.flush()
        await self.db.refresh(so)
        return so
