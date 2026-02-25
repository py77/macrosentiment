import logging
from datetime import date, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.models.fetch_log import FetchLog
from app.services.fred_client import fred_client, FRED_SERIES
from app.services.ibkr_client import fetch_ibkr_all, IBKR_CONTRACTS
from app.services.indicator_processor import compute_all_stats
from app.services.scoring_engine import compute_and_save_regime

logger = logging.getLogger(__name__)


async def _upsert_values(
    db: AsyncSession,
    indicator_id: int,
    observations: list[dict],
) -> int:
    """Insert or update indicator values. Returns count of new records."""
    count = 0
    for obs in observations:
        obs_date = obs["date"] if isinstance(obs["date"], date) else date.fromisoformat(str(obs["date"]))
        existing = await db.execute(
            select(IndicatorValue).where(
                and_(
                    IndicatorValue.indicator_id == indicator_id,
                    IndicatorValue.date == obs_date,
                )
            )
        )
        row = existing.scalar_one_or_none()
        if row:
            row.value = obs["value"]
        else:
            db.add(IndicatorValue(
                indicator_id=indicator_id,
                date=obs_date,
                value=obs["value"],
            ))
            count += 1
    await db.commit()
    return count


async def fetch_fred_data(db: AsyncSession, backfill_years: int = 3) -> list[str]:
    """Fetch all FRED series and store in database."""
    fetched = []
    start_date = date.today() - timedelta(days=backfill_years * 365)

    all_data = await fred_client.fetch_all_series(start_date=start_date)

    for series_id, observations in all_data.items():
        try:
            # Look up indicator
            result = await db.execute(
                select(Indicator).where(Indicator.series_id == series_id)
            )
            indicator = result.scalar_one_or_none()
            if not indicator:
                logger.warning(f"Indicator {series_id} not found in database, skipping")
                continue

            count = await _upsert_values(db, indicator.id, observations)

            db.add(FetchLog(
                source="fred",
                series_id=series_id,
                status="success",
                records_added=count,
            ))
            await db.commit()
            fetched.append(series_id)
            logger.info(f"FRED {series_id}: {count} new records")

        except Exception as e:
            logger.error(f"Error processing FRED {series_id}: {e}")
            db.add(FetchLog(
                source="fred",
                series_id=series_id,
                status="error",
                error_message=str(e),
            ))
            await db.commit()

    return fetched


async def fetch_ibkr_data(db: AsyncSession) -> list[str]:
    """Fetch all IBKR market data and store in database."""
    fetched = []

    try:
        ibkr_data = await fetch_ibkr_all()
    except ConnectionError as e:
        logger.error(f"Cannot connect to IBKR: {e}")
        db.add(FetchLog(source="ibkr", status="error", error_message=str(e)))
        await db.commit()
        return fetched
    except Exception as e:
        logger.error(f"IBKR fetch failed: {e}")
        db.add(FetchLog(source="ibkr", status="error", error_message=str(e)))
        await db.commit()
        return fetched

    # Process snapshots
    for key, snap in ibkr_data.get("snapshots", {}).items():
        try:
            result = await db.execute(
                select(Indicator).where(Indicator.series_id == key)
            )
            indicator = result.scalar_one_or_none()
            if not indicator:
                continue

            today = date.today()
            count = await _upsert_values(db, indicator.id, [{"date": today, "value": snap["price"]}])
            fetched.append(key)

            db.add(FetchLog(source="ibkr", series_id=key, status="success", records_added=count))
            await db.commit()
            logger.info(f"IBKR snapshot {key}: {snap['price']}")
        except Exception as e:
            logger.error(f"Error processing IBKR snapshot {key}: {e}")

    # Process historical bars
    for key, bars in ibkr_data.get("historical", {}).items():
        try:
            result = await db.execute(
                select(Indicator).where(Indicator.series_id == key)
            )
            indicator = result.scalar_one_or_none()
            if not indicator:
                continue

            count = await _upsert_values(db, indicator.id, bars)
            logger.info(f"IBKR historical {key}: {count} new records")

            db.add(FetchLog(source="ibkr", series_id=key, status="success", records_added=count))
            await db.commit()
            fetched.append(key)
        except Exception as e:
            logger.error(f"Error processing IBKR historical {key}: {e}")

    return fetched


