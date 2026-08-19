import random
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.worker import WorkerStatus
from app.models.job import JobPriority
from app.schemas.job import JobCreate
from app.repositories.worker_repo import WorkerRepository
from app.services.job_service import JobService

class ChaosService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.worker_repo = WorkerRepository(db)
        self.job_service = JobService(db)

    async def execute_chaos(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == "kill_worker":
            worker_id = params.get("target_worker_id")
            workers = await self.worker_repo.list()
            target = None
            if worker_id:
                target = await self.worker_repo.get(worker_id)
            elif workers:
                target = random.choice([w for w in workers if w.status != WorkerStatus.OFFLINE] or workers)

            if target:
                target.status = WorkerStatus.OFFLINE
                await self.db.commit()
                return {
                    "action": "kill_worker",
                    "impact": f"Worker '{target.id}' ({target.hostname}) killed. Active job will be auto-recovered.",
                    "worker_id": target.id
                }
            return {"action": "kill_worker", "impact": "No active workers available."}

        elif action == "force_job_failure":
            job_in = JobCreate(
                name="[Chaos Lab] Force Failure & Retry Stress",
                job_type="failure_simulation",
                priority=JobPriority.HIGH,
                payload={"fail_until_attempt": 3, "always_fail": False},
                max_retries=3,
                base_delay_seconds=2
            )
            job = await self.job_service.submit_job(job_in)
            return {
                "action": "force_job_failure",
                "impact": f"Submitted failure job '{job.id}'.",
                "job_id": job.id
            }

        elif action == "flood_queue":
            count = params.get("job_count", 30)
            priorities = [JobPriority.CRITICAL, JobPriority.HIGH, JobPriority.NORMAL, JobPriority.LOW]
            for i in range(count):
                p = random.choice(priorities)
                job_in = JobCreate(
                    name=f"[Chaos Flood #{i+1}] Stress Job",
                    job_type=random.choice(["cpu_intensive", "io_simulation", "data_processing"]),
                    priority=p,
                    payload={"limit": 5000, "latency_seconds": 0.3}
                )
                await self.job_service.submit_job(job_in)
            return {
                "action": "flood_queue",
                "impact": f"Flooded queues with {count} concurrent priority jobs.",
                "enqueued_count": count
            }

        return {"action": action, "impact": "Chaos action simulated."}
