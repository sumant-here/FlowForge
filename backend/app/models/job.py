import uuid
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

class JobStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"
    DEAD_LETTERED = "DEAD_LETTERED"

class JobPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

class JobType(str, Enum):
    CPU = "cpu_intensive"
    IO = "io_simulation"
    DATA_PROCESSING = "data_processing"
    IMAGE_TRANSFORMATION = "image_transformation"
    REPORT_GENERATOR = "report_generator"
    FAILURE_SIMULATION = "failure_simulation"
    SLEEP_DELAY = "sleep_delay"
    CUSTOM = "custom"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False, index=True)
    job_type = Column(String(64), nullable=False, default="cpu_intensive", index=True)
    priority = Column(SQLEnum(JobPriority), default=JobPriority.NORMAL, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, index=True)
    
    payload = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_backoff = Column(String(32), default="exponential")
    base_delay_seconds = Column(Integer, default=2)
    timeout_seconds = Column(Integer, default=300)
    
    queue_name = Column(String(64), default="queue.normal", index=True)
    worker_id = Column(String(64), nullable=True, index=True)
    workflow_id = Column(String(36), nullable=True, index=True)
    node_id = Column(String(64), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_duration_ms = Column(Integer, nullable=True)
    
    attempts = relationship("JobAttempt", back_populates="job", cascade="all, delete-orphan")
    logs = relationship("JobLog", back_populates="job", cascade="all, delete-orphan")
