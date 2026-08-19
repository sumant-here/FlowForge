import sys
import os
import asyncio
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.broker import broker
from app.core.logging import setup_logging
from app.services.scheduler_service import SchedulerService
from app.services.worker_service import WorkerService

setup_logging()
logger = logging.getLogger("flowforge.scheduler")

class SchedulerDaemon:
    def __init__(self):
        self.running = False

    async def start(self):
        self.running = True
        logger.info("Starting FlowForge Scheduler & Crash Recovery Daemon...")
        await broker.connect()

        while self.running:
            try:
                async with AsyncSessionLocal() as session:
                    # 1. Process recurring & cron schedules
                    sched_svc = SchedulerService(session)
                    triggered = await sched_svc.process_due_schedules()
                    if triggered:
                        logger.info(f"Scheduler triggered {len(triggered)} due jobs.")

                    # 2. Detect crashed workers & auto-requeue orphaned jobs
                    worker_svc = WorkerService(session)
                    recovered = await worker_svc.detect_and_recover_stale_workers(
                        timeout_seconds=settings.HEARTBEAT_TIMEOUT_SECONDS
                    )
                    if recovered:
                        logger.warning(f"Crash Recovery: Recovered {len(recovered)} jobs from dead workers: {recovered}")

            except Exception as e:
                logger.error(f"Scheduler loop iteration error: {e}")

            await asyncio.sleep(2.0)

    async def stop(self):
        self.running = False
        await broker.disconnect()

if __name__ == "__main__":
    daemon = SchedulerDaemon()
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        asyncio.run(daemon.stop())
