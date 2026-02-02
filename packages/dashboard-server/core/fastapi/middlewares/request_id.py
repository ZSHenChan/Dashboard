import sentry_sdk
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import MutableHeaders
from core.context import generate_request_id

class RequestIDMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        req_id = generate_request_id()

        with sentry_sdk.configure_scope() as sentry_scope:
            sentry_scope.set_tag("request_id", req_id)
            sentry_scope.set_transaction_name(f"{scope['method']} {scope['path']}")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                
                message["headers"] = headers.raw
            
            await send(message)

        await self.app(scope, receive, send_wrapper)