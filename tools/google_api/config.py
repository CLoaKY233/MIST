"""
Common configuration settings for Google API services.
"""

import json
import os
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from tools.google_api.client import (
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_TOKEN_PATH,
    GOOGLE_API_SCOPES,
)


class GoogleApiSettings(BaseSettings):
    """
    Settings model for Google API configuration.
    """

    credentials_path: str = DEFAULT_CREDENTIALS_PATH
    token_path: str = DEFAULT_TOKEN_PATH
    scopes: List[str] = GOOGLE_API_SCOPES
    user_id: str = "me"  # For Gmail and similar services
    max_results: int = 10

    # Configure environment variable settings
    model_config = SettingsConfigDict(
        env_prefix="MIST_GOOGLE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


def get_settings(config_file: Optional[str] = None) -> GoogleApiSettings:
    """
    Get settings instance, optionally loaded from a config file.

    Args:
        config_file: Path to a JSON configuration file (optional)

    Returns:
        Settings instance
    """
    settings = GoogleApiSettings()

    # Override with config file if provided
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                file_config = json.load(f)
                settings = GoogleApiSettings.model_validate(file_config)
        except json.JSONDecodeError:
            # If JSON is invalid, return default settings
            pass

    return settings


# Create a default settings instance
settings = get_settings()
