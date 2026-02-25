from sqlalchemy import Column, DateTime, Integer, String, func

from app.models import Base


class FetchLog(Base):
    __tablename__ = "fetch_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String, nullable=False)
    series_id = Column(String, nullable=True)
    status = Column(String, nullable=False)  # "success", "error", "partial"
    records_added = Column(Integer, default=0)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
