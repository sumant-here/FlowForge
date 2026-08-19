# FlowForge System Design

## 1. Core Subsystems

### A. API Gateway Layer
- Built with Python 3.12 and FastAPI.
- Implements Clean Architecture (`api` -> `services` -> `repositories` -> `models`).
- Strict schema validation via Pydantic v2.
- JWT and Role-Based Access Control (RBAC) supporting `USER` and `ADMIN` roles.

### B. Worker Orchestration & Heartbeat Engine
- Worker daemons register a unique identifier on startup.
- Heartbeats are broadcast every 5 seconds containing host CPU, memory usage, current active job ID, and cumulative stats.
- Auto-recovery: If a worker fails to heartbeat within 15 seconds, the Scheduler daemon marks it `OFFLINE` and automatically requeues any in-flight running job.

### C. Retry State Machine & DLQ
- Exponential backoff with full jitter formula: `delay = min(max_delay, base_delay * (2 ^ attempt)) + jitter`.
- Granular exception classification separating transient errors from fatal non-retryable exceptions.
- Permanent failures exceeding `max_retries` are routed to the Dead Letter Queue (`dead_letter_jobs`) for inspection and one-click replay.
