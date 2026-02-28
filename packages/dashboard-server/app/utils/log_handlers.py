import io, os, logging
from contextlib import contextmanager
from fastapi import BackgroundTasks
from core.context import get_request_id
from core.config import config
from app.logging_config import SensitiveDataFilter, RequestIDFilter
from lib.s3_client import s3_client

central_logger = logging.getLogger(config.CENTRAL_LOGGER_NAME)

def _send_log_task(sess_id: str, content: str):
    """
    Receives the in-memory log content and processes/sends it to S3.
    """
    try:
        s3_client.put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=f"session_logs/{sess_id}.log",
            Body=content
        )
    except Exception as ex:
        central_logger.error("Failed to send log for %s: %s", sess_id, ex)


@contextmanager
def session_logger_with_task(background_tasks: BackgroundTasks):
    """
    Context manager to handle session-specific in-memory logging setup/teardown.
    """
    req_id = get_request_id()
    sess_id = f"session_{req_id}"

    log_buffer = io.StringIO()

    handler = logging.StreamHandler(log_buffer)
    sess_formatter = logging.Formatter(config.SESS_LOG_FORMAT)
    handler.setFormatter(sess_formatter)
    handler.setLevel(logging.DEBUG)
    
    handler.addFilter(SensitiveDataFilter())
    handler.addFilter(RequestIDFilter(req_id))

    sess_logger = logging.Logger(name=sess_id)
    sess_logger.setLevel(logging.DEBUG)
    sess_logger.addHandler(handler)
    sess_logger.propagate = False

    try:
        yield sess_logger
    finally:
        log_content = log_buffer.getvalue()

        sess_logger.removeHandler(handler)
        handler.close()
        log_buffer.close()

        if log_content:
            background_tasks.add_task(_send_log_task, sess_id, log_content)