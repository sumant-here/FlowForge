import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Enum as SQLEnum
from app.core.database import Base

class DLQStatus(str, Enum):
    UNRESOLVED = "UNRESOLVED"
    REPLAYED = "REPLAYED"
    PURGED = "PURGED"

class DeadLetterJob(Base):
    __tablename__ = "dead_letter_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    original_job_id = Column(String(36), nullable=False, index=True)
    job_name = Column(String(255), nullable=False)
    job_type = Column(String(64), nullable=False)
    queue_name = Column(String(64), default="queue.normal")
    
    failure_reason = Column(Text, nullable=True)
    stack_trace = Column(Text, nullable=True)
    payload = Column(JSON, default=dict)
    attempts_count = Column(Integer, default=3)
    
    moved_to_dlq_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    replayed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(DLQStatus), default=DLQStatus.UNRESOLVED, index=True)
