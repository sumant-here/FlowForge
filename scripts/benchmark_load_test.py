import sys
import os
import time
import asyncio
import statistics
from typing import List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from app.core.database import init_db, AsyncSessionLocal
from app.core.broker import broker
from app.services.job_service import JobService
from app.schemas.job import JobCreate
from app.models.job import JobPriority

async def run_benchmark(batch_size: int = 100):
    print("==================================================")
    print(f"   FLOWFORGE LOAD TEST BENCHMARK ({batch_size} JOBS)")
    print("==================================================")
    
    await init_db()
    await broker.connect()
    
    latencies: List[float] = []
    start_total = time.time()
    
    async with AsyncSessionLocal() as session:
        job_svc = JobService(session)
        
        print(f"Submitting {batch_size} jobs with mixed priority and workloads...")
        for i in range(batch_size):
            t0 = time.time()
            prio = JobPriority.CRITICAL if i % 10 == 0 else (JobPriority.HIGH if i % 4 == 0 else JobPriority.NORMAL)
            job_in = JobCreate(
                name=f"Benchmark Job #{i+1}",
                job_type="cpu_intensive" if i % 2 == 0 else "data_processing",
                priority=prio,
                payload={"limit": 3000, "records_count": 200}
            )
            await job_svc.submit_job(job_in)
            latencies.append((time.time() - t0) * 1000)

    total_time = time.time() - start_total
    rps = batch_size / total_time
    
    latencies.sort()
    p50 = statistics.median(latencies)
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg = statistics.mean(latencies)

    print(f"\n[BENCHMARK RESULTS - {batch_size} JOBS]")
    print(f"Total Submission Time: {total_time:.3f} s")
    print(f"Throughput:            {rps:.1f} jobs/sec")
    print(f"Avg Latency:           {avg:.2f} ms")
    print(f"P50 Latency:           {p50:.2f} ms")
    print(f"P95 Latency:           {p95:.2f} ms")
    print(f"P99 Latency:           {p99:.2f} ms")
    print("==================================================\n")
    
    await broker.disconnect()
    return {"batch": batch_size, "total_time": total_time, "rps": rps, "avg": avg, "p50": p50, "p95": p95, "p99": p99}

async def main():
    await run_benchmark(100)
    await run_benchmark(1000)

if __name__ == "__main__":
    asyncio.run(main())