import logging
from datetime import date, timedelta

import numpy as np
from scipy import stats
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue

logger = logging.getLogger(__name__)

# Lookback window for z-score / percentile calculations
ZSCORE_LOOKBACK_DAYS = 750  # ~3 years


async def compute_stats_for_indicator(
    db: AsyncSession,
    indicator_id: int,
    as_of: date | None = None,
) -> None:
    """Compute z-scores and percentiles for all values of an indicator."""
    if as_of is None:
        as_of = date.today()

    lookback_start = as_of - timedelta(days=ZSCORE_LOOKBACK_DAYS)

    # Get historical values for the lookback window
    result = await db.execute(
        select(IndicatorValue)
        .where(
            and_(
                IndicatorValue.indicator_id == indicator_id,
                IndicatorValue.date >= lookback_start,
                IndicatorValue.date <= as_of,
            )
        )
        .order_by(IndicatorValue.date)
    )
    rows = result.scalars().all()

    if len(rows) < 10:
        logger.warning(f"Not enough data for indicator {indicator_id} to compute stats ({len(rows)} rows)")
        return

    values = np.array([r.value for r in rows])
    mean = np.mean(values)
    std = np.std(values, ddof=1)

    for row in rows:
        if std > 0:
            row.z_score = round((row.value - mean) / std, 4)
        else:
            row.z_score = 0.0
        row.percentile = round(
            float(stats.percentileofscore(values, row.value, kind="rank")), 2
        )

    await db.commit()
    logger.info(f"Updated z-scores/percentiles for indicator {indicator_id} ({len(rows)} values)")


async def compute_all_stats(db: AsyncSession) -> None:
    """Compute stats for all indicators."""
    result = await db.execute(select(Indicator))
    indicators = result.scalars().all()

    for ind in indicators:
        await compute_stats_for_indicator(db, ind.id)


def compute_changes(values: list[dict]) -> dict:
    """Compute 1d, 1w, 1m changes from a list of {date, value} dicts."""
    if not values:
        return {"change_1d": None, "change_1w": None, "change_1m": None}

    sorted_vals = sorted(values, key=lambda x: x["date"], reverse=True)
    latest = sorted_vals[0]["value"]

    def find_closest(target_date: date) -> float | None:
        for v in sorted_vals:
            if v["date"] <= target_date:
                return v["value"]
        return None

    today = sorted_vals[0]["date"]
    prev_1d = find_closest(today - timedelta(days=2))
    prev_1w = find_closest(today - timedelta(days=8))
    prev_1m = find_closest(today - timedelta(days=35))

    return {
        "change_1d": round(latest - prev_1d, 4) if prev_1d is not None else None,
        "change_1w": round(latest - prev_1w, 4) if prev_1w is not None else None,
        "change_1m": round(latest - prev_1m, 4) if prev_1m is not None else None,
    }


def determine_signal(z_score: float | None, higher_is_bullish: bool) -> str:
    """Determine bullish/bearish/neutral signal from z-score."""
    if z_score is None:
        return "neutral"

    effective_z = z_score if higher_is_bullish else -z_score

    if effective_z > 0.5:
        return "bullish"
    elif effective_z < -0.5:
        return "bearish"
    return "neutral"
