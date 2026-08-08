from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.db.session import get_db
from app.schemas.schemas import AlertOut, AlertUpdate, PaginatedResponse
from app.models.alert import Alert, AlertStatus
from app.core.security import require_permission
from app.core.permissions import ALERT_READ, ALERT_WRITE

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=PaginatedResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    alert_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(ALERT_READ)),
):
    skip = (page - 1) * page_size
    query = select(Alert)
    if severity:
        query = query.where(Alert.severity == severity)
    if status:
        query = query.where(Alert.status == status)
    if alert_type:
        query = query.where(Alert.alert_type == alert_type)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(Alert.created_at.desc()).offset(skip).limit(page_size))
    return PaginatedResponse(
        items=[AlertOut.model_validate(a) for a in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.patch("/{alert_id}", response_model=AlertOut)
async def update_alert(
    alert_id: UUID,
    body: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(ALERT_WRITE)),
):
    from datetime import datetime, timezone
    alert = await db.get(Alert, alert_id)
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus(body.status)
    if alert.status == AlertStatus.RESOLVED:
        alert.resolved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(alert)
    return alert
