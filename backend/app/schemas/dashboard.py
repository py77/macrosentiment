from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.indicator import IndicatorOut
from app.schemas.regime import RegimeOut


class CategorySummary(BaseModel):
    name: str
    signal: str  # "bullish", "bearish", "neutral"
    score: float
    key_indicators: list[IndicatorOut]


class DashboardOut(BaseModel):
    last_updated: Optional[datetime] = None
    regime: Optional[RegimeOut] = None
    composite_score: float = 0.0
    categories: list[CategorySummary] = []
    indicators: list[IndicatorOut] = []


class FetchStatusOut(BaseModel):
    source: str
    last_fetch: Optional[datetime] = None
    status: Optional[str] = None
    records_added: int = 0
    error_message: Optional[str] = None


class FetchTriggerOut(BaseModel):
    status: str
    message: str
    sources_fetched: list[str] = []
