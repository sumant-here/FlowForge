import sys
import os
import time
import socket
import uuid
import signal
import asyncio
import psutil
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from app.core.config import settings
from app.core.broker import broker, QUEUE_NAMES
from app.core.redis_client import redis_client
from app.core.logging import setup_logging
from app.schemas.worker import WorkerHeartbeat
from app.models.worker import WorkerStatus
from worker.app.runner import JobRunner
import httpx

setup_logging()
logger = logging.getLogger("flowforge.worker")

class WorkerDaemon:
    def __init__(self, worker_id: str = None):
        self.worker_id = worker_id or f"worker-{socket.gethostname()}-{str(uuid.uuid4())[:8]}"
        self.hostname = socket.gethostname()
        self.ip_address = "127.0.0.1"
        self.status = WorkerStatus.IDLE
        self.running = False
        self.current_job_id = None
        self.jobs_processed = 0
        self.jobs_succeeded = 0
        self.jobs_failed = 0
        self.concurrency = settings.WORKER_CONCURRENCY
        self.sem = asyncio.Semaphore(self.concurrency)

    async def send_heartbeat(self):
        while self.running:
            try:
                hb = WorkerHeartbeat(
                    worker_id=self.worker_id,
                    hostname=self.hostname,
                    ip_address=self.ip_address,
                    status=self.status,
                    current_job_id=self.current_job_id,
                    jobs_processed=self.jobs_processed,
                    jobs_succeeded=self.jobs_succeeded,
                    jobs_failed=self.jobs_failed,
                    cpu_usage=psutil.cpu_percent(),
                    memory_usage=psutil.virtual_memory().percent,
                    concurrency=self.concurrency
                )
                from app.core.database import AsyncSessionLocal
                from app.repositories.worker_repo import WorkerRepository
                async with AsyncSessionLocal() as session:
                    repo = WorkerRepository(session)
                    await repo.upsert_heartbeat(hb.model_dump())
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
            await asyncio.sleep(settings.HEARTBEAT_INTERVAL_SECONDS)

    async def start(self):
        self.running = True
        logger.info(f"Starting FlowForge Worker '{self.worker_id}' (Concurrency: {self.concurrency})")
        await broker.connect()
        await redis_client.connect()

        # Start background heartbeat loop
        asyncio.create_task(self.send_heartbeat())

        # Main worker consumption loop with strict Priority Queue ordering
        # Critical -> High -> Normal -> Low
        priority_order = ["queue.critical", "queue.high", "queue.normal", "queue.low"]

        while self.running:
            if self.status == WorkerStatus.DRAINING:
                logger.info("Worker draining, exiting loop...")
                break

            consumed_job = False
            for q_name in priority_order:
                job_msg = await broker.consume_one(q_name, timeout=0.1)
                if job_msg:
                    consumed_job = True
                    asyncio.create_task(self._process_wrapper(job_msg))
                    break # Back to top to prioritize critical/high queues again

            if not consumed_job:
                await asyncio.sleep(0.1)

    async def _process_wrapper(self, msg_payload: dict):
        async with self.sem:
            self.status = WorkerStatus.BUSY
            self.current_job_id = msg_payload.get("job_id")
            self.jobs_processed += 1
            try:
                await JobRunner.execute_job(msg_payload, self.worker_id)
                self.jobs_succeeded += 1
            except Exception as e:
                self.jobs_failed += 1
                logger.error(f"Error executing job: {e}")
            finally:
                self.current_job_id = None
                self.status = WorkerStatus.IDLE

    async def stop(self):
        logger.info(f"Shutting down worker {self.worker_id}...")
        self.running = False
        self.status = WorkerStatus.OFFLINE
        await broker.disconnect()

if __name__ == "__main__":
    w_id = sys.argv[1] if len(sys.argv) > 1 else None
    daemon = WorkerDaemon(worker_id=w_id)
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        asyncio.run(daemon.stop())