async def _compute_derived(db: AsyncSession):
    """Compute derived indicators like 2s10s spread from raw data."""
    # 2S10S = DGS10 - DGS2
    dgs10_ind = (await db.execute(select(Indicator).where(Indicator.series_id == "DGS10"))).scalar_one_or_none()
    dgs2_ind = (await db.execute(select(Indicator).where(Indicator.series_id == "DGS2"))).scalar_one_or_none()
    spread_ind = (await db.execute(select(Indicator).where(Indicator.series_id == "2S10S"))).scalar_one_or_none()

    if dgs10_ind and dgs2_ind and spread_ind:
        dgs10_vals = (await db.execute(
            select(IndicatorValue).where(IndicatorValue.indicator_id == dgs10_ind.id).order_by(IndicatorValue.date)
        )).scalars().all()
        dgs2_vals = (await db.execute(
            select(IndicatorValue).where(IndicatorValue.indicator_id == dgs2_ind.id).order_by(IndicatorValue.date)
        )).scalars().all()

        dgs2_map = {v.date: v.value for v in dgs2_vals}
        observations = []
        for v10 in dgs10_vals:
            if v10.date in dgs2_map:
                spread_bps = (v10.value - dgs2_map[v10.date]) * 100  # convert to bps
                observations.append({"date": v10.date, "value": spread_bps})

        if observations:
            count = await _upsert_values(db, spread_ind.id, observations)
            logger.info(f"Computed 2S10S spread: {count} new records from {len(observations)} dates")

    # SPX_VS_200D = (SPX / 200-day MA - 1) * 100  (percentage above/below)
    spx_ind = (await db.execute(select(Indicator).where(Indicator.series_id == "SPX"))).scalar_one_or_none()
    spx_ma_ind = (await db.execute(select(Indicator).where(Indicator.series_id == "SPX_VS_200D"))).scalar_one_or_none()

    if spx_ind and spx_ma_ind:
        spx_vals = (await db.execute(
            select(IndicatorValue).where(IndicatorValue.indicator_id == spx_ind.id).order_by(IndicatorValue.date)
        )).scalars().all()

        if len(spx_vals) >= 200:
            observations = []
            for i in range(199, len(spx_vals)):
                ma_200 = sum(v.value for v in spx_vals[i - 199:i + 1]) / 200
                if ma_200 > 0:
                    pct = (spx_vals[i].value / ma_200 - 1) * 100
                    observations.append({"date": spx_vals[i].date, "value": round(pct, 2)})

            if observations:
                count = await _upsert_values(db, spx_ma_ind.id, observations)
                logger.info(f"Computed SPX_VS_200D: {count} new records from {len(observations)} dates")


async def fetch_all(db: AsyncSession, include_ibkr: bool = True) -> dict:
    """Run full data pipeline: fetch → compute stats → compute regime."""
    sources_fetched = []

    # 1. Fetch FRED data
    fred_series = await fetch_fred_data(db)
    if fred_series:
        sources_fetched.append("fred")

    # 2. Fetch IBKR data
    if include_ibkr:
        ibkr_series = await fetch_ibkr_data(db)
        if ibkr_series:
            sources_fetched.append("ibkr")

    # 2b. Compute derived indicators
    await _compute_derived(db)

    # 3. Compute z-scores and percentiles
    await compute_all_stats(db)

    # 4. Compute regime + composite score
    snapshot = await compute_and_save_regime(db)

    return {
        "sources_fetched": sources_fetched,
        "regime": snapshot.regime if snapshot else None,
        "composite_score": snapshot.composite_score if snapshot else None,
    }
