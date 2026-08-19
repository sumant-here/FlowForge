from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum as SQLEnum
from app.core.database import Base

class WorkerStatus(str, Enum):
    STARTING = "STARTING"
    IDLE = "IDLE"
    BUSY = "BUSY"
    UNHEALTHY = "UNHEALTHY"
    DRAINING = "DRAINING"
    OFFLINE = "OFFLINE"

class Worker(Base):
    __tablename__ = "workers"

    id = Column(String(64), primary_key=True, index=True)
    hostname = Column(String(255), nullable=False)
    ip_address = Column(String(64), default="127.0.0.1")
    status = Column(SQLEnum(WorkerStatus), default=WorkerStatus.IDLE, index=True)
    current_job_id = Column(String(36), nullable=True)
    
    jobs_processed = Column(Integer, default=0)
    jobs_succeeded = Column(Integer, default=0)
    jobs_failed = Column(Integer, default=0)
    
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    concurrency = Column(Integer, default=4)
    
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_heartbeat = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    tags = Column(JSON, default=list)
