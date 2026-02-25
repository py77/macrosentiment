from sqlalchemy import Column, Date, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models import Base


class IndicatorValue(Base):
    __tablename__ = "indicator_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    value = Column(Float, nullable=False)
    z_score = Column(Float)
    percentile = Column(Float)

    indicator = relationship("Indicator", back_populates="values")

    __table_args__ = (
        UniqueConstraint("indicator_id", "date", name="uq_indicator_date"),
    )
