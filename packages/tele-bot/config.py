from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    tele_api_id: int = Field(validation_alias='telegram_api_id')
    tele_api_hash: SecretStr = Field(validation_alias='telegram_api_hash')

    gemini_api_key: SecretStr = Field(validation_alias='gemini_api_key')

    redis_url: SecretStr = Field(validation_alias='redis_url')
    redis_port: int = Field(validation_alias='redis_port')
    redis_password: SecretStr = Field(validation_alias='redis_password')
    
    # App Settings
    omit_group_messages: bool = False
    debounce_buffer_sec: int = 15
    
    gemini_model: str = "gemini-3-pro-preview"

    # Metadata and env-file support
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Instantiate once and use everywhere
settings = Settings()