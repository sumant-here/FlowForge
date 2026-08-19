from typing import Dict, Any, List
from fastapi import APIRouter
from app.core.broker import broker
from app.schemas.queue import QueueStatsResponse, QueueInfo

router = APIRouter(prefix="/queues", tags=["Queues"])

@router.get("", response_model=QueueStatsResponse)
async def get_queue_stats():
    stats_dict = broker.get_queue_stats()
    queue_list = []
    total_depth = 0
    total_processed = 0

    for qname, qdata in stats_dict.items():
        q_info = QueueInfo(
            name=qname,
            depth=qdata["depth"],
            enqueued=qdata["enqueued"],
            processed=qdata["processed"],
            failed=qdata["failed"],
            consumers=qdata["consumers"]
        )
        queue_list.append(q_info)
        total_depth += qdata["depth"]
        total_processed += qdata["processed"]

    return QueueStatsResponse(
        queues=queue_list,
        total_depth=total_depth,
        total_processed=total_processed
    )
