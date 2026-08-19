from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ScheduleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    cron_expression: Optional[str] = None # e.g. "*/5 * * * *"
    interval_seconds: Optional[int] = None # e.g. 60
    job_type: str = "report_generator"
    priority: str = "NORMAL"
    payload: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class ScheduleUpdate(BaseModel):
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class ScheduleResponse(BaseModel):
    id: str
    name: str
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    job_type: str
    priority: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool
    total_runs: int
    last_run_at: Optional[datetime] = None
    next_run_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
