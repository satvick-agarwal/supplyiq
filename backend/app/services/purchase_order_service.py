"""
Purchase Order Service — State Machine
=======================================
Valid transitions:
  draft → approved → sent → partially_received / received → closed | cancelled
  draft → cancelled
  approved → cancelled
"""
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem, POStatus
from app.models.inventory_movement import ReferenceType
from app.services.inventory_service import InventoryService


VALID_TRANSITIONS = {
    POStatus.DRAFT: {POStatus.APPROVED, POStatus.CANCELLED},
    POStatus.APPROVED: {POStatus.SENT, POStatus.CANCELLED},
    POStatus.SENT: {POStatus.PARTIALLY_RECEIVED, POStatus.RECEIVED, POStatus.CANCELLED},
    POStatus.PARTIALLY_RECEIVED: {POStatus.RECEIVED, POStatus.CLOSED, POStatus.CANCELLED},
    POStatus.RECEIVED: {POStatus.CLOSED},
    POStatus.CLOSED: set(),
    POStatus.CANCELLED: set(),
}


class PurchaseOrderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def _assert_transition(self, po: PurchaseOrder, target: POStatus):
        if target not in VALID_TRANSITIONS.get(po.status, set()):
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition PO from '{po.status}' to '{target}'",
            )

    async def create_po(self, data: dict, created_by: UUID) -> PurchaseOrder:
        items_data = data.pop("items")
        po = PurchaseOrder(**data, created_by=created_by)
        self.db.add(po)
        await self.db.flush()

        for item in items_data:
            poi = PurchaseOrderItem(
                purchase_order_id=po.id,
                product_id=item["product_id"],
                quantity_ordered=item["quantity_ordered"],
                quantity_received=Decimal("0"),
                unit_cost=item["unit_cost"],
            )
            self.db.add(poi)
        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def approve(self, po_id: UUID, user_id: UUID) -> PurchaseOrder:
        po = await self.db.get(PurchaseOrder, po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        self._assert_transition(po, POStatus.APPROVED)
        po.status = POStatus.APPROVED
        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def send(self, po_id: UUID) -> PurchaseOrder:
        po = await self.db.get(PurchaseOrder, po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        self._assert_transition(po, POStatus.SENT)
        po.status = POStatus.SENT
        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def receive_items(
        self, po_id: UUID, receive_items: List[dict], user_id: UUID
    ) -> PurchaseOrder:
        """Partial or full receipt of PO items. Creates IN inventory movements."""
        po = await self.db.get(PurchaseOrder, po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        if po.status not in {POStatus.SENT, POStatus.PARTIALLY_RECEIVED, POStatus.APPROVED}:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot receive items on PO in status '{po.status}'",
            )

        # Load PO items
        result = await self.db.execute(
            select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == po_id)
        )
        po_items = {str(item.product_id): item for item in result.scalars().all()}

        inventory_data = []
        for receive in receive_items:
            product_id_str = str(receive["product_id"])
            poi = po_items.get(product_id_str)
            if not poi:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product {product_id_str} not on this PO",
                )
            remaining = poi.quantity_ordered - poi.quantity_received
            qty = min(Decimal(str(receive["quantity_received"])), remaining)
            if qty <= 0:
                continue
            poi.quantity_received += qty
            inventory_data.append({
                "product_id": receive["product_id"],
                "warehouse_id": po.warehouse_id,
                "quantity": qty,
            })

        # Record inbound movements (atomic with on-hand update)
        if inventory_data:
            inv_service = InventoryService(self.db)
            await inv_service.record_inbound(
                inventory_data, ReferenceType.PO, po_id, user_id
            )

        # Auto-determine new PO status
        result2 = await self.db.execute(
            select(PurchaseOrderItem).where(PurchaseOrderItem.purchase_order_id == po_id)
        )
        all_items = result2.scalars().all()
        fully_received = all(
            item.quantity_received >= item.quantity_ordered for item in all_items
        )
        po.status = POStatus.RECEIVED if fully_received else POStatus.PARTIALLY_RECEIVED

        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def cancel(self, po_id: UUID) -> PurchaseOrder:
        po = await self.db.get(PurchaseOrder, po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        self._assert_transition(po, POStatus.CANCELLED)
        po.status = POStatus.CANCELLED
        await self.db.flush()
        await self.db.refresh(po)
        return po

    async def close(self, po_id: UUID) -> PurchaseOrder:
        po = await self.db.get(PurchaseOrder, po_id)
        if not po:
            raise HTTPException(status_code=404, detail="Purchase order not found")
        self._assert_transition(po, POStatus.CLOSED)
        po.status = POStatus.CLOSED
        await self.db.flush()
        await self.db.refresh(po)
        return po
