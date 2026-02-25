import logging
from datetime import date

import numpy as np
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.models.regime import RegimeSnapshot

logger = logging.getLogger(__name__)

# Category weights for composite score
CATEGORY_WEIGHTS = {
    "growth": 0.30,
    "inflation": 0.15,
    "rates": 0.15,
    "credit": 0.15,
    "sentiment": 0.10,
    "liquidity": 0.10,
    "equity": 0.05,
}

# Which direction is bullish for each category score
CATEGORY_BULLISH_DIRECTION = {
    "growth": 1,        # Higher growth = bullish
    "inflation": -1,    # Lower inflation = bullish
    "rates": -1,        # Lower rates = bullish (generally)
    "credit": -1,       # Lower spreads = bullish
    "sentiment": -1,    # Lower VIX = bullish
    "liquidity": 1,     # More liquidity = bullish
    "equity": 1,        # Higher equity = bullish
    "labor": 1,         # Better labor = bullish (will merge into growth)
    "global": 0,        # Mixed signals
}


async def compute_composite_score(
    db: AsyncSession,
    as_of: date | None = None,
) -> tuple[float, dict[str, float]]:
    """
    Compute the composite sentiment score (-100 to +100).
    Returns (composite_score, category_scores_dict).
    """
    if as_of is None:
        as_of = date.today()

    # Get all indicators
    result = await db.execute(select(Indicator))
    indicators = result.scalars().all()

    # Group by category and compute weighted category z-scores
    category_zscores: dict[str, list[tuple[float, float]]] = {}  # category -> [(z, weight)]

    for ind in indicators:
        # Get latest z-score
        val_result = await db.execute(
            select(IndicatorValue.z_score)
            .where(
                and_(
                    IndicatorValue.indicator_id == ind.id,
                    IndicatorValue.date <= as_of,
                    IndicatorValue.z_score.isnot(None),
                )
            )
            .order_by(IndicatorValue.date.desc())
            .limit(1)
        )
        z = val_result.scalar_one_or_none()
        if z is None:
            continue

        # Map labor into growth for composite purposes
        cat = ind.category
        if cat == "labor":
            cat = "growth"
        if cat == "global":
            cat = "equity"

        if cat not in category_zscores:
            category_zscores[cat] = []

        # Adjust z-score direction based on higher_is_bullish
        effective_z = z if ind.higher_is_bullish else -z
        category_zscores[cat].append((effective_z, ind.weight))

    # Compute weighted average z-score per category
    category_scores = {}
    for cat, pairs in category_zscores.items():
        total_w = sum(w for _, w in pairs)
        if total_w > 0:
            cat_z = sum(z * w for z, w in pairs) / total_w
            category_scores[cat] = round(cat_z, 4)

    # Compute composite: weighted sum of category scores, scaled to -100..+100
    composite = 0.0
    total_weight = 0.0

    for cat, weight in CATEGORY_WEIGHTS.items():
        if cat in category_scores:
            direction = CATEGORY_BULLISH_DIRECTION.get(cat, 1)
            composite += category_scores[cat] * direction * weight
            total_weight += weight

    if total_weight > 0:
        composite /= total_weight

    # Scale from z-score space to -100..+100 (z of +-2 maps to +-100)
    composite_scaled = float(np.clip(composite * 50, -100, 100))

    return round(composite_scaled, 2), category_scores


async def compute_and_save_regime(
    db: AsyncSession,
    as_of: date | None = None,
) -> RegimeSnapshot | None:
    """Compute regime + composite score and save to database."""
    from app.services.regime_engine import compute_regime

    if as_of is None:
        as_of = date.today()

    snapshot = await compute_regime(db, as_of)
    if snapshot is None:
        return None

    # Compute composite score
    composite, category_scores = await compute_composite_score(db, as_of)
    snapshot.composite_score = composite
    snapshot.component_scores["category_scores"] = category_scores

    # Upsert: check if exists for this date
    existing = await db.execute(
        select(RegimeSnapshot).where(RegimeSnapshot.date == as_of)
    )
    existing_row = existing.scalar_one_or_none()

    if existing_row:
        existing_row.regime = snapshot.regime
        existing_row.growth_score = snapshot.growth_score
        existing_row.inflation_score = snapshot.inflation_score
        existing_row.confidence = snapshot.confidence
        existing_row.composite_score = snapshot.composite_score
        existing_row.component_scores = snapshot.component_scores
        await db.commit()
        logger.info(f"Updated regime snapshot for {as_of}: {snapshot.regime} ({composite})")
        return existing_row
    else:
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)
        logger.info(f"Created regime snapshot for {as_of}: {snapshot.regime} ({composite})")
        return snapshot
