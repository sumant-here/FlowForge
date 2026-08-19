import asyncio
import json
import logging
import time
from enum import Enum
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger("flowforge.broker")

class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"

PRIORITY_LEVELS = {
    Priority.CRITICAL: 10,
    Priority.HIGH: 7,
    Priority.NORMAL: 4,
    Priority.LOW: 1
}

QUEUE_NAMES = ["queue.critical", "queue.high", "queue.normal", "queue.low", "queue.dlq"]

class MessageBroker:
    def __init__(self):
        self._connection = None
        self._channel = None
        self._seq = 0
        self._in_memory_queues: Dict[str, asyncio.PriorityQueue] = {
            q: asyncio.PriorityQueue() for q in QUEUE_NAMES
        }
        self._subscribers: Dict[str, list] = {q: [] for q in QUEUE_NAMES}
        self._use_rabbitmq = not settings.USE_EMBEDDED_BROKER
        self._running = False
        self._stats = {q: {"enqueued": 0, "processed": 0, "failed": 0} for q in QUEUE_NAMES}

    async def connect(self):
        self._running = True
        if self._use_rabbitmq:
            try:
                import aio_pika
                self._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
                self._channel = await self._connection.channel()
                await self._channel.set_qos(prefetch_count=10)
                
                jobs_exchange = await self._channel.declare_exchange(
                    "flowforge.jobs", aio_pika.ExchangeType.TOPIC, durable=True
                )
                dlx_exchange = await self._channel.declare_exchange(
                    "flowforge.dlx", aio_pika.ExchangeType.DIRECT, durable=True
                )
                
                dlq = await self._channel.declare_queue("queue.dlq", durable=True)
                await dlq.bind(dlx_exchange, routing_key="dead_letter")
                
                for q_name, prio in [
                    ("queue.critical", 10),
                    ("queue.high", 7),
                    ("queue.normal", 4),
                    ("queue.low", 1)
                ]:
                    q = await self._channel.declare_queue(
                        q_name,
                        durable=True,
                        arguments={
                            "x-max-priority": 10,
                            "x-dead-letter-exchange": "flowforge.dlx",
                            "x-dead-letter-routing-key": "dead_letter"
                        }
                    )
                    await q.bind(jobs_exchange, routing_key="job." + q_name.split(".")[-1])
                
                logger.info("Connected to RabbitMQ at %s", settings.RABBITMQ_URL)
                return
            except Exception as e:
                logger.warning("RabbitMQ connection fallback to in-memory: %s", e)
                self._use_rabbitmq = False

        logger.info("In-memory priority broker initialized.")

    async def disconnect(self):
        self._running = False
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def publish_job(self, queue_name: str, payload: Dict[str, Any], priority: Priority = Priority.NORMAL, delay_seconds: int = 0) -> bool:
        if queue_name not in self._in_memory_queues:
            queue_name = "queue.normal"
        
        self._stats[queue_name]["enqueued"] += 1
        
        if delay_seconds > 0:
            async def delayed_pub():
                await asyncio.sleep(delay_seconds)
                await self._do_publish(queue_name, payload, priority)
            asyncio.create_task(delayed_pub())
            return True
        else:
            return await self._do_publish(queue_name, payload, priority)

    async def _do_publish(self, queue_name: str, payload: Dict[str, Any], priority: Priority) -> bool:
        prio_val = PRIORITY_LEVELS.get(priority, 4)
        
        if self._use_rabbitmq and self._channel:
            try:
                import aio_pika
                jobs_exchange = await self._channel.get_exchange("flowforge.jobs")
                message = aio_pika.Message(
                    body=json.dumps(payload).encode("utf-8"),
                    priority=prio_val,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                )
                routing_key = "job." + queue_name.split(".")[-1]
                await jobs_exchange.publish(message, routing_key=routing_key)
                return True
            except Exception as e:
                logger.error("RabbitMQ publish error: %s", e)

        heap_priority = -prio_val
        self._seq += 1
        await self._in_memory_queues[queue_name].put((heap_priority, self._seq, payload))
        return True

    async def consume_one(self, queue_name: str, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        if queue_name not in self._in_memory_queues:
            return None
        try:
            item = await asyncio.wait_for(self._in_memory_queues[queue_name].get(), timeout=timeout)
            _, _, payload = item
            self._in_memory_queues[queue_name].task_done()
            self._stats[queue_name]["processed"] += 1
            return payload
        except asyncio.TimeoutError:
            return None

    def get_queue_stats(self) -> Dict[str, Any]:
        result = {}
        for q_name in QUEUE_NAMES:
            q_depth = self._in_memory_queues[q_name].qsize()
            result[q_name] = {
                "name": q_name,
                "depth": q_depth,
                "enqueued": self._stats[q_name]["enqueued"],
                "processed": self._stats[q_name]["processed"],
                "failed": self._stats[q_name]["failed"],
                "consumers": len(self._subscribers.get(q_name, []))
            }
        return result

broker = MessageBroker()