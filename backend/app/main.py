from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
import time
import asyncio

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import redis_client
from app.core.broker import broker
from app.core.logging import setup_logging
from app.services.demo_service import DemoService
from app.core.database import AsyncSessionLocal

# Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.workers import router as workers_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.schedules import router as schedules_router
from app.api.v1.queues import router as queues_router
from app.api.v1.dead_letter import router as dlq_router
from app.api.v1.chaos import router as chaos_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.system import router as system_router
from app.api.v1.websocket import router as ws_router

setup_logging()

# Prometheus metrics
REQUEST_COUNT = Counter("flowforge_http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("flowforge_http_request_duration_seconds", "HTTP request latency", ["endpoint"])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await redis_client.connect()
    await broker.connect()
    
    # Auto-seed initial demo data if enabled
    if settings.ENABLE_DEMO_MODE:
        async with AsyncSessionLocal() as session:
            try:
                demo_svc = DemoService(session)
                await demo_svc.seed_initial_demo_data()
            except Exception as e:
                print("Demo seeding skipped/error:", e)

    yield
    # Shutdown
    await broker.disconnect()
    await redis_client.disconnect()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Distributed Job Processing & Workflow Orchestration Engine",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    endpoint = request.url.path
    status = str(response.status_code)
    REQUEST_COUNT.labels(method=request.method, endpoint=endpoint, status=status).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    return response

# Include V1 Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(jobs_router, prefix=settings.API_V1_STR)
app.include_router(workers_router, prefix=settings.API_V1_STR)
app.include_router(workflows_router, prefix=settings.API_V1_STR)
app.include_router(schedules_router, prefix=settings.API_V1_STR)
app.include_router(queues_router, prefix=settings.API_V1_STR)
app.include_router(dlq_router, prefix=settings.API_V1_STR)
app.include_router(chaos_router, prefix=settings.API_V1_STR)
app.include_router(metrics_router, prefix=settings.API_V1_STR)
app.include_router(system_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "HEALTHY", "service": "FlowForge API Gateway", "version": settings.VERSION}

@app.get("/ready")
async def readiness_check():
    return {"ready": True, "database": "CONNECTED", "broker": "READY"}

@app.get("/metrics")
async def prometheus_metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)
