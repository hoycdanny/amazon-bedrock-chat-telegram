"""
Centralized configuration management with Pydantic models.
Supports environment variables and YAML file configuration.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with validation and environment variable support.
    Configuration priority: Environment Variables > Default values
    """
    
    # Telegram Settings
    telegram_bot_token: str = Field(..., description="Telegram bot token", alias="TELEGRAM_BOT_TOKEN")
    
    # bedrock-chat API Settings
    bedrock_chat_api_url: str = Field(..., description="bedrock-chat API base URL", alias="BEDROCK_CHAT_API_URL")
    bedrock_chat_api_token: Optional[str] = Field(None, description="API authentication token", alias="BEDROCK_CHAT_API_TOKEN")
    bedrock_chat_timeout: int = Field(30, description="API request timeout in seconds", alias="BEDROCK_CHAT_TIMEOUT")
    
    # Authorization Settings
    authorized_users: str = Field("", description="Comma-separated authorized user IDs", alias="AUTHORIZED_USERS")
    
    # System Settings
    log_level: str = Field("INFO", description="Logging level", alias="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # 忽略額外的環境變數
        populate_by_name = True  # 允許使用別名
    
    @field_validator("telegram_bot_token")
    @classmethod
    def validate_bot_token(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Invalid Telegram bot token")
        return v
    
    @field_validator("bedrock_chat_api_url")
    @classmethod
    def validate_api_url(cls, v):
        if not v or not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Invalid bedrock-chat API URL")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    

    
    @property
    def authorized_user_list(self) -> List[int]:
        """Convert comma-separated user IDs to list of integers."""
        if not self.authorized_users:
            return []
        try:
            return [int(uid.strip()) for uid in self.authorized_users.split(",") if uid.strip()]
        except ValueError:
            raise ValueError("Invalid user ID in authorized_users")


def load_config() -> Settings:
    """
    Load configuration from environment variables.
        
    Returns:
        Settings: Validated configuration object
        
    Raises:
        ValueError: If configuration validation fails
    """
    try:
        return Settings()
    except Exception as e:
        raise ValueError(f"Configuration validation failed: {e}")

