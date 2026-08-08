from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from uuid import UUID
from typing import Optional
from datetime import date

from app.db.session import get_db
from app.schemas.schemas import AiInsightOut, PaginatedResponse
from app.models.ai_insight import AiInsight
from app.services.ai_insight_engine.engine import AiInsightEngine
from app.core.security import require_permission
from app.core.permissions import AI_INSIGHT_READ, AI_INSIGHT_GENERATE

router = APIRouter(prefix="/ai-insights", tags=["AI Insights"])


@router.get("", response_model=PaginatedResponse)
async def list_insights(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    severity: Optional[str] = None,
    entity_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(AI_INSIGHT_READ)),
):
    skip = (page - 1) * page_size
    query = select(AiInsight)
    if category:
        query = query.where(AiInsight.category == category)
    if severity:
        query = query.where(AiInsight.severity == severity)
    if entity_type:
        query = query.where(AiInsight.entity_type == entity_type)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(desc(AiInsight.generated_at)).offset(skip).limit(page_size))
    return PaginatedResponse(
        items=[AiInsightOut.model_validate(i) for i in result.scalars().all()],
        total=total, page=page, page_size=page_size
    )


@router.get("/dashboard-summary")
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(AI_INSIGHT_READ)),
):
    """Top 5 most recent insights sorted by severity for the dashboard feed."""
    from app.models.ai_insight import InsightSeverity
    result = await db.execute(
        select(AiInsight)
        .order_by(desc(AiInsight.generated_at))
        .limit(10)
    )
    all_insights = result.scalars().all()
    # Sort by severity then recency
    sev_order = {InsightSeverity.CRITICAL: 0, InsightSeverity.WARNING: 1, InsightSeverity.INFO: 2}
    sorted_insights = sorted(all_insights, key=lambda x: (sev_order.get(x.severity, 3), -x.generated_at.timestamp()))
    return [AiInsightOut.model_validate(i) for i in sorted_insights[:5]]


@router.post("/generate")
async def generate_insights(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_permission(AI_INSIGHT_GENERATE)),
):
    async def _run():
        engine = AiInsightEngine(db)
        await engine.generate_all()
        await db.commit()

    background_tasks.add_task(_run)
    return {"message": "AI insight generation triggered", "status": "running"}
