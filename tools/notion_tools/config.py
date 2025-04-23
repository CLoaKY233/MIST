"""
Configuration settings for Notion API integration.
"""

import os
import json
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Find and load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
if os.path.exists(env_path):
    load_dotenv(env_path)

# Notion API configuration
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_API_VERSION = "2022-02-22"
NOTION_BASE_URL = "https://api.notion.com/v1"

# Default settings
DEFAULT_PAGE_SIZE = 100

# For easier imports
settings = {
    "api_key": NOTION_API_KEY,
    "api_version": NOTION_API_VERSION,
    "base_url": NOTION_BASE_URL,
    "page_size": DEFAULT_PAGE_SIZE
}