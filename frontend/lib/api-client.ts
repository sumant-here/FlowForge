const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Client-side in-memory & localStorage store for live demo simulation mode
const getMockData = () => {
  if (typeof window === "undefined") return { jobs: [], workers: [], workflows: [] };
  const stored = localStorage.getItem("flowforge_mock_state");
  if (stored) {
    try { return JSON.parse(stored); } catch (e) {}
  }
  const initial = {
    jobs: [
      {
        id: "job-demo-prime-01",
        name: "Compute 10,000 Primes (CPU Intensive)",
        job_type: "cpu_intensive",
        priority: "CRITICAL",
        status: "SUCCEEDED",
        retry_count: 1,
        max_retries: 3,
        execution_duration_ms: 382,
        queue_name: "queue.critical",
        worker_id: "worker-node-01",
        created_at: new Date(Date.now() - 60000).toISOString(),
        payload: { limit: 10000 },
        result: { status: "COMPLETED", count: 1229, highest_prime: 9973 },
        logs: [
          { id: "1", timestamp: new Date(Date.now() - 60000).toISOString(), level: "INFO", message: "Job picked up by worker-node-01" },
          { id: "2", timestamp: new Date(Date.now() - 59000).toISOString(), level: "INFO", message: "Computed primes up to 10000 in chunks" },
          { id: "3", timestamp: new Date(Date.now() - 58000).toISOString(), level: "INFO", message: "Execution finished successfully in 382ms" }
        ],
        attempts: [{ id: "att-1", attempt_number: 1, worker_id: "worker-node-01", status: "SUCCEEDED", duration_ms: 382, started_at: new Date(Date.now() - 60000).toISOString() }]
      },
      {
        id: "job-demo-etl-02",
        name: "Transform Analytics JSON (ETL)",
        job_type: "data_processing",
        priority: "HIGH",
        status: "SUCCEEDED",
        retry_count: 1,
        max_retries: 3,
        execution_duration_ms: 540,
        queue_name: "queue.high",
        worker_id: "worker-node-02",
        created_at: new Date(Date.now() - 120000).toISOString(),
        payload: { records_count: 500 },
        result: { status: "PROCESSED", records_transformed: 500, checksum: "a9f4c3b" },
        logs: [
          { id: "1", timestamp: new Date(Date.now() - 120000).toISOString(), level: "INFO", message: "Streamed 500 records from ingest queue" },
          { id: "2", timestamp: new Date(Date.now() - 119000).toISOString(), level: "INFO", message: "Batch transformation complete" }
        ],
        attempts: [{ id: "att-2", attempt_number: 1, worker_id: "worker-node-02", status: "SUCCEEDED", duration_ms: 540, started_at: new Date(Date.now() - 120000).toISOString() }]
      },
      {
        id: "job-demo-image-03",
        name: "Generate Thumbnail Watermarks",
        job_type: "image_transformation",
        priority: "NORMAL",
        status: "RUNNING",
        retry_count: 1,
        max_retries: 3,
        execution_duration_ms: 180,
        queue_name: "queue.normal",
        worker_id: "worker-node-01",
        created_at: new Date().toISOString(),
        payload: { width: 1080, height: 720, filter: "sharpen" },
        logs: [
          { id: "1", timestamp: new Date().toISOString(), level: "INFO", message: "Resizing image to 1080x720..." }
        ],
        attempts: []
      }
    ],
    workers: [
      { id: "worker-node-01", hostname: "worker-prod-01", ip_address: "10.0.1.12", status: "BUSY", cpu_usage: 42.5, memory_usage: 38.0, concurrency: 4, jobs_processed: 124, jobs_succeeded: 122, jobs_failed: 2 },
      { id: "worker-node-02", hostname: "worker-prod-02", ip_address: "10.0.1.14", status: "IDLE", cpu_usage: 12.0, memory_usage: 26.5, concurrency: 4, jobs_processed: 98, jobs_succeeded: 97, jobs_failed: 1 }
    ],
    workflows: [
      {
        id: "wf-diamond-01",
        name: "Diamond DAG Pipeline",
        description: "Fetch Ingest -> (Transform Image + Compute Primes in Parallel) -> Compile PDF Report",
        status: "RUNNING",
        created_at: new Date(Date.now() - 300000).toISOString(),
        definition: {
          nodes: [
            { id: "step1", name: "Fetch Ingest Payload", job_type: "io_simulation" },
            { id: "step2a", name: "Transform Image Pipeline", job_type: "image_transformation" },
            { id: "step2b", name: "Compute Prime Checksums", job_type: "cpu_intensive" },
            { id: "step3", name: "Compile PDF Report", job_type: "report_generator" }
          ]
        },
        node_states: [
          { node_id: "step1", status: "SUCCEEDED", output_data: { fetched_bytes: 8192 } },
          { node_id: "step2a", status: "RUNNING" },
          { node_id: "step2b", status: "SUCCEEDED", output_data: { checksum: "e837bf" } },
          { node_id: "step3", status: "PENDING" }
        ]
      }
    ],
    schedules: [
      { id: "sched-1", name: "Hourly Partition Compression", cron_expression: "0 * * * *", is_active: true, total_runs: 48, next_run_at: new Date(Date.now() + 1800000).toISOString() },
      { id: "sched-2", name: "Worker Fleet Heartbeat Pruning", interval_seconds: 30, is_active: true, total_runs: 1420, next_run_at: new Date(Date.now() + 15000).toISOString() }
    ],
    dlq: [
      {
        id: "dlq-01",
        original_job_id: "job-fail-test-99",
        job_name: "External Webhook Ingest (Failed)",
        job_type: "io_simulation",
        queue_name: "queue.normal",
        failure_reason: "HTTP 503 Service Unavailable: Remote upstream gateway connection refused",
        stack_trace: "Traceback (most recent call last):\n  File 'worker/app/runner.py', line 68, in execute_job\n  aiohttp.ClientError: 503 Gateway Timeout",
        attempts_count: 3,
        moved_to_dlq_at: new Date(Date.now() - 900000).toISOString()
      }
    ]
  };
  localStorage.setItem("flowforge_mock_state", JSON.stringify(initial));
  return initial;
};

