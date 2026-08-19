from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, delete
from app.models.dead_letter import DeadLetterJob, DLQStatus
from app.repositories.base import BaseRepository

class DLQRepository(BaseRepository[DeadLetterJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(DeadLetterJob, db)

    async def list_unresolved(self, skip: int = 0, limit: int = 50) -> List[DeadLetterJob]:
        query = (
            select(DeadLetterJob)
            .where(DeadLetterJob.status == DLQStatus.UNRESOLVED)
            .order_by(desc(DeadLetterJob.moved_to_dlq_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def purge_all(self) -> int:
        result = await self.db.execute(delete(DeadLetterJob))
        await self.db.commit()
        return result.rowcount
