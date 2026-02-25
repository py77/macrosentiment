from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.models.regime import RegimeSnapshot
from app.schemas.dashboard import CategorySummary, DashboardOut
from app.schemas.indicator import IndicatorOut
from app.schemas.regime import RegimeOut
from app.services.indicator_processor import determine_signal

router = APIRouter()


async def _build_indicator_out(db: AsyncSession, ind: Indicator) -> IndicatorOut:
    """Build an IndicatorOut from an Indicator model with latest values."""
    # Get latest value
    result = await db.execute(
        select(IndicatorValue)
        .where(IndicatorValue.indicator_id == ind.id)
        .order_by(IndicatorValue.date.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()

    # Get recent values for sparkline and changes
    sparkline_result = await db.execute(
        select(IndicatorValue)
        .where(
            and_(
                IndicatorValue.indicator_id == ind.id,
                IndicatorValue.date >= date.today() - timedelta(days=60),
            )
        )
        .order_by(IndicatorValue.date.asc())
    )
    recent = sparkline_result.scalars().all()
    sparkline = [r.value for r in recent[-30:]] if recent else []

    # Compute changes
    change_1d = None
    change_1w = None
    change_1m = None
    if len(recent) >= 2:
        change_1d = round(recent[-1].value - recent[-2].value, 4)
    if len(recent) >= 6:
        change_1w = round(recent[-1].value - recent[-6].value, 4)
    if len(recent) >= 22:
        change_1m = round(recent[-1].value - recent[-22].value, 4)

    signal = determine_signal(latest.z_score if latest else None, ind.higher_is_bullish)

    return IndicatorOut(
        id=ind.id,
        series_id=ind.series_id,
        name=ind.name,
        category=ind.category,
        source=ind.source,
        frequency=ind.frequency,
        weight=ind.weight,
        higher_is_bullish=ind.higher_is_bullish,
        unit=ind.unit,
        description=ind.description,
        latest_value=latest.value if latest else None,
        latest_date=latest.date if latest else None,
        z_score=latest.z_score if latest else None,
        percentile=latest.percentile if latest else None,
        change_1d=change_1d,
        change_1w=change_1w,
        change_1m=change_1m,
        signal=signal,
        sparkline=sparkline,
    )


@router.get("/dashboard", response_model=DashboardOut)
async def get_dashboard(db: AsyncSession = Depends(get_db)):
    """Full dashboard payload: regime + score + categories + indicators."""
    # Get current regime
    regime_result = await db.execute(
        select(RegimeSnapshot).order_by(RegimeSnapshot.date.desc()).limit(1)
    )
    regime_row = regime_result.scalar_one_or_none()
    regime_out = RegimeOut.model_validate(regime_row) if regime_row else None

    # Get all indicators with latest data
    ind_result = await db.execute(
        select(Indicator).order_by(Indicator.category, Indicator.name)
    )
    indicators = ind_result.scalars().all()

    indicator_outs = []
    for ind in indicators:
        indicator_outs.append(await _build_indicator_out(db, ind))

    # Build category summaries
    categories_map: dict[str, list[IndicatorOut]] = {}
    for io in indicator_outs:
        categories_map.setdefault(io.category, []).append(io)

    category_summaries = []
    for cat_name, cat_indicators in categories_map.items():
        # Category signal: majority vote from indicators
        signals = [i.signal for i in cat_indicators if i.signal != "neutral"]
        if signals:
            bullish_count = signals.count("bullish")
            bearish_count = signals.count("bearish")
            if bullish_count > bearish_count:
                cat_signal = "bullish"
            elif bearish_count > bullish_count:
                cat_signal = "bearish"
            else:
                cat_signal = "neutral"
        else:
            cat_signal = "neutral"

        # Category score: average z-score
        z_scores = [i.z_score for i in cat_indicators if i.z_score is not None]
        cat_score = round(sum(z_scores) / len(z_scores), 4) if z_scores else 0.0

        # Top 3 indicators by weight for the card
        key_indicators = sorted(cat_indicators, key=lambda x: x.weight, reverse=True)[:3]

        category_summaries.append(CategorySummary(
            name=cat_name,
            signal=cat_signal,
            score=cat_score,
            key_indicators=key_indicators,
        ))

    return DashboardOut(
        last_updated=regime_row.date if regime_row else None,
        regime=regime_out,
        composite_score=regime_row.composite_score if regime_row else 0.0,
        categories=category_summaries,
        indicators=indicator_outs,
    )
