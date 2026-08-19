import psutil
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.job_repo import JobRepository
from app.repositories.worker_repo import WorkerRepository
from app.repositories.workflow_repo import WorkflowRepository
from app.core.broker import broker
from app.models.worker import WorkerStatus

router = APIRouter(prefix="/metrics", tags=["Metrics & Telemetry"])

@router.get("/summary")
async def get_dashboard_metrics(db: AsyncSession = Depends(get_db)):
    job_repo = JobRepository(db)
    worker_repo = WorkerRepository(db)
    wf_repo = WorkflowRepository(db)

    counts = await job_repo.get_counts_by_status()
    workers = await worker_repo.list()
    active_workers = [w for w in workers if w.status != WorkerStatus.OFFLINE]
    workflows = await wf_repo.list()
    queue_stats = broker.get_queue_stats()

    total_jobs = sum(counts.values())
    cpu_percent = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent

    return {
        "total_jobs": total_jobs,
        "running_jobs": counts.get("RUNNING", 0),
        "queued_jobs": counts.get("QUEUED", 0),
        "succeeded_jobs": counts.get("SUCCEEDED", 0),
        "failed_jobs": counts.get("FAILED", 0),
        "retrying_jobs": counts.get("RETRYING", 0),
        "dead_lettered_jobs": counts.get("DEAD_LETTERED", 0),
        "active_workers": len(active_workers),
        "total_workers": len(workers),
        "total_workflows": len(workflows),
        "host_cpu_percent": cpu_percent,
        "host_memory_percent": mem,
        "queues": [
            {"name": k, "depth": v["depth"], "processed": v["processed"], "failed": v["failed"]}
            for k, v in queue_stats.items()
        ]
    }
