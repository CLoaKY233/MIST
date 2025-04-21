"""
Configuration settings for the MCP Gmail server.
"""

import json
import os
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Import default settings from gmail module
from tools.gmail_tools.gmail import (
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_TOKEN_PATH,
    DEFAULT_USER_ID,
    GMAIL_SCOPES,
)


class Settings(BaseSettings):
    """
    Settings model for MCP Gmail server configuration.

    Automatically reads from environment variables with MCP_GMAIL_ prefix.
    """

    credentials_path: str = DEFAULT_CREDENTIALS_PATH
    token_path: str = DEFAULT_TOKEN_PATH
    scopes: List[str] = GMAIL_SCOPES
    user_id: str = DEFAULT_USER_ID
    max_results: int = 10

    # Configure environment variable settings
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
    Uses LRU cache for performance.

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
