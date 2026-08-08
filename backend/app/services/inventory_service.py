"""
Inventory Service — The Core Invariant
======================================
quantity_on_hand on InventoryItem is NEVER written directly by any API endpoint.
It is ONLY updated as a side effect of an InventoryMovement insert,
inside the same DB transaction. This guarantees the ledger and cached balance
can never drift.

All stock-affecting operations go through this service.
"""
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.inventory_item import InventoryItem
from app.models.inventory_movement import InventoryMovement, MovementType, ReferenceType
from app.models.product import Product
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.notification import Notification
from fastapi import HTTPException


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_or_create_inventory_item(
        self, product_id: UUID, warehouse_id: UUID
    ) -> InventoryItem:
        """Get existing inventory item or create one with 0 quantity."""
        result = await self.db.execute(
            select(InventoryItem).where(
                InventoryItem.product_id == product_id,
                InventoryItem.warehouse_id == warehouse_id,
            )
        )
        item = result.scalar_one_or_none()
        if not item:
            item = InventoryItem(
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity_on_hand=Decimal("0"),
                quantity_reserved=Decimal("0"),
                safety_stock=Decimal("0"),
            )
            self.db.add(item)
            await self.db.flush()
            await self.db.refresh(item)
        return item

    async def _apply_movement(
        self,
        inventory_item: InventoryItem,
        movement_type: MovementType,
        quantity: Decimal,
        reference_type: Optional[ReferenceType],
        reference_id: Optional[UUID],
        reason: Optional[str],
        created_by: Optional[UUID],
    ) -> InventoryMovement:
        """Insert movement and atomically update quantity_on_hand."""
        movement = InventoryMovement(
            inventory_item_id=inventory_item.id,
            movement_type=movement_type,
            quantity=abs(quantity),
            reference_type=reference_type,
            reference_id=reference_id,
            reason=reason,
            created_by=created_by,
        )
        self.db.add(movement)

        # Update on-hand atomically — the ONLY place this happens
        if movement_type == MovementType.IN:
            inventory_item.quantity_on_hand += abs(quantity)
        elif movement_type in (MovementType.OUT, MovementType.TRANSFER):
            new_qty = inventory_item.quantity_on_hand - abs(quantity)
            if new_qty < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: {inventory_item.quantity_on_hand}, Requested: {abs(quantity)}",
                )
            inventory_item.quantity_on_hand = new_qty
        elif movement_type == MovementType.ADJUSTMENT:
            # quantity can be + or - for adjustments; stored abs, direction from sign
            inventory_item.quantity_on_hand += quantity  # signed quantity for adjustments

        await self.db.flush()
        return movement

    async def adjust_stock(
        self,
        product_id: UUID,
        warehouse_id: UUID,
        quantity: Decimal,  # signed: positive = add, negative = remove
        reason: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ) -> InventoryMovement:
        """Manual stock adjustment."""
        item = await self._get_or_create_inventory_item(product_id, warehouse_id)
        new_qty = item.quantity_on_hand + quantity
        if new_qty < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Adjustment would result in negative stock ({new_qty})",
            )
        movement = await self._apply_movement(
            item, MovementType.ADJUSTMENT, quantity,
            ReferenceType.MANUAL, None, reason, created_by
        )
        await self._check_reorder_alert(item, product_id)
        return movement

    async def transfer_stock(
        self,
        product_id: UUID,
        from_warehouse_id: UUID,
        to_warehouse_id: UUID,
        quantity: Decimal,
        reason: Optional[str] = None,
        created_by: Optional[UUID] = None,
    ):
        """Inter-warehouse transfer — creates OUT + IN movements atomically."""
        if from_warehouse_id == to_warehouse_id:
            raise HTTPException(status_code=400, detail="Source and destination warehouse must differ")

        from_item = await self._get_or_create_inventory_item(product_id, from_warehouse_id)
        to_item = await self._get_or_create_inventory_item(product_id, to_warehouse_id)

        out_movement = await self._apply_movement(
            from_item, MovementType.OUT, quantity,
            ReferenceType.MANUAL, None, reason or "Transfer out", created_by
        )
        await self._apply_movement(
            to_item, MovementType.IN, quantity,
            ReferenceType.MANUAL, None, reason or "Transfer in", created_by
        )
        await self._check_reorder_alert(from_item, product_id)
        return out_movement

    async def record_inbound(
        self,
        items: List[dict],  # [{"product_id": UUID, "quantity": Decimal, "warehouse_id": UUID}]
        reference_type: ReferenceType,
        reference_id: UUID,
        created_by: Optional[UUID] = None,
    ):
        """Record incoming stock (PO receiving, shipment delivery)."""
        movements = []
        for item_data in items:
            inv_item = await self._get_or_create_inventory_item(
                item_data["product_id"], item_data["warehouse_id"]
            )
            movement = await self._apply_movement(
                inv_item, MovementType.IN, item_data["quantity"],
                reference_type, reference_id, "Inbound receipt", created_by
            )
            movements.append(movement)
        return movements

    async def record_outbound(
        self,
        items: List[dict],  # [{"product_id": UUID, "quantity": Decimal, "warehouse_id": UUID}]
        reference_type: ReferenceType,
        reference_id: UUID,
        created_by: Optional[UUID] = None,
    ):
        """Record outgoing stock (SO fulfillment)."""
        movements = []
        for item_data in items:
            inv_item = await self._get_or_create_inventory_item(
                item_data["product_id"], item_data["warehouse_id"]
            )
            movement = await self._apply_movement(
                inv_item, MovementType.OUT, item_data["quantity"],
                reference_type, reference_id, "Outbound fulfillment", created_by
            )
            await self._check_reorder_alert(inv_item, item_data["product_id"])
            movements.append(movement)
        return movements

    async def _check_reorder_alert(self, item: InventoryItem, product_id: UUID):
        """Raise a low_stock alert if quantity falls below reorder point."""
        product = await self.db.get(Product, product_id)
        if not product:
            return
        if item.quantity_on_hand <= product.reorder_point:
            severity = (
                AlertSeverity.CRITICAL
                if item.quantity_on_hand <= 0
                else AlertSeverity.WARNING
            )
            alert = Alert(
                alert_type="low_stock",
                severity=severity,
                entity_type="product",
                entity_id=product_id,
                message=(
                    f"Product '{product.name}' (SKU: {product.sku}) in warehouse "
                    f"is at {item.quantity_on_hand} units — "
                    f"{'STOCKOUT' if item.quantity_on_hand <= 0 else 'below reorder point'} "
                    f"of {product.reorder_point}."
                ),
                status=AlertStatus.OPEN,
            )
            self.db.add(alert)
            await self.db.flush()
