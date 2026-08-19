from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.job import JobCreate, JobResponse, JobDetailResponse
from app.services.job_service import JobService
from app.websocket.event_publisher import event_publisher

router = APIRouter(prefix="/jobs", tags=["Jobs"])

@router.post("", response_model=JobResponse)
async def create_job(data: JobCreate, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.submit_job(data)
    await event_publisher.publish("JOB_CREATED", {
        "job_id": job.id,
        "name": job.name,
        "job_type": job.job_type,
        "priority": job.priority.value,
        "status": job.status.value,
        "queue_name": job.queue_name
    })
    return JobResponse.model_validate(job)

@router.get("", response_model=Dict[str, Any])
async def list_jobs(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    workflow_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    service = JobService(db)
    skip = (page - 1) * limit
    jobs, total = await service.list_jobs(
        status=status,
        priority=priority,
        job_type=job_type,
        workflow_id=workflow_id,
        search=search,
        skip=skip,
        limit=limit
    )
    return {
        "items": [JobResponse.model_validate(j) for j in jobs],
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit if total else 1
    }

@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job_detail(job_id: str, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.get_job_detail(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobDetailResponse.model_validate(job)

@router.post("/{job_id}/retry", response_model=JobResponse)
async def retry_job(job_id: str, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.retry_job(job_id)
    await event_publisher.publish("JOB_RETRYING", {"job_id": job.id, "status": job.status.value})
    return JobResponse.model_validate(job)

@router.post("/{job_id}/cancel", response_model=JobResponse)
async def cancel_job(job_id: str, db: AsyncSession = Depends(get_db)):
    service = JobService(db)
    job = await service.cancel_job(job_id)
    await event_publisher.publish("JOB_CANCELLED", {"job_id": job.id, "status": job.status.value})
    return JobResponse.model_validate(job)
