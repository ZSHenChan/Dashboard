import redis.asyncio as redis
from config.db import global_redis_client

async def get_redis_client() -> redis.Redis:
    return global_redis_client