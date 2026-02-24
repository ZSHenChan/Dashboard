import time, logging
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import Headers
from core.config import config
from core.context import get_request_id

logger = logging.getLogger(config.CENTRAL_LOGGER_NAME)

class AccessLogMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        client_ip = scope.get("client", ("0.0.0.0", 0))[0]
        headers = Headers(scope=scope)
        
        forwarded = headers.get("x-forwarded-for")
        if forwarded:
            client_ip = forwarded.split(",")[0]
        else:
            client_ip = scope.get("client", ("0.0.0.0", 0))[0]
    
        user_agent = headers.get("user-agent", "Unknown Device")
        method = scope["method"]
        path = scope["path"]

        status_code = 500 
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            raise e
        finally:
            process_time = time.time() - start_time
            
            logger.info(
                f"{method} {path} | Status: {status_code} | IP: {client_ip} | Device: {user_agent} | Time: {process_time:.3f}s"
            )