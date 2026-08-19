from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.job import JobStatus, JobPriority, JobType

class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    job_type: str = Field(default="cpu_intensive")
    priority: JobPriority = Field(default=JobPriority.NORMAL)
    payload: Dict[str, Any] = Field(default_factory=dict)
    max_retries: int = Field(default=3, ge=0, le=10)
    retry_backoff: str = Field(default="exponential")
    base_delay_seconds: int = Field(default=2, ge=0, le=300)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)
    queue_name: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class JobUpdate(BaseModel):
    priority: Optional[JobPriority] = None
    max_retries: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None

class JobAttemptResponse(BaseModel):
    id: str
    attempt_number: int
    worker_id: Optional[str] = None
    status: str
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

class JobLogResponse(BaseModel):
    id: str
    level: str
    message: str
    timestamp: datetime
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(from_attributes=True)

class JobResponse(BaseModel):
    id: str
    name: str
    job_type: str
    priority: JobPriority
    status: JobStatus
    payload: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int
    max_retries: int
    retry_backoff: str
    queue_name: str
    worker_id: Optional[str] = None
    workflow_id: Optional[str] = None
    node_id: Optional[str] = None
    created_at: datetime
    scheduled_for: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_duration_ms: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class JobDetailResponse(JobResponse):
    attempts: List[JobAttemptResponse] = []
    logs: List[JobLogResponse] = []