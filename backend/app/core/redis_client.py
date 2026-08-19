import json
import logging
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger("flowforge.redis")

class RedisManager:
    def __init__(self):
        self._redis = None
        self._in_memory_store = {}
        self._connected = False

    async def connect(self):
        try:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            await self._redis.ping()
            self._connected = True
            logger.info("Connected to Redis at %s", settings.REDIS_URL)
        except Exception as e:
            logger.warning("Redis connection fallback to in-memory: %s", e)
            self._connected = False

    async def disconnect(self):
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Optional[str]:
        if self._connected and self._redis:
            try:
                return await self._redis.get(key)
            except Exception:
                pass
        return self._in_memory_store.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        val_str = value if isinstance(value, str) else json.dumps(value)
        if self._connected and self._redis:
            try:
                await self._redis.set(key, val_str, ex=ex)
                return True
            except Exception:
                pass
        self._in_memory_store[key] = val_str
        return True

    async def delete(self, key: str) -> bool:
        if self._connected and self._redis:
            try:
                await self._redis.delete(key)
                return True
            except Exception:
                pass
        self._in_memory_store.pop(key, None)
        return True

    async def publish(self, channel: str, message: dict) -> int:
        msg_str = json.dumps(message)
        if self._connected and self._redis:
            try:
                return await self._redis.publish(channel, msg_str)
            except Exception:
                pass
        return 1

redis_client = RedisManager()
