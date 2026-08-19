import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.broker import broker, Priority
from app.core.exceptions import FlowForgeException
from app.engine.state_machine import StateMachine
from app.models.job import Job, JobStatus, JobPriority
from app.models.job_log import JobLog
from app.schemas.job import JobCreate
from app.repositories.job_repo import JobRepository

class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)

    async def submit_job(self, data: JobCreate, workflow_id: Optional[str] = None, node_id: Optional[str] = None) -> Job:
        prio_enum = data.priority
        queue_mapping = {
            JobPriority.CRITICAL: "queue.critical",
            JobPriority.HIGH: "queue.high",
            JobPriority.NORMAL: "queue.normal",
            JobPriority.LOW: "queue.low"
        }
        target_queue = data.queue_name or queue_mapping.get(prio_enum, "queue.normal")

        job = Job(
            id=str(uuid.uuid4()),
            name=data.name,
            job_type=data.job_type,
            priority=prio_enum,
            status=JobStatus.QUEUED,
            payload=data.payload,
            max_retries=data.max_retries,
            retry_backoff=data.retry_backoff,
            base_delay_seconds=data.base_delay_seconds,
            timeout_seconds=data.timeout_seconds,
            queue_name=target_queue,
            workflow_id=workflow_id,
            node_id=node_id,
            scheduled_for=data.scheduled_for,
            created_at=datetime.now(timezone.utc)
        )
        saved = await self.job_repo.create(job)

        await self.job_repo.add_log(JobLog(
            job_id=saved.id,
            level="INFO",
            message=f"Job enqueued into {target_queue} (Priority: {prio_enum.value})"
        ))

        msg_payload = {
            "job_id": saved.id,
            "name": saved.name,
            "job_type": saved.job_type,
            "payload": saved.payload,
            "max_retries": saved.max_retries,
            "retry_count": saved.retry_count,
            "base_delay_seconds": saved.base_delay_seconds,
            "retry_backoff": saved.retry_backoff,
            "timeout_seconds": saved.timeout_seconds,
            "workflow_id": workflow_id,
            "node_id": node_id
        }
        await broker.publish_job(
            queue_name=target_queue,
            payload=msg_payload,
            priority=Priority(prio_enum.value)
        )
        return saved

    async def retry_job(self, job_id: str) -> Job:
        job = await self.job_repo.get(job_id)
        if not job:
            raise FlowForgeException("Job not found", status_code=404)
        
        StateMachine.validate_job_transition(job.status, JobStatus.QUEUED)
        job.status = JobStatus.QUEUED
        job.error = None
        await self.db.commit()
        await self.db.refresh(job)

        await self.job_repo.add_log(JobLog(
            job_id=job.id,
            level="INFO",
            message=f"Retry requested for job {job.id}"
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
        return job

    async def cancel_job(self, job_id: str) -> Job:
        job = await self.job_repo.get(job_id)
        if not job:
            raise FlowForgeException("Job not found", status_code=404)
        
        StateMachine.validate_job_transition(job.status, JobStatus.CANCELLED)
        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(job)

        await self.job_repo.add_log(JobLog(
            job_id=job.id,
            level="WARN",
            message=f"Job {job.id} cancelled by user"
        ))
        return job

    async def list_jobs(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        job_type: Optional[str] = None,
        workflow_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Job], int]:
        return await self.job_repo.list_filtered(
            status=status,
            priority=priority,
            job_type=job_type,
            workflow_id=workflow_id,
            search=search,
            skip=skip,
            limit=limit
        )

    async def get_job_detail(self, job_id: str) -> Optional[Job]:
        return await self.job_repo.get_detail(job_id)
