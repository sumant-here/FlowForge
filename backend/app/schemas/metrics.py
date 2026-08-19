from typing import Dict, Any, List
from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_jobs: int
    running_jobs: int
    queued_jobs: int
    succeeded_jobs: int
    failed_jobs: int
    retrying_jobs: int
    dead_lettered_jobs: int
    active_workers: int
    total_workflows: int
    system_throughput_rps: float
    avg_duration_ms: float
    queues: List[Dict[str, Any]]
