import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dead_letter import DeadLetterJob, DLQStatus
from app.models.job import Job
from app.repositories.dlq_repo import DLQRepository
from app.repositories.job_repo import JobRepository
from app.services.job_service import JobService

class DLQService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dlq_repo = DLQRepository(db)
        self.job_repo = JobRepository(db)
        self.job_service = JobService(db)

    async def add_to_dlq(self, job: Job, failure_reason: str, stack_trace: str) -> DeadLetterJob:
        dlq_entry = DeadLetterJob(
            id=str(uuid.uuid4()),
            original_job_id=job.id,
            job_name=job.name,
            job_type=job.job_type,
            queue_name=job.queue_name,
            failure_reason=failure_reason,
            stack_trace=stack_trace,
            payload=job.payload,
            attempts_count=job.retry_count,
            moved_to_dlq_at=datetime.now(timezone.utc),
            status=DLQStatus.UNRESOLVED
        )
        return await self.dlq_repo.create(dlq_entry)

    async def replay_job(self, dlq_id: str) -> Job:
        dlq_job = await self.dlq_repo.get(dlq_id)
        if not dlq_job:
            raise Exception("Dead Letter Job not found")
        
        job = await self.job_service.retry_job(dlq_job.original_job_id)
        dlq_job.status = DLQStatus.REPLAYED
        dlq_job.replayed_at = datetime.now(timezone.utc)
        await self.db.commit()
        return job

    async def purge(self) -> int:
        return await self.dlq_repo.purge_all()
