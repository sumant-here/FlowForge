import pytest
from app.core.database import AsyncSessionLocal
from app.services.worker_service import WorkerService
from app.schemas.worker import WorkerHeartbeat
from app.models.worker import WorkerStatus

@pytest.mark.asyncio
async def test_worker_heartbeat_and_drain():
    async with AsyncSessionLocal() as session:
        worker_svc = WorkerService(session)

        hb = WorkerHeartbeat(
            worker_id="test-worker-unit-01",
            hostname="test-host",
            status=WorkerStatus.IDLE,
            cpu_usage=12.5,
            memory_usage=35.0,
            concurrency=4
        )
        worker = await worker_svc.process_heartbeat(hb)
        assert worker.id == "test-worker-unit-01"
        assert worker.status == WorkerStatus.IDLE

        drained = await worker_svc.drain_worker("test-worker-unit-01")
        assert drained.status == WorkerStatus.DRAINING