const saveMockData = (data: any) => {
  if (typeof window !== "undefined") {
    localStorage.setItem("flowforge_mock_state", JSON.stringify(data));
  }
};

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("flowforge_token") : null;
  const headers = new Headers(options.headers || {});
  headers.set("Content-Type", "application/json");
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000);

    const response = await fetch(`${API_BASE}/api/v1${endpoint}`, {
      ...options,
      headers,
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    // Seamless Simulated Mode for Live GitHub Pages / Offline Browser Execution
    return handleSimulatedRequest<T>(endpoint, options);
  }
}

function handleSimulatedRequest<T>(endpoint: string, options: RequestInit = {}): T {
  const method = options.method || "GET";
  const state = getMockData();

  // 1. METRICS SUMMARY
  if (endpoint.startsWith("/metrics/summary")) {
    const total = state.jobs.length;
    const running = state.jobs.filter((j: any) => j.status === "RUNNING").length;
    const queued = state.jobs.filter((j: any) => j.status === "QUEUED").length;
    const succeeded = state.jobs.filter((j: any) => j.status === "SUCCEEDED").length;
    const failed = state.jobs.filter((j: any) => j.status === "FAILED").length;
    const retrying = state.jobs.filter((j: any) => j.status === "RETRYING").length;
    const dlqCount = state.dlq.length;

    return {
      total_jobs: total,
      running_jobs: running,
      queued_jobs: queued,
      succeeded_jobs: succeeded,
      failed_jobs: failed,
      retrying_jobs: retrying,
      dead_lettered_jobs: dlqCount,
      active_workers: state.workers.length,
      total_workers: state.workers.length,
      total_workflows: state.workflows.length,
      host_cpu_percent: Math.floor(25 + Math.random() * 20),
      host_memory_percent: 44,
      queues: [
        { name: "queue.critical", depth: queued > 0 ? 1 : 0, processed: 142, failed: 1 },
        { name: "queue.high", depth: 0, processed: 289, failed: 3 },
        { name: "queue.normal", depth: 0, processed: 512, failed: 2 },
        { name: "queue.low", depth: 0, processed: 98, failed: 0 }
      ]
    } as T;
  }

  // 2. JOBS LIST / CREATE
  if (endpoint.startsWith("/jobs")) {
    if (method === "POST" && endpoint === "/jobs") {
      const body = JSON.parse((options.body as string) || "{}");
      const newJob = {
        id: `job-${Math.random().toString(36).substring(2, 9)}`,
        name: body.name || "Custom Computation Task",
        job_type: body.job_type || "cpu_intensive",
        priority: body.priority || "NORMAL",
        status: "RUNNING",
        retry_count: 1,
        max_retries: body.max_retries || 3,
        execution_duration_ms: 410,
        queue_name: `queue.${(body.priority || "normal").toLowerCase()}`,
        worker_id: "worker-node-01",
        created_at: new Date().toISOString(),
        payload: body.payload || {},
        result: { status: "COMPLETED", output: "Computed successfully in browser demo mode", duration: "410ms" },
        logs: [
          { id: "1", timestamp: new Date().toISOString(), level: "INFO", message: `Dispatched to worker-node-01 with priority ${body.priority || "NORMAL"}` },
          { id: "2", timestamp: new Date().toISOString(), level: "INFO", message: "Executing task handlers..." }
        ],
        attempts: [{ id: `att-${Date.now()}`, attempt_number: 1, worker_id: "worker-node-01", status: "RUNNING", duration_ms: 410, started_at: new Date().toISOString() }]
      };

      state.jobs.unshift(newJob);
      saveMockData(state);

      // Async simulate completion
      setTimeout(() => {
        const s = getMockData();
        const j = s.jobs.find((x: any) => x.id === newJob.id);
        if (j) {
          j.status = "SUCCEEDED";
          j.logs.push({ id: "3", timestamp: new Date().toISOString(), level: "INFO", message: "Task completed successfully (410ms)" });
          saveMockData(s);
        }
      }, 2500);

      return newJob as T;
    }

    // Job Detail
    const match = endpoint.match(/\/jobs\/([a-zA-Z0-9_-]+)/);
    if (match && !endpoint.includes("/retry") && !endpoint.includes("/cancel")) {
      const id = match[1];
      const job = state.jobs.find((j: any) => j.id === id) || state.jobs[0];
      return job as T;
    }

    // List Jobs
    return {
      items: state.jobs,
      total: state.jobs.length,
      page: 1,
      limit: 25,
      pages: 1
    } as T;
  }

  // 3. WORKERS
  if (endpoint.startsWith("/workers")) {
    return state.workers as T;
  }

  // 4. QUEUES
  if (endpoint.startsWith("/queues")) {
    return {
      queues: [
        { name: "queue.critical", depth: 0, enqueued: 142, processed: 142, failed: 0, consumers: 2 },
        { name: "queue.high", depth: 0, enqueued: 289, processed: 289, failed: 1, consumers: 2 },
        { name: "queue.normal", depth: 0, enqueued: 512, processed: 510, failed: 2, consumers: 2 },
        { name: "queue.low", depth: 0, enqueued: 98, processed: 98, failed: 0, consumers: 1 },
        { name: "queue.dlq", depth: state.dlq.length, enqueued: state.dlq.length, processed: 0, failed: 0, consumers: 0 }
      ],
      total_depth: 0,
      total_processed: 1039
    } as T;
  }

  // 5. WORKFLOWS
  if (endpoint.startsWith("/workflows")) {
    if (method === "POST" && endpoint.includes("/run")) {
      const id = endpoint.split("/")[2];
      const wf = state.workflows.find((w: any) => w.id === id) || state.workflows[0];
      wf.status = "RUNNING";
      saveMockData(state);
      return wf as T;
    }
    const match = endpoint.match(/\/workflows\/([a-zA-Z0-9_-]+)/);
    if (match) {
      return (state.workflows.find((w: any) => w.id === match[1]) || state.workflows[0]) as T;
    }
    return state.workflows as T;
  }

  // 6. CHAOS
  if (endpoint.startsWith("/chaos")) {
    return {
      status: "SUCCESS",
      action: "chaos_drill_executed",
      impact: "Disaster simulation completed. Scheduler detected state and triggered recovery loop."
    } as T;
  }

  // 7. SCHEDULES & DLQ
  if (endpoint.startsWith("/schedules")) {
    return state.schedules as T;
  }
  if (endpoint.startsWith("/dlq")) {
    return state.dlq as T;
  }

  // 8. SYSTEM
  if (endpoint.startsWith("/system/architecture")) {
    return {
      version: "1.0.0",
      components: [
        { id: "frontend", name: "Next.js 14 Developer Dashboard", role: "Real-time reactive control plane, workflow DAG designer, and chaos lab.", tech: "React 18, Next.js 14, Framer Motion, Tailwind CSS" },
        { id: "api_gateway", name: "FastAPI Distributed API Gateway", role: "Validates payloads, provides OpenAPI REST specs, handles JWT auth, and dispatches jobs to RabbitMQ.", tech: "Python 3.12, FastAPI, Pydantic v2, aio-pika, asyncio" },
        { id: "broker", name: "RabbitMQ Broker & Priority Queues", role: "High-throughput AMQP message broker with priority levels 0-10, Dead Letter Exchange (DLX), and delayed retries.", tech: "RabbitMQ 3.13 / AMQP 0-9-1 / Async Priority Engine" },
        { id: "worker_fleet", name: "Autonomous Distributed Worker Pool", role: "Heartbeating worker daemons executing CPU, I/O, Data, Image, and Report jobs with exponential backoff.", tech: "Python asyncio, Multi-worker pools, Task Registry, Process Isolation" },
        { id: "workflow_engine", name: "DAG Workflow Orchestrator", role: "Kahn's topological sorting, cycle detection, parallel branching, and conditional execution engine.", tech: "DAG Engine, State Machine, Dynamic Variable Passing" },
        { id: "database", name: "PostgreSQL Durable Persistence", role: "ACID relational store with indexed job lifecycle, attempts history, worker metadata, and DLQ entries.", tech: "PostgreSQL 16 / SQLAlchemy 2.0 Async / Alembic" },
        { id: "redis_pubsub", name: "Redis Pub/Sub & Heartbeat Cache", role: "Sub-millisecond worker heartbeat expiration, ephemeral states, and WebSocket event distribution.", tech: "Redis 7.2 / aioredis / PubSub" },
        { id: "observability", name: "Prometheus & Grafana Monitoring", role: "Scrapes Prometheus metrics at /metrics, monitors RPS, queue depth, error rates, and worker CPU.", tech: "Prometheus, Grafana, Structured Logging" }
      ]
    } as T;
  }

  return {} as T;
}