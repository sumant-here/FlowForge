from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.worker import Worker, WorkerStatus
from app.models.job import Job, JobStatus
from app.models.job_log import JobLog
from app.schemas.worker import WorkerHeartbeat
from app.repositories.worker_repo import WorkerRepository
from app.repositories.job_repo import JobRepository
from app.core.broker import broker, Priority

class WorkerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.worker_repo = WorkerRepository(db)
        self.job_repo = JobRepository(db)

    async def process_heartbeat(self, heartbeat: WorkerHeartbeat) -> Worker:
        return await self.worker_repo.upsert_heartbeat(heartbeat.model_dump())

    async def list_workers(self) -> List[Worker]:
        return await self.worker_repo.list(skip=0, limit=100)

    async def drain_worker(self, worker_id: str) -> Optional[Worker]:
        worker = await self.worker_repo.get(worker_id)
        if worker:
            worker.status = WorkerStatus.DRAINING
            await self.db.commit()
            await self.db.refresh(worker)
        return worker

    async def detect_and_recover_stale_workers(self, timeout_seconds: int = 15) -> List[str]:
        stale_workers = await self.worker_repo.find_stale_workers(timeout_seconds=timeout_seconds)
        recovered_job_ids = []

        for w in stale_workers:
            w.status = WorkerStatus.OFFLINE
            if w.current_job_id:
                job = await self.job_repo.get(w.current_job_id)
                if job and job.status == JobStatus.RUNNING:
                    job.status = JobStatus.QUEUED
                    job.worker_id = None
                    recovered_job_ids.append(job.id)
                    
                    await self.job_repo.add_log(JobLog(
                        job_id=job.id,
                        level="WARN",
                        message=f"Worker {w.id} timed out. Job auto-recovered and requeued."
                    ))

                    msg_payload = {
                        "job_id": job.id,
                        "name": job.name,
                        "job_type": job.job_type,
                        "payload": job.payload,
                        "max_retries": job.max_retries,
                        "retry_count": job.retry_count,
                        "base_delay_seconds": job.base_delay_seconds,
                        "retry_backoff": job.retry_backoff,
                        "timeout_seconds": job.timeout_seconds,
                        "workflow_id": job.workflow_id,
                        "node_id": job.node_id
                    }
                    await broker.publish_job(
                        queue_name=job.queue_name,
                        payload=msg_payload,
                        priority=Priority(job.priority.value)
                    )

                w.current_job_id = None

        if stale_workers:
            await self.db.commit()

        return recovered_job_ids
