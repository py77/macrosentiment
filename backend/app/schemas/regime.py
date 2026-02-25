from datetime import date
from typing import Optional

from pydantic import BaseModel


class RegimeOut(BaseModel):
    date: date
    regime: str
    growth_score: float
    inflation_score: float
    confidence: float
    composite_score: float
    component_scores: dict

    model_config = {"from_attributes": True}


class RegimeHistoryOut(BaseModel):
    snapshots: list[RegimeOut]
