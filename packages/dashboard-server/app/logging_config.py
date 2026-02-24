import logging
import logging.config
import re
from core.config import config
from core.context import get_request_id

class RequestIDFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id()
        return True

class SensitiveDataFilter(logging.Filter):
    SENSITIVE_KEYS = (
        "credentials", "authorization", "token", "password", "access_token",
    )
    TOKEN_PATTERN = rf"token=([^;]+)"

    def filter(self, record):
        try:
            record.args = self.mask_sensitive_args(record.args)
            record.msg = self.mask_sensitive_msg(record.msg)
            return True
        except Exception:
            return True

    def mask_sensitive_args(self, args):
        if isinstance(args, dict):
            new_args = args.copy()
            for key in args.keys():
                if key.lower() in self.SENSITIVE_KEYS:
                    new_args[key] = "******"
                else:
                    new_args[key] = self.mask_sensitive_msg(args[key])
            return new_args
        return tuple([self.mask_sensitive_msg(arg) for arg in args])

    def mask_sensitive_msg(self, message):
        if isinstance(message, dict):
            return self.mask_sensitive_args(message)
        if isinstance(message, str):
            replace = "token=******"
            message = re.sub(self.TOKEN_PATTERN, replace, message)
        return message

active_handlers = ["console"]
# Replace 'ENVIRONMENT' with whatever attribute your config uses (e.g., 'ENV')
if config.ENV.lower() in ["dev", "development"]:
    active_handlers.append("file")

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(levelname)s] - %(asctime)s - [%(request_id)s] - %(name)s - %(message)s",
        },
        "standard": {
        "fmt": "[%(asctime)s] [%(request_id)s] %(message)s",
        },
    },
    "filters": {
        "request_id": {"()": RequestIDFilter},
        "sensitive_data_filter": {
            "()": SensitiveDataFilter, 
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
            "filters": ["request_id","sensitive_data_filter"],
        },
        "file": {
            "formatter": "standard",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f'{config.CENTRAL_LOG_FILE_PATH}/{config.CENTRAL_LOG_FILE_NAME}',
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 5,            
            "level": "INFO",
            "filters": ["request_id", "sensitive_data_filter"],
        },
    },
    "loggers": {
        config.CENTRAL_LOGGER_NAME: {
            "handlers": active_handlers,
            "level": "DEBUG",
            "propagate": False,
        }
    },
}