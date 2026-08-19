import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.core.database import init_db, AsyncSessionLocal
from app.services.chaos_service import ChaosService

async def main():
    await init_db()
    async with AsyncSessionLocal() as session:
        chaos = ChaosService(session)
        print("Executing Chaos Action 1: Force Job Failure...")
        r1 = await chaos.execute_chaos("force_job_failure", {})
        print("Result:", r1)

        print("
Executing Chaos Action 2: Flood Queue with 25 priority jobs...")
        r2 = await chaos.execute_chaos("flood_queue", {"job_count": 25})
        print("Result:", r2)

        print("
Executing Chaos Action 3: Kill Active Worker...")
        r3 = await chaos.execute_chaos("kill_worker", {})
        print("Result:", r3)

if __name__ == "__main__":
    asyncio.run(main())
