from cachetools import TTLCache
from datetime import datetime
from app.config import settings
import json
import logging

logger = logging.getLogger(__name__)


class InMemoryCache:
    """
    Cache sederhana in-memory menggunakan cachetools.
    Ganti dengan Redis untuk production multi-instance.
    """

    def __init__(self):
        self.cache = TTLCache(maxsize=1000, ttl=settings.CACHE_TTL_SECONDS)

    async def initialize(self):
        logger.info("In-memory cache initialized")

    async def close(self):
        self.cache.clear()

    async def get(self, key: str):
        try:
            value = self.cache.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def set(self, key: str, value, ttl: int = None):
        try:
            self.cache[key] = json.dumps(value, default=str)
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")

    async def delete(self, key: str):
        self.cache.pop(key, None)


# Bisa swap ke Redis nanti:
# from redis.asyncio import Redis
# class RedisCache:
#     def __init__(self): self.redis = Redis.from_url(settings.REDIS_URL)
#     async def get(self, key): val = await self.redis.get(key); return json.loads(val) if val else None
#     async def set(self, key, value, ttl=300): await self.redis.set(key, json.dumps(value, default=str), ex=ttl)

cache = InMemoryCache()
