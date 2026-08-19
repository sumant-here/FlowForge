from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.worker import WorkerStatus

class WorkerHeartbeat(BaseModel):
    worker_id: str
    hostname: str
    ip_address: str = "127.0.0.1"
    status: WorkerStatus = WorkerStatus.IDLE
    current_job_id: Optional[str] = None
    jobs_processed: int = 0
    jobs_succeeded: int = 0
    jobs_failed: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    concurrency: int = 4
    tags: List[str] = Field(default_factory=list)

class WorkerResponse(BaseModel):
    id: str
    hostname: str
    ip_address: str
    status: WorkerStatus
    current_job_id: Optional[str] = None
    jobs_processed: int
    jobs_succeeded: int
    jobs_failed: int
    cpu_usage: float
    memory_usage: float
    concurrency: int
    started_at: datetime
    last_heartbeat: datetime
    tags: List[str] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)