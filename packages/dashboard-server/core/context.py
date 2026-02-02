from contextvars import ContextVar
from uuid import uuid4

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="N/A")

def get_request_id() -> str:
    return request_id_ctx.get()

def generate_request_id() -> str:
    new_id = str(uuid4())
    request_id_ctx.set(new_id)
    return new_id