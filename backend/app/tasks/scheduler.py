import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import async_session
from app.services.data_fetcher import fetch_all

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()


async def evening_fetch_job():
    """Daily evening fetch: FRED + IBKR (23:00 UTC)."""
    logger.info("Running evening data fetch (FRED + IBKR)")
    async with async_session() as db:
        try:
            result = await fetch_all(db, include_ibkr=True)
            logger.info(f"Evening fetch complete: {result}")
        except Exception as e:
            logger.error(f"Evening fetch failed: {e}")


async def morning_fetch_job():
    """Morning fetch: FRED only for overnight releases (13:30 UTC)."""
    now = datetime.now(timezone.utc)
    if now.weekday() >= 5:  # Skip weekends
        return
    logger.info("Running morning data fetch (FRED only)")
    async with async_session() as db:
        try:
            result = await fetch_all(db, include_ibkr=False)
            logger.info(f"Morning fetch complete: {result}")
        except Exception as e:
            logger.error(f"Morning fetch failed: {e}")


def start_scheduler():
    # Evening fetch: daily at 23:00 UTC
    # misfire_grace_time=None → run no matter how late (host sleep/hibernate tolerant)
    scheduler.add_job(
        evening_fetch_job,
        "cron",
        hour=23,
        minute=0,
        id="evening_fetch",
        misfire_grace_time=None,
        coalesce=True,
    )
    # Morning fetch: weekdays at 13:30 UTC (after US data releases)
    scheduler.add_job(
        morning_fetch_job,
        "cron",
        hour=13,
        minute=30,
        id="morning_fetch",
        misfire_grace_time=None,
        coalesce=True,
    )
    scheduler.start()
    logger.info("Scheduler started with evening (23:00 UTC) and morning (13:30 UTC) jobs")


def stop_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped")
