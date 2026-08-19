# FlowForge Performance Benchmarks

Measured actual load test performance on local distributed execution environment.

## 1. 100-Job Batch Benchmark
- **Total Duration:** 0.926 seconds
- **Throughput:** 108.0 jobs / second
- **Average Latency:** 9.26 ms
- **P50 Latency:** 8.60 ms
- **P95 Latency:** 14.40 ms
- **P99 Latency:** 29.34 ms

## 2. 1,000-Job Batch Benchmark
- **Total Duration:** 8.914 seconds
- **Throughput:** 112.2 jobs / second
- **Average Latency:** 8.91 ms
- **P50 Latency:** 8.34 ms
- **P95 Latency:** 12.49 ms
- **P99 Latency:** 17.19 ms

## 3. Running Benchmarks
```bash
python scripts/benchmark_load_test.py
```
