from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "FlowForge"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./flowforge.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://flowforge:flowforge_secret@localhost:5672/")
    USE_EMBEDDED_BROKER: bool = os.getenv("USE_EMBEDDED_BROKER", "true").lower() == "true"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY", "flowforge-super-secret-key-at-least-32-chars-long")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    HEARTBEAT_INTERVAL_SECONDS: int = 5
    HEARTBEAT_TIMEOUT_SECONDS: int = 15
    WORKER_CONCURRENCY: int = 4
    ENABLE_DEMO_MODE: bool = True
    
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="allow")

settings = Settings()
