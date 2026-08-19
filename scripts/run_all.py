import subprocess
import sys
import os
import time

def start_services():
    print("Starting FlowForge Distributed Platform...")
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    print("1. Initializing DB & Seeding data...")
    subprocess.run([sys.executable, "scripts/seed_data.py"], cwd=root)

    print("
2. Launching FastAPI API Gateway on http://localhost:8000 ...")
    api_proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=os.path.join(root, "backend"))

    print("3. Launching Worker Pool #1...")
    w1_proc = subprocess.Popen([sys.executable, "worker/app/worker_daemon.py", "worker-node-01"], cwd=root)

    print("4. Launching Worker Pool #2...")
    w2_proc = subprocess.Popen([sys.executable, "worker/app/worker_daemon.py", "worker-node-02"], cwd=root)

    print("5. Launching Scheduler & Crash Recovery Daemon...")
    sched_proc = subprocess.Popen([sys.executable, "scheduler/app/scheduler_daemon.py"], cwd=root)

    print("
All FlowForge services running!")
    print("API Docs: http://localhost:8000/docs")
    print("Metrics:  http://localhost:8000/metrics")
    print("Health:   http://localhost:8000/health")
    print("
Press Ctrl+C to terminate all services.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("
Stopping FlowForge services...")
        api_proc.terminate()
        w1_proc.terminate()
        w2_proc.terminate()
        sched_proc.terminate()
        print("All processes terminated.")

if __name__ == "__main__":
    start_services()
