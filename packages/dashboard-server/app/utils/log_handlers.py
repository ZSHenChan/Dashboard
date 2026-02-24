import io, os, logging
from contextlib import contextmanager
from fastapi import BackgroundTasks
from core.context import get_request_id
from core.config import config
from app.logging_config import SensitiveDataFilter, RequestIdFilter
from botocore.exceptions import ClientError
from lib.s3_client import s3_client

central_logger = logging.getLogger(config.CENTRAL_LOGGER_NAME)

async def _send_log_task(session_id: str, log_content: str):
    """
    Uploads the log string directly to S3.
    """
    # Define a clear pathing strategy: e.g., logs/YYYY/MM/DD/uuid.log
    file_path = f"session-logs/{session_id}.log"
    
    try:
        # We convert the string to bytes for the S3 put_object call
        s3_client.put_object(
            Bucket=config.S3_BUCKET_NAME,
            Key=file_path,
            Body=log_content.encode('utf-8'),
            ContentType='text/plain'
        )
    except ClientError as e:
        # Important: Since this is a background task, log failures 
        # to your primary application log so they aren't lost.
        central_logger.error(f"Failed to upload session log {session_id} to S3: {e}")

@contextmanager
def session_logger_with_task(background_tasks: BackgroundTasks):
    req_id = get_request_id()

    # 1. Create an in-memory string buffer instead of a file
    log_stream = io.StringIO()
    handler = logging.StreamHandler(log_stream)
    
    sess_formatter = logging.Formatter(config.SESS_LOG_FORMAT)
    handler.setFormatter(sess_formatter)
    handler.setLevel(logging.DEBUG)
    handler.addFilter(SensitiveDataFilter()) 
    handler.addFilter(RequestIdFilter(req_id))

    # 2. Ensure the logger name is UNIQUE to this specific request
    logger_name = f"{config.SESSION_LOGGER_NAME}.{req_id}"
    sess_logger = logging.Logger(logger_name)
    sess_logger.setLevel(logging.DEBUG)
    sess_logger.addHandler(handler)
    sess_logger.propagate = False

    try:
        yield sess_logger
    finally:
        # 3. Clean up the handler
        sess_logger.removeHandler(handler)
        
        # 4. Extract the log text from memory
        log_content = log_stream.getvalue()
        
        # Free up the memory buffer
        log_stream.close()
        
        # 5. Send the log text directly to your background task
        if log_content:
            background_tasks.add_task(_send_log_task, req_id, log_content)