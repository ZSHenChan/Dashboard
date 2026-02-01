import redis.asyncio as redis
from core.config import config

r = redis.Redis(host=config.REDIS_URL, port=config.REDIS_PORT ,decode_responses=True, username="default", password=config.REDIS_PASSWORD)