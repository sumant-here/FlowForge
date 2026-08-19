from typing import List
from datetime import datetime, timezone, timedelta
from croniter import croniter
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schedule import Schedule
from app.schemas.job import JobCreate
from app.repositories.schedule_repo import ScheduleRepository
from app.services.job_service import JobService

class SchedulerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.schedule_repo = ScheduleRepository(db)
        self.job_service = JobService(db)

    async def process_due_schedules(self) -> List[str]:
        due = await self.schedule_repo.get_due_schedules()
        triggered_job_ids = []

        now = datetime.now(timezone.utc)
        for s in due:
            job_in = JobCreate(
                name=f"Schedule: {s.name}",
                job_type=s.job_type,
                priority=s.priority,
                payload=s.payload
            )
            job = await self.job_service.submit_job(job_in)
            triggered_job_ids.append(job.id)

            s.total_runs += 1
            s.last_run_at = now

            if s.cron_expression:
                itr = croniter(s.cron_expression, now)
                s.next_run_at = itr.get_next(datetime)
            elif s.interval_seconds:
                s.next_run_at = now + timedelta(seconds=s.interval_seconds)
            else:
                s.is_active = False

        if due:
            await self.db.commit()

        return triggered_job_ids
