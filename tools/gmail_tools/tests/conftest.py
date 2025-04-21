"""
Pytest configuration for MCP Gmail tests.
"""

import json
import os
import tempfile
from typing import Generator

import pytest

from config import Settings, get_settings


@pytest.fixture
def temp_config_file() -> Generator[str, None, None]:
    """
    Create a temporary config file for testing.

    Returns:
        Path to the temporary config file
    """
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as temp_file:
        config_data = {
            "credentials_path": "test_creds.json",
            "token_path": "test_token.json",
            "max_results": 20,
        }
        temp_file.write(json.dumps(config_data).encode("utf-8"))
        temp_path = temp_file.name

    yield temp_path

    # Clean up after the test
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def test_settings(temp_config_file: str) -> Settings:
    """
    Create a Settings instance using a temporary config file.

    Args:
        temp_config_file: Path to a temporary config file

    Returns:
        Configured Settings instance
    """
    return get_settings(temp_config_file)
