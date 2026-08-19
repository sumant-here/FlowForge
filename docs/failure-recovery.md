# FlowForge Failure Recovery & Chaos Lab

## 1. Failure Recovery Mechanics
FlowForge is designed with resilience at every layer:

```mermaid
sequenceDiagram
    participant W as Worker Pool
    participant S as Scheduler Daemon
    participant B as Broker (RabbitMQ)
    participant D as PostgreSQL
    
    W->>W: Process Crashes (SIGKILL)
    Note over W: Heartbeat stops
    S->>D: Check workers with last_heartbeat > 15s
    S->>D: Mark worker OFFLINE
    S->>D: Reset active Job status: RUNNING -> QUEUED
    S->>B: Re-publish job payload to Priority Queue
    B->>W: Healthy Worker consumes and completes job
```

## 2. Chaos Engineering Scenarios
- **Worker Termination:** Simulates sudden worker loss during execution.
- **Intentional Failure:** Stresses exponential retry backoff.
- **Queue Flooding:** Evaluates priority preemption under high load.
