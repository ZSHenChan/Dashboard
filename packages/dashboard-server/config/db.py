import redis.asyncio as redis
from core.config import config
from pymongo import MongoClient

pool = redis.ConnectionPool.from_url(config.REDIS_URL, decode_responses=True)
global_redis_client = redis.Redis(connection_pool=pool)
# def check_pool_status():
#     in_use = len(pool._in_use_connections)
#     available = len(pool._available_connections)
#     print(f"Pool: {in_use} in use, {available} available")

mongodb_client = MongoClient(config.MONGODB_URL, timeoutMS=config.MONGODB_TIMEOUT)
mongodb_db = mongodb_client[config.MONGODB_AGENT]
