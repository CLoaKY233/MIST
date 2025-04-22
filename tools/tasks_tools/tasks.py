"""
This module provides utilities for authenticating with and using the Google Tasks API.
"""

import base64
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional, TypeVar, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build


DEFAULT_CREDENTIALS_PATH = "credentials.json"
DEFAULT_TOKEN_PATH = "token.json"
DEFAULT_USER_ID = "me"

TASKS_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/tasks"
]

TaskService=Any

def get_tasks_service(
    credentials_path: str = DEFAULT_CREDENTIALS_PATH,
    token_path: str = DEFAULT_TOKEN_PATH,
    scopes: List[str] = TASKS_SCOPES,
) -> Any:
    """
    Authenticate with Tasks API and return the service object.

    Args:
        credentials_path: Path to the credentials JSON file
        token_path: Path to save/load the token
        scopes: OAuth scopes to request

    Returns:
        Authenticated Tasks API service
    """
    creds = None

    # Look for token file with stored credentials
    if os.path.exists(token_path):
        try:
            with open(token_path, "r") as token:
                token_data = json.load(token)
                creds = Credentials.from_authorized_user_info(token_data)
        except json.JSONDecodeError:
            print(f"Warning: Token file at {token_path} is invalid or empty. Will re-authenticate.")

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

    # Build the Tasks service
    return build("tasks", "v1", credentials=creds)

def list_task_lists(service: Any, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    List all task lists for the user.

    Args:
        service: Tasks API service instance
        max_results: Maximum number of task lists to return

    Returns:
        List of task list objects
    """
    response = service.tasklists().list(maxResults=max_results).execute()
    return response.get("items", [])

def get_tasks(service: Any, task_list_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Get all tasks in a specific task list.

    Args:
        service: Tasks API service instance
        task_list_id: ID of the task list
        max_results: Maximum number of tasks to return

    Returns:
        List of task objects
    """
    response = service.tasks().list(tasklist=task_list_id, maxResults=max_results).execute()
    return response.get("items", [])

def create_task(
    service: Any,
    task_list_id: str,
    title: str,
    notes: Optional[str] = None,
    due: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task in the specified task list.

    Args:
        service: Tasks API service instance
        task_list_id: ID of the task list to add the task to
        title: Title of the new task
        notes: Additional notes for the task (optional)
        due: Due date for the task in RFC 3339 format (optional)

    Returns:
        Created task object
    """
    task_body = {
        "title": title,
    }

    # Add optional fields if provided
    if notes is not None:
        task_body["notes"] = notes
    if due is not None:
        task_body["due"] = due

    return service.tasks().insert(tasklist=task_list_id, body=task_body).execute()

def update_task(
    service: Any,
    task_list_id: str,
    task_id: str,
    title: Optional[str] = None,
    notes: Optional[str] = None,
    due: Optional[str] = None,
    status: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing task.

    Args:
        service: Tasks API service instance
        task_list_id: ID of the task list
        task_id: ID of the task to update
        title: New title for the task (optional)
        notes: New notes for the task (optional)
        due: New due date for the task in RFC 3339 format (optional)
        status: New status for the task ('needsAction' or 'completed') (optional)

    Returns:
        Updated task object
    """
    # Get the current task
    task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()

    # Update fields if provided
    if title is not None:
        task["title"] = title
    if notes is not None:
        task["notes"] = notes
    if due is not None:
        task["due"] = due
    if status is not None:
        task["status"] = status

    return service.tasks().update(tasklist=task_list_id, task=task_id, body=task).execute()

def delete_task(service: Any, task_list_id: str, task_id: str) -> None:
    """
    Delete a task.

    Args:
        service: Tasks API service instance
        task_list_id: ID of the task list
        task_id: ID of the task to delete
    """
    service.tasks().delete(tasklist=task_list_id, task=task_id).execute()

def create_task_list(service: Any, title: str) -> Dict[str, Any]:
    """
    Create a new task list.

    Args:
        service: Tasks API service instance
        title: Title of the new task list

    Returns:
        Created task list object
    """
    tasklist_body = {"title": title}
    return service.tasklists().insert(body=tasklist_body).execute()

def delete_task_list(service: Any, task_list_id: str) -> None:
    """
    Delete a task list.

    Args:
        service: Tasks API service instance
        task_list_id: ID of the task list to delete
    """
    service.tasklists().delete(tasklist=task_list_id).execute()

def complete_task(service: Any, task_list_id: str, task_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed.

    Args:
        service: Tasks API service instance
        task_list_id: ID of the task list
        task_id: ID of the task to complete

    Returns:
        Updated task object
    """
    return update_task(service, task_list_id, task_id, status="completed")
