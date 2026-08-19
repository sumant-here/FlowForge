FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ /app/backend/
COPY scheduler/ /app/scheduler/
CMD ["python", "scheduler/app/scheduler_daemon.py"]
