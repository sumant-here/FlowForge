# FlowForge REST API Reference

All endpoints prefixed with `/api/v1`.

## Authentication
- `POST /api/v1/auth/register` - Create new user account.
- `POST /api/v1/auth/login` - Authenticate and obtain JWT access token.
- `GET /api/v1/auth/me` - Get current user profile.

## Jobs
- `POST /api/v1/jobs` - Submit new job.
- `GET /api/v1/jobs` - List jobs with filtering, pagination, and search.
- `GET /api/v1/jobs/{id}` - Get full job details, execution timeline, logs, and attempts.
- `POST /api/v1/jobs/{id}/retry` - Trigger manual job retry.
- `POST /api/v1/jobs/{id}/cancel` - Cancel active/queued job.

## Workers
- `GET /api/v1/workers` - List registered distributed workers with CPU/RAM metrics.
- `POST /api/v1/workers/heartbeat` - Worker heartbeat ingestion.
- `POST /api/v1/workers/{id}/drain` - Gracefully drain worker.

## Workflows
- `POST /api/v1/workflows` - Create DAG workflow definition.
- `GET /api/v1/workflows` - List workflows.
- `GET /api/v1/workflows/{id}` - Get workflow details and step states.
- `POST /api/v1/workflows/{id}/run` - Trigger DAG workflow execution.

## Queues & DLQ
- `GET /api/v1/queues` - Inspect queue depths across priority tiers.
- `GET /api/v1/dlq` - List unresolved dead-lettered jobs.
- `POST /api/v1/dlq/{id}/replay` - Replay dead-lettered job.
- `DELETE /api/v1/dlq/purge` - Purge dead letter records.

## Metrics & Chaos
- `GET /api/v1/metrics/summary` - Aggregate telemetry summary.
- `POST /api/v1/chaos/execute` - Trigger chaos disaster injection.
- `GET /metrics` - Prometheus metrics scraping endpoint.
