import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from app.core.database import Base

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False)
    cron_expression = Column(String(64), nullable=True)
    interval_seconds = Column(Integer, nullable=True)
    
    job_type = Column(String(64), nullable=False)
    priority = Column(String(32), default="NORMAL")
    payload = Column(JSON, default=dict)
    
    is_active = Column(Boolean, default=True, index=True)
    total_runs = Column(Integer, default=0)
    
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
