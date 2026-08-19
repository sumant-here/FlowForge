import sys
import os
import time
import traceback
import asyncio
from datetime import datetime, timezone

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.core.database import AsyncSessionLocal
from app.models.job import Job, JobStatus
from app.models.job_attempt import JobAttempt
from app.models.job_log import JobLog
from app.repositories.job_repo import JobRepository
from app.engine.task_registry import task_registry
from app.engine.retry_policy import RetryPolicy
from app.engine.state_machine import StateMachine
from app.services.dlq_service import DLQService
from app.services.workflow_service import WorkflowService
from app.websocket.event_publisher import event_publisher
from app.core.broker import broker, Priority

class JobRunner:
    @staticmethod
    async def execute_job(msg_payload: dict, worker_id: str):
        job_id = msg_payload["job_id"]
        
        async with AsyncSessionLocal() as session:
            job_repo = JobRepository(session)
            workflow_svc = WorkflowService(session)
            dlq_svc = DLQService(session)
            
            job = await job_repo.get(job_id)
            if not job or job.status in (JobStatus.CANCELLED, JobStatus.SUCCEEDED):
                return

            # Transition to RUNNING
            StateMachine.validate_job_transition(job.status, JobStatus.RUNNING)
            job.status = JobStatus.RUNNING
            job.worker_id = worker_id
            job.started_at = datetime.now(timezone.utc)
            job.retry_count += 1
            current_attempt_num = job.retry_count
            
            attempt = JobAttempt(
                job_id=job.id,
                attempt_number=current_attempt_num,
                worker_id=worker_id,
                status="RUNNING",
                started_at=datetime.now(timezone.utc)
            )
            await job_repo.create_attempt(attempt)
            await session.commit()

            await event_publisher.publish("JOB_STARTED", {
                "job_id": job.id,
                "worker_id": worker_id,
                "attempt": current_attempt_num,
                "status": "RUNNING"
            })

            # Progress callback
            async def progress_callback(msg: str):
                log_entry = JobLog(job_id=job.id, level="INFO", message=msg)
                await job_repo.add_log(log_entry)
                await event_publisher.publish("JOB_PROGRESS", {
                    "job_id": job.id,
                    "worker_id": worker_id,
                    "progress_message": msg
                })

            start_t = time.time()
            try:
                handler = task_registry.get(job.job_type)
                # Inject current attempt info for failure simulators
                exec_payload = dict(job.payload or {})
                exec_payload["current_attempt"] = current_attempt_num

                result = await asyncio.wait_for(
                    handler(exec_payload, progress_cb=progress_callback),
                    timeout=float(job.timeout_seconds or 300)
                )
                duration_ms = int((time.time() - start_t) * 1000)

                # SUCCESS
                StateMachine.validate_job_transition(job.status, JobStatus.SUCCEEDED)
                job.status = JobStatus.SUCCEEDED
                job.result = result
                job.completed_at = datetime.now(timezone.utc)
                job.execution_duration_ms = duration_ms
                
                attempt.status = "SUCCEEDED"
                attempt.completed_at = datetime.now(timezone.utc)
                attempt.duration_ms = duration_ms

                await job_repo.add_log(JobLog(
                    job_id=job.id,
                    level="INFO",
                    message=f"Job completed successfully in {duration_ms}ms"
                ))
                await session.commit()

                await event_publisher.publish("JOB_SUCCEEDED", {
                    "job_id": job.id,
                    "worker_id": worker_id,
                    "duration_ms": duration_ms,
                    "status": "SUCCEEDED"
                })

                # If part of workflow DAG, trigger downstream steps
                if job.workflow_id and job.node_id:
                    await workflow_svc.handle_job_completed(
                        workflow_id=job.workflow_id,
                        node_id=job.node_id,
                        status="SUCCEEDED",
                        output_data=result
                    )

            except Exception as e:
                duration_ms = int((time.time() - start_t) * 1000)
                err_str = str(e)
                stack_trace = traceback.format_exc()

                attempt.status = "FAILED"
                attempt.error = err_str
                attempt.completed_at = datetime.now(timezone.utc)
                attempt.duration_ms = duration_ms

                is_retryable = RetryPolicy.is_retryable(e)
                has_retries_left = job.retry_count < job.max_retries

                if is_retryable and has_retries_left:
                    # RETRY
                    delay = RetryPolicy.calculate_delay(
                        attempt=job.retry_count,
                        strategy=job.retry_backoff or "exponential",
                        base_delay_seconds=job.base_delay_seconds or 2
                    )
                    job.status = JobStatus.RETRYING
                    job.error = f"Attempt #{job.retry_count} failed: {err_str}"
                    
                    await job_repo.add_log(JobLog(
                        job_id=job.id,
                        level="WARN",
                        message=f"Attempt #{job.retry_count} failed ({err_str}). Retrying in {delay}s..."
                    ))
                    await session.commit()

                    await event_publisher.publish("JOB_RETRYING", {
                        "job_id": job.id,
                        "worker_id": worker_id,
                        "attempt": job.retry_count,
                        "next_retry_delay_s": delay,
                        "status": "RETRYING"
                    })

                    # Re-publish with delay
                    await broker.publish_job(
                        queue_name=job.queue_name,
                        payload=msg_payload,
                        priority=Priority(job.priority.value),
                        delay_seconds=int(delay)
                    )
                else:
                    # DEAD LETTERED / FAILED
                    job.status = JobStatus.DEAD_LETTERED
                    job.error = f"Job failed permanently after {job.retry_count} attempts: {err_str}"
                    job.completed_at = datetime.now(timezone.utc)
                    job.execution_duration_ms = duration_ms

                    await job_repo.add_log(JobLog(
                        job_id=job.id,
                        level="ERROR",
                        message=f"Job exceeded retry limits. Moved to Dead Letter Queue (DLQ). Reason: {err_str}"
                    ))
                    # Insert into DLQ
                    await dlq_svc.add_to_dlq(job, failure_reason=err_str, stack_trace=stack_trace)
                    await session.commit()

                    await event_publisher.publish("JOB_FAILED", {
                        "job_id": job.id,
                        "worker_id": worker_id,
                        "status": "DEAD_LETTERED",
                        "error": err_str
                    })

                    # If part of workflow DAG, notify workflow of failure
                    if job.workflow_id and job.node_id:
                        await workflow_svc.handle_job_completed(
                            workflow_id=job.workflow_id,
                            node_id=job.node_id,
                            status="FAILED",
                            output_data={},
                            error=err_str
                        )
