from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.dead_letter import DeadLetterJob
from app.services.dlq_service import DLQService
from app.schemas.job import JobResponse

router = APIRouter(prefix="/dlq", tags=["Dead Letter Queue"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_dead_letter_jobs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    service = DLQService(db)
    skip = (page - 1) * limit
    jobs = await service.dlq_repo.list_unresolved(skip=skip, limit=limit)
    return [
        {
            "id": j.id,
            "original_job_id": j.original_job_id,
            "job_name": j.job_name,
            "job_type": j.job_type,
            "queue_name": j.queue_name,
            "failure_reason": j.failure_reason,
            "stack_trace": j.stack_trace,
            "payload": j.payload,
            "attempts_count": j.attempts_count,
            "moved_to_dlq_at": j.moved_to_dlq_at.isoformat() if j.moved_to_dlq_at else None,
            "status": j.status.value
        }
        for j in jobs
    ]

@router.post("/{dlq_id}/replay", response_model=JobResponse)
async def replay_dlq_job(dlq_id: str, db: AsyncSession = Depends(get_db)):
    service = DLQService(db)
    replayed = await service.replay_job(dlq_id)
    return JobResponse.model_validate(replayed)

@router.delete("/purge", response_model=Dict[str, Any])
async def purge_dlq(db: AsyncSession = Depends(get_db)):
    service = DLQService(db)
    count = await service.purge()
    return {"status": "PURGED", "purged_count": count}
