import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import redis.asyncio as redis
from core.config import config
from fastapi.responses import JSONResponse
from config.db import pool

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        redis_client = redis.Redis(connection_pool=pool)

        key = f"rate_limit:{client_ip}"
        request_count = await redis_client.incr(key)

        if request_count == 1:
            await redis_client.expire(key, config.RATE_LIMIT_PERIOD)

        if request_count > config.RATE_LIMIT_LIMIT:
            security_logger = logging.getLogger("security.anomaly")
            
            security_logger.error(
                "Suspicious Activity Detected: IP %s exceeded rate limit (%d reqs/%ds). Path: %s",
                client_ip, request_count, config.RATE_LIMIT_PERIOD, request.url.path,
                extra={
                    "ip": client_ip,
                    "user_agent": request.headers.get("user-agent"),
                    "fingerprint": ["security-anomaly"]
                }
            )
        
            return JSONResponse(status_code=429, content={"detail": "Blocked"})

        response = await call_next(request)
        return response