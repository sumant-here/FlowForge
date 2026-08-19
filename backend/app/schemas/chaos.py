from typing import Optional, Dict, Any
from pydantic import BaseModel

class ChaosActionRequest(BaseModel):
    action: str # kill_worker, delay_worker, force_job_failure, flood_queue, simulate_broker_disconnect
    target_worker_id: Optional[str] = None
    target_job_id: Optional[str] = None
    delay_seconds: Optional[int] = 5
    job_count: Optional[int] = 50

class ChaosSimulationStatus(BaseModel):
    active_experiments: int
    last_action: Optional[str] = None
    message: str
    impact: Dict[str, Any] = {}
