import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[1]

class ServerSettings(BaseSettings):
    ENV: str = "production"
    DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    WRITER_DB_URL: str = "mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    READER_DB_URL: str = "mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi"
    JWT_SECRET_KEY: str = "fastapi"
    JWT_ALGORITHM: str = "HS256"
    
    CELERY_BROKER_URL: str = "amqp://user:bitnami@localhost:5672/"
    CELERY_BACKEND_URL: str = "redis://:password123@localhost:6379/0"

class StorageSettings(BaseSettings):
    S3_BUCKET_NAME: str = 'tele-bot-storage'
    AWS_ACCESS_KEY_ID: str = 'AWS_ACCESS_KEY_ID'
    AWS_SECRET_ACCESS_KEY: str = 'AWS_SECRET_ACCESS_KEY'

class DatabaseSettings(BaseSettings):
    REDIS_URL: str = 'YOUR_REDIS_URL'
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: str = '6379'
    REDIS_PASSWORD: str = 'REDIS_PASSWORD_DEFAULT'
    MONGODB_URL: str = 'MONGODB_URL'
    MONGODB_AGENT: str = 'tele_agent_db'
    MONGODB_LOGS: str = 'training_logs'

class LoggingSettings(BaseSettings):
    CENTRAL_LOG_FILE_NAME: str = "server.log"
    CENTRAL_LOG_FILE_PATH: str = "server_logs"
    CENTRAL_LOGGER_NAME: str = "server_logger"
    SESSION_LOGGER_NAME: str = "session"
    SESSION_LOG_FILE_PATH: str = "session_logs"
    SESS_LOG_FORMAT: str = "%(asctime)s - %(levelname)s - [%(request_id)s] [%(filename)s:%(lineno)d] - %(message)s"
    SENTRY_DSN: str = 'https://YOUR_SENTRY_URL.ingest.us.sentry.io/SOME_NUMBERS_HERE'

class SecuritySettings(BaseSettings):
    RATE_LIMIT_LIMIT: int = 50 # Max requests
    RATE_LIMIT_PERIOD: int = 60 # Seconds

class BaseConfig(
    ServerSettings,
    DatabaseSettings,
    StorageSettings,
    LoggingSettings,
    SecuritySettings,
    BaseSettings
):
    """
    Master Config class inheriting from all Mixins.
    """
    model_config = SettingsConfigDict(
        env_file=str(ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


class TestConfig(BaseConfig):
    WRITER_DB_URL: str = "mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi_test"
    READER_DB_URL: str = "mysql+aiomysql://fastapi:fastapi@localhost:3306/fastapi_test"


class LocalConfig(BaseConfig):
    ...


class ProductionConfig(BaseConfig):
    DEBUG: bool = False



def get_config() -> BaseConfig:
    env = os.getenv("ENV", "local")
    config_type = {
        "test": TestConfig(),
        "local": LocalConfig(),
        "prod": ProductionConfig(),
    }
    return config_type[env]


config = get_config()
