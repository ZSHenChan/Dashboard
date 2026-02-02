import os, logging
from contextlib import contextmanager
from fastapi import BackgroundTasks
from core.context import get_request_id
from core.config import config
from app.logging_config import SensitiveDataFilter

async def _send_log_task(log_path: str):
    """
    Reads the completed log file and processes/sends it.
    """
    pass
    # print(f"Background Task: Processing log file at {log_path}...")

@contextmanager
def session_logger_with_task(background_tasks: BackgroundTasks, log_dir: str = config.SESSION_LOG_FILE_PATH):
    """
    Context manager to handle session-specific logging setup/teardown.
    NOW WITH SENSITIVE DATA FILTERING!
    """
    req_id = get_request_id()
    log_dir = os.path.dirname(log_dir)

    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, f"sess_{req_id}.log")

    handler = logging.FileHandler(log_path)
    sess_formatter = logging.Formatter(config.SESS_LOG_FORMAT)
    handler.setFormatter(sess_formatter)
    handler.setLevel(logging.DEBUG)
    
    handler.addFilter(SensitiveDataFilter()) 

    sess_logger = logging.getLogger(config.SESSION_LOGGER_NAME)
    sess_logger.setLevel(logging.DEBUG)
    sess_logger.addHandler(handler)
    
    sess_logger.propagate = False 

    try:
        yield sess_logger
    finally:
        sess_logger.removeHandler(handler)
        handler.close()
        
        background_tasks.add_task(_send_log_task, log_path)