from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.regime import RegimeSnapshot
from app.schemas.regime import RegimeHistoryOut, RegimeOut

router = APIRouter()


@router.get("/regime/current", response_model=RegimeOut | None)
async def get_current_regime(db: AsyncSession = Depends(get_db)):
    """Get the most recent regime classification."""
    result = await db.execute(
        select(RegimeSnapshot).order_by(RegimeSnapshot.date.desc()).limit(1)
    )
    row = result.scalar_one_or_none()
    if not row:
        return None
    return RegimeOut.model_validate(row)


@router.get("/regime/history", response_model=RegimeHistoryOut)
async def get_regime_history(
    limit: int = 365,
    db: AsyncSession = Depends(get_db),
):
    """Get historical regime timeline."""
    result = await db.execute(
        select(RegimeSnapshot)
        .order_by(RegimeSnapshot.date.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    return RegimeHistoryOut(
        snapshots=[RegimeOut.model_validate(r) for r in reversed(rows)]
    )
