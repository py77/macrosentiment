from sqlalchemy import Boolean, Column, Float, Integer, String
from sqlalchemy.orm import relationship

from app.models import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, autoincrement=True)
    series_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, index=True)
    source = Column(String, nullable=False)  # "fred", "ibkr", "manual"
    frequency = Column(String, nullable=False, default="daily")
    weight = Column(Float, nullable=False, default=1.0)
    higher_is_bullish = Column(Boolean, nullable=False, default=True)
    unit = Column(String, default="")
    description = Column(String, default="")

    values = relationship("IndicatorValue", back_populates="indicator", cascade="all, delete-orphan")
