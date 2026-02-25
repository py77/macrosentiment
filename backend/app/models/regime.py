from sqlalchemy import Column, Date, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.models import Base


class RegimeSnapshot(Base):
    __tablename__ = "regime_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    regime = Column(String, nullable=False)  # goldilocks, reflation, deflation, stagflation
    growth_score = Column(Float, nullable=False)
    inflation_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    composite_score = Column(Float, nullable=False)
    component_scores = Column(JSONB, default={})
