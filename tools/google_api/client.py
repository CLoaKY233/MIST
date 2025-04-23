"""
Common Google API client utilities for authentication and service creation.
"""

import json
import os
from typing import Any, List, Union

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.external_account_authorized_user import (
    Credentials as ExternalCredentials,
)
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Default settings
DEFAULT_CREDENTIALS_PATH = "credentials.json"
DEFAULT_TOKEN_PATH = "token.json"

# Common scopes across services
GOOGLE_API_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.labels",                           # Read, compose, send and permanently delete all your email from Gmail
    "https://www.googleapis.com/auth/tasks",                # Create, edit, organize and delete all your tasks
    "https://www.googleapis.com/auth/tasks.readonly",       # View your tasks
]


# Define a type for the credentials that could be returned
GoogleCredentials = Union[Credentials, ExternalCredentials]


def get_credentials(
    credentials_path: str = DEFAULT_CREDENTIALS_PATH,
    token_path: str = DEFAULT_TOKEN_PATH,
    scopes: List[str] = GOOGLE_API_SCOPES,
) -> GoogleCredentials:
    """
    Get Google OAuth credentials for API services.

    Args:
        credentials_path: Path to the credentials JSON file
        token_path: Path to save/load the token
        scopes: OAuth scopes to request

    Returns:
        Google OAuth credentials
    """
    creds = None

    # Look for token file with stored credentials
    if os.path.exists(token_path):
        try:
            with open(token_path, "r") as token:
                token_data = json.load(token)
                creds = Credentials.from_authorized_user_info(token_data)
        except json.JSONDecodeError:
            print(
                f"Warning: Token file at {token_path} is invalid or empty. Will re-authenticate."
            )

    # If credentials don't exist or are invalid, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if credentials file exists
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    "Please download your OAuth credentials from Google Cloud Console."
                )

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)

        # Save credentials for future runs
        token_json = json.loads(creds.to_json())
        with open(token_path, "w") as token:
            json.dump(token_json, token)

    return creds


def get_google_service(
    service_name: str,
    version: str,
    credentials_path: str = DEFAULT_CREDENTIALS_PATH,
    token_path: str = DEFAULT_TOKEN_PATH,
    scopes: List[str] = GOOGLE_API_SCOPES,
) -> Any:
    """
    Get an authenticated Google API service.

    Args:
        service_name: Name of the Google service (e.g., 'gmail', 'tasks')
        version: API version (e.g., 'v1')
        credentials_path: Path to the credentials JSON file
        token_path: Path to save/load the token
        scopes: OAuth scopes to request

    Returns:
        Authenticated Google API service
    """
    creds = get_credentials(credentials_path, token_path, scopes)
    return build(service_name, version, credentials=creds)
