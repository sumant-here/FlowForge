import pytest
from app.core.database import AsyncSessionLocal
from app.services.chaos_service import ChaosService

@pytest.mark.asyncio
async def test_chaos_actions():
    async with AsyncSessionLocal() as session:
        chaos_svc = ChaosService(session)

        res_failure = await chaos_svc.execute_chaos("force_job_failure", {})
        assert res_failure["action"] == "force_job_failure"
        assert "job_id" in res_failure

        res_flood = await chaos_svc.execute_chaos("flood_queue", {"job_count": 5})
        assert res_flood["action"] == "flood_queue"
        assert res_flood["enqueued_count"] == 5
