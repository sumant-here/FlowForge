import pytest
from app.core.database import AsyncSessionLocal
from app.services.job_service import JobService
from app.schemas.job import JobCreate
from app.models.job import JobStatus, JobPriority

@pytest.mark.asyncio
async def test_job_submission_and_state():
    async with AsyncSessionLocal() as session:
        job_service = JobService(session)
        
        job_in = JobCreate(
            name="Unit Test Prime Computation",
            job_type="cpu_intensive",
            priority=JobPriority.CRITICAL,
            payload={"limit": 5000}
        )
        job = await job_service.submit_job(job_in)
        assert job.id is not None
        assert job.status == JobStatus.QUEUED
        assert job.priority == JobPriority.CRITICAL

        # Cancel job
        cancelled = await job_service.cancel_job(job.id)
        assert cancelled.status == JobStatus.CANCELLED
