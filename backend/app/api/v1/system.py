from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.demo_service import DemoService

router = APIRouter(prefix="/system", tags=["System & Architecture"])

@router.get("/architecture")
async def get_architecture_map():
    return {
        "version": "1.0.0",
        "components": [
            {
                "id": "frontend",
                "name": "Next.js 14 Developer Dashboard",
                "role": "Real-time reactive control plane, workflow DAG designer, and chaos lab.",
                "tech": "React 18, Next.js 14, ReactFlow, Framer Motion, Tailwind CSS"
            },
            {
                "id": "api_gateway",
                "name": "FastAPI Distributed API Gateway",
                "role": "Validates payloads, provides OpenAPI REST specs, handles JWT auth, and dispatches jobs to RabbitMQ.",
                "tech": "Python 3.12, FastAPI, Pydantic v2, aio-pika, asyncio"
            },
            {
                "id": "broker",
                "name": "RabbitMQ Broker & Priority Queues",
                "role": "High-throughput AMQP message broker with priority levels 0-10, Dead Letter Exchange (DLX), and delayed retries.",
                "tech": "RabbitMQ 3.13 / AMQP 0-9-1 / Async Priority Engine"
            },
            {
                "id": "worker_fleet",
                "name": "Autonomous Distributed Worker Pool",
                "role": "Heartbeating worker daemons executing CPU, I/O, Data, Image, and Report jobs with exponential backoff.",
                "tech": "Python asyncio, Multi-worker pools, Task Registry, Process Isolation"
            },
            {
                "id": "workflow_engine",
                "name": "DAG Workflow Orchestrator",
                "role": "Kahn's topological sorting, cycle detection, parallel branching, and conditional execution engine.",
                "tech": "DAG Engine, State Machine, Dynamic Variable Passing"
            },
            {
                "id": "database",
                "name": "PostgreSQL Durable Persistence",
                "role": "ACID relational store with indexed job lifecycle, attempts history, worker metadata, and DLQ entries.",
                "tech": "PostgreSQL 16 / SQLAlchemy 2.0 Async / Alembic"
            },
            {
                "id": "redis_pubsub",
                "name": "Redis Pub/Sub & Heartbeat Cache",
                "role": "Sub-millisecond worker heartbeat expiration, ephemeral states, and WebSocket event distribution.",
                "tech": "Redis 7.2 / aioredis / PubSub"
            },
            {
                "id": "observability",
                "name": "Prometheus & Grafana Monitoring",
                "role": "Scrapes Prometheus metrics at /metrics, monitors RPS, queue depth, error rates, and worker CPU.",
                "tech": "Prometheus, Grafana, Structured Logging"
            }
        ]
    }

@router.post("/demo/seed")
async def seed_demo(db: AsyncSession = Depends(get_db)):
    service = DemoService(db)
    await service.seed_initial_demo_data()
    return {"status": "SUCCESS", "message": "Demo data successfully initialized."}
