from typing import List, Dict, Any
from pydantic import BaseModel

class QueueInfo(BaseModel):
    name: str
    depth: int
    enqueued: int
    processed: int
    failed: int
    consumers: int

class QueueStatsResponse(BaseModel):
    queues: List[QueueInfo]
    total_depth: int
    total_processed: int
