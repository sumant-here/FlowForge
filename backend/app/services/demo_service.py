import random
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.worker import Worker, WorkerStatus
from app.models.job import JobPriority
from app.models.schedule import Schedule
from app.schemas.job import JobCreate
from app.schemas.workflow import WorkflowCreate, WorkflowDefinition, WorkflowNode, WorkflowEdge
from app.services.job_service import JobService
from app.services.workflow_service import WorkflowService
from app.core.security import get_password_hash

class DemoService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_service = JobService(db)
        self.workflow_service = WorkflowService(db)

    async def seed_initial_demo_data(self):
        from app.repositories.user_repo import UserRepository
        from app.repositories.worker_repo import WorkerRepository
        from app.repositories.schedule_repo import ScheduleRepository

        user_repo = UserRepository(self.db)
        worker_repo = WorkerRepository(self.db)
        sched_repo = ScheduleRepository(self.db)

        if not await user_repo.get_by_email("admin@flowforge.dev"):
            admin_user = User(
                email="admin@flowforge.dev",
                hashed_password=get_password_hash("admin123!"),
                full_name="FlowForge Administrator",
                role=UserRole.ADMIN
            )
            await user_repo.create(admin_user)

        if not await user_repo.get_by_email("demo@flowforge.dev"):
            demo_user = User(
                email="demo@flowforge.dev",
                hashed_password=get_password_hash("demo123!"),
                full_name="Demo Engineer",
                role=UserRole.USER
            )
            await user_repo.create(demo_user)

        worker_specs = [
            ("worker-us-east-01", "ip-10-0-1-12", "10.0.1.12", 42.5, 58.1),
            ("worker-us-east-02", "ip-10-0-1-15", "10.0.1.15", 21.0, 34.6),
            ("worker-eu-west-01", "ip-10-0-2-88", "10.0.2.88", 68.3, 72.4),
            ("worker-ap-south-01", "ip-10-0-3-40", "10.0.3.40", 15.2, 28.0)
        ]
        for wid, hname, ip, cpu, mem in worker_specs:
            w_data = {
                "worker_id": wid,
                "hostname": hname,
                "ip_address": ip,
                "status": WorkerStatus.IDLE,
                "cpu_usage": cpu,
                "memory_usage": mem,
                "jobs_processed": random.randint(120, 850),
                "jobs_succeeded": random.randint(110, 820),
                "jobs_failed": random.randint(2, 18),
                "concurrency": 4,
                "tags": ["prod", "gpu" if "01" in wid else "compute"]
            }
            await worker_repo.upsert_heartbeat(w_data)

        wf_list = await self.workflow_service.workflow_repo.list_all()
        if not wf_list:
            data_pipeline_def = WorkflowDefinition(
                nodes=[
                    WorkflowNode(id="extract", name="Extract Raw Data", job_type="io_simulation", payload={"latency_seconds": 1.2, "chunks": 4}, position={"x": 50, "y": 150}),
                    WorkflowNode(id="validate", name="Validate & Clean Schema", job_type="data_processing", payload={"records_count": 1000}, position={"x": 300, "y": 150}),
                    WorkflowNode(id="compute_stats", name="Calculate Analytics", job_type="cpu_intensive", payload={"limit": 15000}, position={"x": 580, "y": 70}),
                    WorkflowNode(id="render_charts", name="Transform Image Assets", job_type="image_transformation", payload={"width": 1920, "height": 1080}, position={"x": 580, "y": 240}),
                    WorkflowNode(id="generate_report", name="Publish PDF Report", job_type="report_generator", payload={"report_type": "QUARTERLY_PERFORMANCE"}, position={"x": 860, "y": 150})
                ],
                edges=[
                    WorkflowEdge(id="e1", source="extract", target="validate", condition="success"),
                    WorkflowEdge(id="e2", source="validate", target="compute_stats", condition="success"),
                    WorkflowEdge(id="e3", source="validate", target="render_charts", condition="success"),
                    WorkflowEdge(id="e4", source="compute_stats", target="generate_report", condition="success"),
                    WorkflowEdge(id="e5", source="render_charts", target="generate_report", condition="success")
                ]
            )
            await self.workflow_service.create_workflow(WorkflowCreate(
                name="E-Commerce Daily Analytics Pipeline",
                description="End-to-end distributed DAG workflow for multi-stage ETL and report generation.",
                definition=data_pipeline_def
            ))

        schedules = await sched_repo.list()
        if not schedules:
            now = datetime.now(timezone.utc)
            s1 = Schedule(
                name="Every 5 Minutes System Health Audit",
                cron_expression="*/5 * * * *",
                job_type="io_simulation",
                priority="HIGH",
                payload={"latency_seconds": 0.5},
                is_active=True,
                next_run_at=now + timedelta(minutes=5)
            )
            s2 = Schedule(
                name="Hourly Executive PDF Generator",
                cron_expression="0 * * * *",
                job_type="report_generator",
                priority="NORMAL",
                payload={"report_type": "HOURLY_THROUGHPUT"},
                is_active=True,
                next_run_at=now + timedelta(hours=1)
            )
            await sched_repo.create(s1)
            await sched_repo.create(s2)

        sample_jobs = [
            ("Calculate RSA Key Primes", "cpu_intensive", JobPriority.CRITICAL, {"limit": 25000}),
            ("Fetch Customer Webhook Ingestion", "io_simulation", JobPriority.HIGH, {"latency_seconds": 1.5}),
            ("Batch Transform User Events", "data_processing", JobPriority.NORMAL, {"records_count": 800}),
            ("Compress Profile Avatars", "image_transformation", JobPriority.LOW, {"width": 800, "height": 800}),
            ("Simulated Chaos Failure & Auto-Retry", "failure_simulation", JobPriority.HIGH, {"fail_until_attempt": 2})
        ]
        for name, jtype, prio, pld in sample_jobs:
            await self.job_service.submit_job(JobCreate(
                name=name,
                job_type=jtype,
                priority=prio,
                payload=pld
            ))
