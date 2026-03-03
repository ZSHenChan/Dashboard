from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    tele_api_id: int = Field(validation_alias='telegram_api_id')
    tele_api_hash: SecretStr = Field(validation_alias='telegram_api_hash')

    gemini_api_key: SecretStr = Field(validation_alias='gemini_api_key')
    mem0ai_api_key: SecretStr = Field(validation_alias='mem0ai_api_key')

    redis_url: str = Field(validation_alias='redis_url')
    
    # App Settings
    omit_group_messages: bool = False
    debounce_buffer_sec: int = 45
    
    gemini_model: str = "gemini-3-pro-preview"

    ml_flow_host: str = 'localhost'
    ml_flow_port: int = 6600
    ml_flow_prompt_reply: str = 'Reply-Prompt'
    ml_flow_prompt_style: str = 'Reply-Style'
    ml_flow_sys_reply: str = 'Sys-Generate-Reply'
    ml_flow_sys_tools: str = 'Sys-Tools'
    ml_flow_sys_summary: str = 'Sys-Summary'

    # Metadata and env-file support
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Instantiate once and use everywhere
settings = Settings()