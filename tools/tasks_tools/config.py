"""
Configuration settings for the MCP Tasks server.
"""

import json
import os
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


from tools.tasks_tools.tasks import (
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_TOKEN_PATH,
    DEFAULT_USER_ID,
    TASKS_SCOPES,
)

class Settings(BaseSettings):
    """Settings model for MCP Tasks server configuration."""
    credentials_path: str = DEFAULT_CREDENTIALS_PATH
    token_path: str = DEFAULT_TOKEN_PATH
    scopes: List[str] = TASKS_SCOPES
    user_id: str = DEFAULT_USER_ID
    max_results: int = 10

    model_config = SettingsConfigDict(
        env_prefix="MCP_GMAIL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

def get_settings(config_file: Optional[str] = None) -> Settings:
    """
    Get settings instance, optionally loaded from a config file.

    Args:
        config_file: Path to a JSON configuration file (optional)

    Returns:
        Settings instance
    """
    settings = Settings()

    # Override with config file if provided
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                settings = Settings.model_validate(file_config)
        except json.JSONDecodeError:
            # If JSON is invalid, return default settings
            pass

    return settings

# Create a default settings instance
settings = get_settings()
