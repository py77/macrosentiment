import logging
from datetime import date, timedelta

import numpy as np
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.indicator import Indicator
from app.models.indicator_value import IndicatorValue
from app.models.regime import RegimeSnapshot

logger = logging.getLogger(__name__)

# Growth indicators and their weights
GROWTH_INDICATORS = {
    "INDPRO": {"weight": 0.20, "inverted": False},
    "ICSA": {"weight": 0.20, "inverted": True},  # Claims inverted: lower = better
    "PAYEMS": {"weight": 0.20, "inverted": False},
    "USSLIND": {"weight": 0.15, "inverted": False},
    "UNRATE": {"weight": 0.10, "inverted": True},  # Lower unemployment = better
    "A191RL1Q225SBEA": {"weight": 0.15, "inverted": False},
}

# Inflation indicators and their weights
INFLATION_INDICATORS = {
    "CPIAUCSL": {"weight": 0.20, "inverted": False},
    "CPILFESL": {"weight": 0.20, "inverted": False},
    "PCEPI": {"weight": 0.15, "inverted": False},
    "PCEPILFE": {"weight": 0.15, "inverted": False},
    "T5YIE": {"weight": 0.15, "inverted": False},
    "CL": {"weight": 0.10, "inverted": False},  # Oil as inflation proxy
    "HG": {"weight": 0.05, "inverted": False},  # Copper as inflation proxy
}

REGIME_LABELS = {
    (True, False): "goldilocks",    # Growth up, inflation down
    (True, True): "reflation",      # Growth up, inflation up
    (False, False): "deflation",    # Growth down, inflation down
    (False, True): "stagflation",   # Growth down, inflation up
}


async def _get_latest_zscore(db: AsyncSession, series_id: str, as_of: date) -> float | None:
    """Get the most recent z-score for an indicator on or before as_of."""
    result = await db.execute(
        select(IndicatorValue.z_score)
        .join(Indicator)
        .where(
            and_(
                Indicator.series_id == series_id,
                IndicatorValue.date <= as_of,
                IndicatorValue.z_score.isnot(None),
            )
        )
        .order_by(IndicatorValue.date.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    return row


def _compute_momentum(z_scores: dict[str, float], config: dict) -> float:
    """Compute weighted momentum score from z-scores. Returns -1 to +1."""
    total_weight = 0.0
    weighted_sum = 0.0

    for series_id, cfg in config.items():
        z = z_scores.get(series_id)
        if z is None:
            continue
        if cfg["inverted"]:
            z = -z
        weighted_sum += z * cfg["weight"]
        total_weight += cfg["weight"]

    if total_weight == 0:
        return 0.0

    raw = weighted_sum / total_weight
    # Clamp to [-1, 1] using tanh-like compression
    return float(np.clip(raw / 2.0, -1.0, 1.0))


async def compute_regime(db: AsyncSession, as_of: date | None = None) -> RegimeSnapshot | None:
    """Compute the regime classification for a given date."""
    if as_of is None:
        as_of = date.today()

    # Gather z-scores for growth indicators
    growth_zscores = {}
    for series_id in GROWTH_INDICATORS:
        z = await _get_latest_zscore(db, series_id, as_of)
        if z is not None:
            growth_zscores[series_id] = z

    # Gather z-scores for inflation indicators
    inflation_zscores = {}
    for series_id in INFLATION_INDICATORS:
        z = await _get_latest_zscore(db, series_id, as_of)
        if z is not None:
            inflation_zscores[series_id] = z

    if not growth_zscores and not inflation_zscores:
        logger.warning("No z-scores available for regime computation")
        return None

    growth_score = _compute_momentum(growth_zscores, GROWTH_INDICATORS)
    inflation_score = _compute_momentum(inflation_zscores, INFLATION_INDICATORS)

    # Classify quadrant
    growth_up = growth_score > 0
    inflation_up = inflation_score > 0
    regime = REGIME_LABELS[(growth_up, inflation_up)]

    # Confidence: how far from the axes (0,0) we are
    distance = float(np.sqrt(growth_score**2 + inflation_score**2))
    confidence = min(distance / 1.0, 1.0)  # Normalize to 0-1

    # Create snapshot
    snapshot = RegimeSnapshot(
        date=as_of,
        regime=regime,
        growth_score=round(growth_score, 4),
        inflation_score=round(inflation_score, 4),
        confidence=round(confidence, 4),
        composite_score=0.0,  # Will be set by scoring engine
        component_scores={
            "growth_inputs": {k: round(v, 4) for k, v in growth_zscores.items()},
            "inflation_inputs": {k: round(v, 4) for k, v in inflation_zscores.items()},
        },
    )

    return snapshot
