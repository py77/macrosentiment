from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.schemas.indicator import IndicatorHistoryOut, IndicatorValueOut

router = APIRouter()


@router.get("/indicators")
async def list_indicators(db: AsyncSession = Depends(get_db)):
    """List all indicators with latest values."""
    from app.api.dashboard import _build_indicator_out

    result = await db.execute(
        select(Indicator).order_by(Indicator.category, Indicator.name)
    )
    indicators = result.scalars().all()

    return [await _build_indicator_out(db, ind) for ind in indicators]


@router.get("/indicators/{series_id}/history", response_model=IndicatorHistoryOut)
async def get_indicator_history(
    series_id: str,
    start: date | None = None,
    end: date | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Get historical values for a specific indicator."""
    result = await db.execute(
        select(Indicator).where(Indicator.series_id == series_id)
    )
    indicator = result.scalar_one_or_none()
    if not indicator:
        raise HTTPException(status_code=404, detail=f"Indicator {series_id} not found")

    query = select(IndicatorValue).where(
        IndicatorValue.indicator_id == indicator.id
    )
    if start:
        query = query.where(IndicatorValue.date >= start)
    if end:
        query = query.where(IndicatorValue.date <= end)
    query = query.order_by(IndicatorValue.date.asc())

    val_result = await db.execute(query)
    values = val_result.scalars().all()

    return IndicatorHistoryOut(
        series_id=indicator.series_id,
        name=indicator.name,
        category=indicator.category,
        values=[IndicatorValueOut.model_validate(v) for v in values],
    )


