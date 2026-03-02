import redis.asyncio as redis
from config.db import pool

async def get_redis_client() -> redis.Redis:
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.close()
