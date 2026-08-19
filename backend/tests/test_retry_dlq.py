import pytest
from app.engine.retry_policy import RetryPolicy
from app.core.exceptions import NonRetryableJobError, JobExecutionError
from app.core.database import AsyncSessionLocal
from app.services.job_service import JobService
from app.services.dlq_service import DLQService
from app.schemas.job import JobCreate
from app.models.job import JobPriority, JobStatus
from app.models.dead_letter import DLQStatus

def test_exponential_backoff_calculation():
    delay1 = RetryPolicy.calculate_delay(attempt=1, strategy="exponential", base_delay_seconds=2, jitter=False)
    delay2 = RetryPolicy.calculate_delay(attempt=2, strategy="exponential", base_delay_seconds=2, jitter=False)
    delay3 = RetryPolicy.calculate_delay(attempt=3, strategy="exponential", base_delay_seconds=2, jitter=False)
    
    assert delay1 == 2
    assert delay2 == 4
    assert delay3 == 8

def test_retryable_classification():
    assert RetryPolicy.is_retryable(JobExecutionError("Timeout")) is True
    assert RetryPolicy.is_retryable(NonRetryableJobError("Fatal memory crash")) is False

@pytest.mark.asyncio
async def test_dlq_add_and_replay():
    async with AsyncSessionLocal() as session:
        job_service = JobService(session)
        dlq_service = DLQService(session)

        job_in = JobCreate(
            name="DLQ Test Job",
            job_type="failure_simulation",
            priority=JobPriority.NORMAL,
            payload={"always_fail": True}
        )
        job = await job_service.submit_job(job_in)

        # Move to DLQ
        dlq_entry = await dlq_service.add_to_dlq(job, "Retry limit exceeded", "Traceback...")
        assert dlq_entry.id is not None
        assert dlq_entry.status == DLQStatus.UNRESOLVED

        # Replay from DLQ
        replayed_job = await dlq_service.replay_job(dlq_entry.id)
        assert replayed_job.status == JobStatus.QUEUED
        assert dlq_entry.status == DLQStatus.REPLAYED
