from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, desc, func
from sqlalchemy.orm import selectinload
from app.models.job import Job, JobStatus, JobPriority
from app.models.job_attempt import JobAttempt
from app.models.job_log import JobLog
from app.repositories.base import BaseRepository

class JobRepository(BaseRepository[Job]):
    def __init__(self, db: AsyncSession):
        super().__init__(Job, db)

    async def get_detail(self, job_id: str) -> Optional[Job]:
        query = (
            select(Job)
            .options(selectinload(Job.attempts), selectinload(Job.logs))
            .where(Job.id == job_id)
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def list_filtered(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        job_type: Optional[str] = None,
        workflow_id: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Job], int]:
        query = select(Job)
        count_query = select(func.count(Job.id))

        if status:
            query = query.where(Job.status == status)
            count_query = count_query.where(Job.status == status)
        if priority:
            query = query.where(Job.priority == priority)
            count_query = count_query.where(Job.priority == priority)
        if job_type:
            query = query.where(Job.job_type == job_type)
            count_query = count_query.where(Job.job_type == job_type)
        if workflow_id:
            query = query.where(Job.workflow_id == workflow_id)
            count_query = count_query.where(Job.workflow_id == workflow_id)
        if search:
            query = query.where(Job.name.ilike(f"%{search}%"))
            count_query = count_query.where(Job.name.ilike(f"%{search}%"))

        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        query = query.order_by(desc(Job.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def create_attempt(self, attempt: JobAttempt) -> JobAttempt:
        self.db.add(attempt)
        await self.db.commit()
        await self.db.refresh(attempt)
        return attempt

    async def add_log(self, log: JobLog) -> JobLog:
        self.db.add(log)
        await self.db.commit()
        return log

    async def get_counts_by_status(self) -> Dict[str, int]:
        query = select(Job.status, func.count(Job.id)).group_by(Job.status)
        result = await self.db.execute(query)
        counts = {status.value if hasattr(status, "value") else str(status): 0 for status in JobStatus}
        for status, cnt in result.all():
            k = status.value if hasattr(status, "value") else str(status)
            counts[k] = cnt
        return counts
