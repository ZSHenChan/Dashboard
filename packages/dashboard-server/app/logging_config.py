import logging, os
import logging.config
import re
from core.config import config
from core.context import get_request_id

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = get_request_id() or "-"
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

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(levelname)s] - %(asctime)s - %(name)s - Session[%(request_id)s] - %(message)s",
        },
        "standard": {
        "fmt": "[%(asctime)s] [%(request_id)s] %(message)s",
        },
    },
    "filters": {
        "sensitive_data_filter": {
            "()": SensitiveDataFilter, 
        },
        "request_id_filter": {
            "()": RequestIdFilter, 
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
            "filters": ["sensitive_data_filter","request_id_filter"],
        },
    },
    "loggers": {
        config.CENTRAL_LOGGER_NAME: {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
}

ENVIRONMENT = config.ENV

if ENVIRONMENT == "development":
    os.makedirs(config.CENTRAL_LOG_FILE_PATH, exist_ok=True)
    
    LOGGING_CONFIG["handlers"]["file"] = {
        "formatter": "standard",
        "class": "logging.handlers.RotatingFileHandler",
        "filename": f'{config.CENTRAL_LOG_FILE_PATH}/{config.CENTRAL_LOG_FILE_NAME}',
        "maxBytes": 10 * 1024 * 1024,
        "backupCount": 5,            
        "level": "INFO",
        "filters": ["sensitive_data_filter","request_id_filter"],
    }
    
    LOGGING_CONFIG["loggers"][config.CENTRAL_LOGGER_NAME]["handlers"].append("file")