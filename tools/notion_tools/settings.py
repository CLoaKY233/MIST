"""
Settings model for the Notion API configuration.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find and load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
if os.path.exists(env_path):
    load_dotenv(env_path)

class NotionSettings(BaseSettings):
    """
    Settings model for Notion API configuration.
    """
    api_key: str = os.getenv("NOTION_API_KEY", "")
    api_version: str = "2022-02-22"
    base_url: str = "https://api.notion.com/v1"
    page_size: int = 100

    # Configure environment variable settings
    model_config = SettingsConfigDict(
        env_prefix="MIST_NOTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

def get_settings() -> NotionSettings:
    """
    Get the settings instance for Notion API.
    
    Returns:
        NotionSettings instance
    """
    return NotionSettings()

# Create default settings instance
settings = get_settings()