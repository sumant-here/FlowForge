from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.worker import Worker, WorkerStatus
from app.repositories.base import BaseRepository

class WorkerRepository(BaseRepository[Worker]):
    def __init__(self, db: AsyncSession):
        super().__init__(Worker, db)

    async def upsert_heartbeat(self, worker_data: dict) -> Worker:
        worker_id = worker_data["worker_id"]
        existing = await self.get(worker_id)
        if existing:
            for k, v in worker_data.items():
                if k != "worker_id" and hasattr(existing, k):
                    setattr(existing, k, v)
            existing.last_heartbeat = datetime.now(timezone.utc)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            new_worker = Worker(
                id=worker_id,
                hostname=worker_data.get("hostname", "unknown"),
                ip_address=worker_data.get("ip_address", "127.0.0.1"),
                status=worker_data.get("status", WorkerStatus.IDLE),
                concurrency=worker_data.get("concurrency", 4),
                tags=worker_data.get("tags", []),
                last_heartbeat=datetime.now(timezone.utc)
            )
            self.db.add(new_worker)
            await self.db.commit()
            await self.db.refresh(new_worker)
            return new_worker

    async def find_stale_workers(self, timeout_seconds: int = 15) -> List[Worker]:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout_seconds)
        query = select(Worker).where(
            Worker.status != WorkerStatus.OFFLINE,
            Worker.last_heartbeat < cutoff
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
