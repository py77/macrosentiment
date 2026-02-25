from datetime import date
from typing import Optional

from pydantic import BaseModel


class IndicatorBase(BaseModel):
    series_id: str
    name: str
    category: str
    source: str
    frequency: str = "daily"
    weight: float = 1.0
    higher_is_bullish: bool = True
    unit: str = ""
    description: str = ""


class IndicatorOut(IndicatorBase):
    id: int
    latest_value: Optional[float] = None
    latest_date: Optional[date] = None
    z_score: Optional[float] = None
    percentile: Optional[float] = None
    change_1d: Optional[float] = None
    change_1w: Optional[float] = None
    change_1m: Optional[float] = None
    signal: Optional[str] = None  # "bullish", "bearish", "neutral"
    sparkline: list[float] = []

    model_config = {"from_attributes": True}


class IndicatorValueOut(BaseModel):
    date: date
    value: float
    z_score: Optional[float] = None
    percentile: Optional[float] = None

    model_config = {"from_attributes": True}


class IndicatorHistoryOut(BaseModel):
    series_id: str
    name: str
    category: str
    values: list[IndicatorValueOut]


