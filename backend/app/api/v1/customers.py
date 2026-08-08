from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import CustomerCreate, CustomerUpdate, CustomerOut, SOOut, PaginatedResponse
from app.models.customer import Customer
from app.models.sales_order import SalesOrder
from app.core.security import require_permission
from app.core.permissions import CUSTOMER_READ, CUSTOMER_WRITE, CUSTOMER_DELETE, SO_READ

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("", response_model=PaginatedResponse)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CUSTOMER_READ)),
):
    skip = (page - 1) * page_size
    query = select(Customer)
    if search:
        query = query.where(Customer.name.ilike(f"%{search}%") | Customer.email.ilike(f"%{search}%"))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size).order_by(Customer.name))
    return PaginatedResponse(
        items=[CustomerOut.model_validate(c) for c in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.post("", response_model=CustomerOut, status_code=201)
async def create_customer(
    body: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CUSTOMER_WRITE)),
):
    customer = Customer(**body.model_dump())
    db.add(customer)
    await db.flush()
    await db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CUSTOMER_READ)),
):
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: UUID,
    body: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CUSTOMER_WRITE)),
):
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(customer, field, value)
    await db.flush()
    await db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(CUSTOMER_DELETE)),
):
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await db.delete(customer)
    await db.flush()


@router.get("/{customer_id}/orders", response_model=PaginatedResponse)
async def get_customer_orders(
    customer_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(SO_READ)),
):
    customer = await db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    skip = (page - 1) * page_size
    query = select(SalesOrder).where(SalesOrder.customer_id == customer_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.offset(skip).limit(page_size).order_by(SalesOrder.created_at.desc()))
    return PaginatedResponse(
        items=[SOOut.model_validate(o) for o in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )
