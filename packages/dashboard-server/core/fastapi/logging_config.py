# logger_config.py
import logging
import logging.config
import re

# 1. Define the Filter Class FIRST
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

# 2. Define the Config Dictionary SECOND
# This references the class defined above
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "[%(levelname)s] - %(asctime)s - %(name)s - %(message)s",
        },
    },
    "filters": {
        "sensitive_data_filter": {
            # We reference the class directly here
            "()": SensitiveDataFilter, 
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
            "stream": "ext://sys.stdout",
            "filters": ["sensitive_data_filter"],
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "filename": "my_log.log",
            "mode": "a",
            # Add filters here if you want the file masked too
            "filters": ["sensitive_data_filter"], 
        },
    },
    "loggers": {
        "my_customer_logger": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        }
    },
}