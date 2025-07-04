"""
Google API common utilities for various services.
"""

from .client import (
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_TOKEN_PATH,
    GOOGLE_API_SCOPES,
    get_credentials,
    get_google_service,
)
from .config import GoogleApiSettings, get_settings, settings

__all__ = [
    "get_credentials",
    "get_google_service",
    "GOOGLE_API_SCOPES",
    "DEFAULT_CREDENTIALS_PATH",
    "DEFAULT_TOKEN_PATH",
    "GoogleApiSettings",
    "get_settings",
    "settings",
]
