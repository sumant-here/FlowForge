import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.core.database import init_db, AsyncSessionLocal
from app.services.demo_service import DemoService

async def main():
    print("Initializing FlowForge Database...")
    await init_db()
    async with AsyncSessionLocal() as session:
        demo_svc = DemoService(session)
        print("Seeding demo users, workers, workflows, schedules, and priority jobs...")
        await demo_svc.seed_initial_demo_data()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
