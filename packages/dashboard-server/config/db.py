import redis.asyncio as redis
from core.config import config

pool = redis.ConnectionPool.from_url(config.REDIS_URL, decode_responses=True)