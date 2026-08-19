import asyncio
import math
import random
import time
from typing import Dict, Any, Callable, Awaitable
from app.core.exceptions import JobExecutionError, NonRetryableJobError

class TaskRegistry:
    def __init__(self):
        self._handlers: Dict[str, Callable[[Dict[str, Any], Any], Awaitable[Dict[str, Any]]]] = {}
        self._register_builtins()

    def register(self, name: str, handler: Callable):
        self._handlers[name] = handler

    def get(self, name: str) -> Callable:
        return self._handlers.get(name, self._default_handler)

    def _register_builtins(self):
        self._handlers["cpu_intensive"] = self._handle_cpu
        self._handlers["io_simulation"] = self._handle_io
        self._handlers["data_processing"] = self._handle_data_processing
        self._handlers["image_transformation"] = self._handle_image
        self._handlers["report_generator"] = self._handle_report
        self._handlers["failure_simulation"] = self._handle_failure
        self._handlers["sleep_delay"] = self._handle_sleep
        self._handlers["custom"] = self._handle_custom

    async def _handle_cpu(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        """Calculates primes and matrix transforms to simulate real compute work."""
        limit = payload.get("limit", 20000)
        primes = []
        for i in range(2, limit):
            is_prime = True
            for d in range(2, int(math.isqrt(i)) + 1):
                if i % d == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(i)
            if i % (limit // 5 or 1) == 0 and progress_cb:
                await progress_cb(f"Evaluated {i}/{limit} numbers, found {len(primes)} primes")
                await asyncio.sleep(0.01)
        
        return {
            "status": "COMPLETED",
            "primes_count": len(primes),
            "highest_prime": primes[-1] if primes else 0,
            "complexity_score": limit * len(primes)
        }

    async def _handle_io(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        """Simulates external network/file I/O."""
        latency = payload.get("latency_seconds", 1.0)
        chunks = payload.get("chunks", 4)
        for c in range(1, chunks + 1):
            await asyncio.sleep(latency / chunks)
            if progress_cb:
                await progress_cb(f"Fetched chunk {c}/{chunks} ({c * 256} KB)")
        
        return {
            "status": "COMPLETED",
            "bytes_transferred": chunks * 262144,
            "endpoints_contacted": ["api.flowforge.internal/data", "s3.storage/blobs"],
            "io_time_seconds": latency
        }

    async def _handle_data_processing(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        """Processes and transforms data batch."""
        records_count = payload.get("records_count", 500)
        if progress_cb:
            await progress_cb(f"Parsing schema for {records_count} records")
        await asyncio.sleep(0.2)
        
        records = [{"id": i, "val": i * 1.5, "flag": i % 2 == 0} for i in range(records_count)]
        valid_records = [r for r in records if r["flag"]]
        avg_val = sum(r["val"] for r in valid_records) / len(valid_records) if valid_records else 0
        
        return {
            "status": "COMPLETED",
            "total_records": records_count,
            "filtered_records": len(valid_records),
            "average_metric": round(avg_val, 2),
            "checksum": f"sha256-{records_count * 42}"
        }

    async def _handle_image(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        """Performs simulated image transformations."""
        width = payload.get("width", 1920)
        height = payload.get("height", 1080)
        ops = payload.get("operations", ["resize", "filter_blur", "watermark", "compress"])
        
        for op in ops:
            if progress_cb:
                await progress_cb(f"Applying operation: {op}")
            await asyncio.sleep(0.15)
        
        return {
            "status": "COMPLETED",
            "original_dim": f"{width}x{height}",
            "processed_dim": f"{width // 2}x{height // 2}",
            "applied_filters": ops,
            "compression_ratio": "0.42"
        }

    async def _handle_report(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        """Generates comprehensive summary report."""
        report_type = payload.get("report_type", "EXECUTIVE_FINANCIAL")
        if progress_cb:
            await progress_cb("Aggregating metrics across distributed workers")
        await asyncio.sleep(0.2)
        
        return {
            "status": "COMPLETED",
            "report_type": report_type,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "summary": {
                "total_volume": 4200000,
                "efficiency_rate": "99.8%",
                "cost_saved_usd": 12850
            },
            "document_url": f"https://reports.flowforge.internal/{report_type.lower()}-summary.pdf"
        }

    async def _handle_failure(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        """Intentionally fails to demonstrate retries and Dead Letter Queue mechanics."""
        should_fail_always = payload.get("always_fail", False)
        fail_attempt_threshold = payload.get("fail_until_attempt", 3)
        current_attempt = payload.get("current_attempt", 1)
        fatal = payload.get("fatal_error", False)
        
        if progress_cb:
            await progress_cb(f"Attempt #{current_attempt}: Executing failure simulation")
        await asyncio.sleep(0.1)
        
        if fatal:
            raise NonRetryableJobError("Fatal error injected: Non-recoverable memory corruption")
        
        if should_fail_always or current_attempt < fail_attempt_threshold:
            raise JobExecutionError(
                f"Simulated network timeout/crash on attempt #{current_attempt}. Threshold={fail_attempt_threshold}",
                retryable=True
            )
        
        return {
            "status": "COMPLETED",
            "recovered_at_attempt": current_attempt,
            "message": "Successfully passed after retry attempts!"
        }

    async def _handle_sleep(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        seconds = payload.get("seconds", 3)
        for s in range(1, int(seconds) + 1):
            if progress_cb:
                await progress_cb(f"Sleeping... {s}/{seconds}s")
            await asyncio.sleep(1.0)
        return {"status": "COMPLETED", "duration_seconds": seconds}

    async def _handle_custom(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        await asyncio.sleep(0.2)
        return {"status": "COMPLETED", "output": payload}

    async def _default_handler(self, payload: Dict[str, Any], progress_cb=None) -> Dict[str, Any]:
        await asyncio.sleep(0.1)
        return {"status": "COMPLETED", "echo": payload}

task_registry = TaskRegistry()
