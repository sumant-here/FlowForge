from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.worker import WorkerResponse, WorkerHeartbeat
from app.services.worker_service import WorkerService
from app.websocket.event_publisher import event_publisher

router = APIRouter(prefix="/workers", tags=["Workers"])

@router.get("", response_model=List[WorkerResponse])
async def list_workers(db: AsyncSession = Depends(get_db)):
    service = WorkerService(db)
    workers = await service.list_workers()
    return [WorkerResponse.model_validate(w) for w in workers]

@router.post("/heartbeat", response_model=WorkerResponse)
async def worker_heartbeat(data: WorkerHeartbeat, db: AsyncSession = Depends(get_db)):
    service = WorkerService(db)
    w = await service.process_heartbeat(data)
    await event_publisher.publish("WORKER_HEARTBEAT", {
        "worker_id": w.id,
        "status": w.status.value,
        "cpu_usage": w.cpu_usage,
        "memory_usage": w.memory_usage,
        "current_job_id": w.current_job_id
    })
    return WorkerResponse.model_validate(w)

@router.post("/{worker_id}/drain", response_model=WorkerResponse)
async def drain_worker(worker_id: str, db: AsyncSession = Depends(get_db)):
    service = WorkerService(db)
    w = await service.drain_worker(worker_id)
    if not w:
        raise HTTPException(status_code=404, detail="Worker not found")
    return WorkerResponse.model_validate(w)
