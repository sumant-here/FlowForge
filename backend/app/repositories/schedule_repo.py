from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.schedule import Schedule
from app.repositories.base import BaseRepository

class ScheduleRepository(BaseRepository[Schedule]):
    def __init__(self, db: AsyncSession):
        super().__init__(Schedule, db)

    async def get_due_schedules(self) -> List[Schedule]:
        now = datetime.now(timezone.utc)
        query = select(Schedule).where(
            Schedule.is_active == True,
            Schedule.next_run_at <= now
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
