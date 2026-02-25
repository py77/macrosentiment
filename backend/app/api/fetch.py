from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.models.fetch_log import FetchLog
from app.schemas.dashboard import FetchStatusOut, FetchTriggerOut
from app.services.data_fetcher import fetch_all

router = APIRouter()


async def _run_fetch():
    """Background task to run full data pipeline."""
    async with async_session() as db:
        await fetch_all(db)


@router.post("/fetch/trigger", response_model=FetchTriggerOut)
async def trigger_fetch(background_tasks: BackgroundTasks):
    """Manually trigger a data refresh."""
    background_tasks.add_task(_run_fetch)
    return FetchTriggerOut(
        status="started",
        message="Data fetch started in background",
        sources_fetched=["fred", "ibkr"],
    )


@router.get("/fetch/status", response_model=list[FetchStatusOut])
async def get_fetch_status(db: AsyncSession = Depends(get_db)):
    """Get last fetch time and status per source."""
    # Get latest log entry per source
    sources = ["fred", "ibkr"]
    statuses = []

    for source in sources:
        result = await db.execute(
            select(FetchLog)
            .where(FetchLog.source == source)
            .order_by(FetchLog.created_at.desc())
            .limit(1)
        )
        log = result.scalar_one_or_none()
        statuses.append(FetchStatusOut(
            source=source,
            last_fetch=log.created_at if log else None,
            status=log.status if log else None,
            records_added=log.records_added if log else 0,
            error_message=log.error_message if log else None,
        ))

    return statuses
