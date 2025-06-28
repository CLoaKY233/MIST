"""
Tasks MCP Server Implementation

This module provides a Model Context Protocol server for interacting with Google Tasks.
It exposes Tasks as resources and provides tools for managing tasks and task lists.
"""

from typing import Any

from tools.tasks_tools.tasks import (
    complete_task,
    create_task,
    create_task_list,
    delete_task,
    delete_task_list,
    get_tasks,
    get_tasks_service,
    list_task_lists,
    update_task,
)

service = get_tasks_service()


# Resources
def get_task_list(task_list_id: str) -> str:
    """
    Get all tasks in a task list by its ID.

    Args:
        task_list_id: ID of the task list

    Returns:
        Formatted string with task list details
    """
    tasks = get_tasks(service, task_list_id)
    result = f"Task List (ID: {task_list_id})\n"

    if not tasks:
        return result + "\nNo tasks found in this list."

    for task in tasks:
        result += f"\nTitle: {task.get('title', 'Untitled')}\n"
        result += f"Status: {task.get('status', 'Unknown')}\n"
        if task.get("notes"):
            result += f"Notes: {task.get('notes')}\n"
        if task.get("due"):
            result += f"Due: {task.get('due')}\n"
    return result


def get_task(task_list_id: str, task_id: str) -> str:
    """
    Get details of a specific task.

    Args:
        task_list_id: ID of the task list
        task_id: ID of the task

    Returns:
        Formatted string with task details
    """
    task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()
    result = f"Task (ID: {task_id})\n"
    result += f"Title: {task.get('title', 'Untitled')}\n"
    result += f"Status: {task.get('status', 'Unknown')}\n"
    if task.get("notes"):
        result += f"Notes: {task.get('notes')}\n"
    if task.get("due"):
        result += f"Due: {task.get('due')}\n"
    return result


# Tools
def list_task_lists_tool() -> str:
    """
    List all task lists available to the user.

    Returns:
        Formatted string with all task lists
    """
    task_lists = list_task_lists(service)

    if not task_lists:
        return "No task lists found."

    result = f"Found {len(task_lists)} task lists:\n"
    for task_list in task_lists:
        result += f"\nTitle: {task_list.get('title', 'Untitled')}\n"
        result += f"ID: {task_list.get('id', 'Unknown')}\n"
    return result


def create_task_tool(
    task_list_id: str,
    title: str,
    notes: str = "",
    due: str = "",
) -> str:
    """
    Create a new task in a specified task list.

    Args:
        task_list_id: ID of the task list
        title: Title of the new task
        notes: Additional notes for the task (defaults to empty string)
        due: Due date for the task in RFC 3339 format (defaults to empty string)

    Returns:
        Confirmation message with task details
    """
    task = create_task(service, task_list_id, title, notes, due)
    return f"""
Task created successfully:
ID: {task.get("id", "Unknown")}
Title: {title}
Notes: {notes or ""}
Due: {due or "Not specified"}
"""


def update_task_tool(
    task_list_id: str,
    task_id: str,
    title: str = "",
    notes: str = "",
    due: str = "",
) -> str:
    """
    Update an existing task.

    Args:
        task_list_id: ID of the task list
        task_id: ID of the task to update
        title: New title for the task (defaults to empty string)
        notes: New notes for the task (defaults to empty string)
        due: New due date for the task in RFC 3339 format (defaults to empty string)

    Returns:
        Confirmation message with updated task details
    """
    task = update_task(service, task_list_id, task_id, title, notes, due)

    result = f"Task updated successfully (ID: {task_id}):\n"
    result += f"Title: {task.get('title', 'Untitled')}\n"
    result += f"Status: {task.get('status', 'Unknown')}\n"
    if task.get("notes"):
        result += f"Notes: {task.get('notes')}\n"
    if task.get("due"):
        result += f"Due: {task.get('due')}\n"
    return result


def complete_task_tool(task_list_id: str, task_id: str) -> str:
    """
    Mark a task as completed.

    Args:
        task_list_id: ID of the task list
        task_id: ID of the task to complete

    Returns:
        Confirmation message
    """
    task = complete_task(service, task_list_id, task_id)
    return (
        f"Task '{task.get('title', 'Untitled')}' (ID: {task_id}) marked as completed."
    )


def delete_task_tool(task_list_id: str, task_id: str) -> str:
    """
    Delete a task.

    Args:
        task_list_id: ID of the task list
        task_id: ID of the task to delete

    Returns:
        Confirmation message
    """
    delete_task(service, task_list_id, task_id)
    return f"Task (ID: {task_id}) deleted successfully."


def create_task_list_tool(title: str) -> str:
    """
    Create a new task list.

    Args:
        title: Title of the new task list

    Returns:
        Confirmation message with task list details
    """
    task_list = create_task_list(service, title)
    return f"""
Task list created successfully:
ID: {task_list.get("id", "Unknown")}
Title: {title}
"""


def delete_task_list_tool(task_list_id: str) -> str:
    """
    Delete a task list.

    Args:
        task_list_id: ID of the task list to delete

    Returns:
        Confirmation message
    """
    delete_task_list(service, task_list_id)
    return f"Task list (ID: {task_list_id}) deleted successfully."


# Register all tools with MCP
def register_tools_tasks(mcp: Any):
    """
    Register all tasks tools with the MCP server.
    """
    # Register tools
    mcp.tool()(list_task_lists_tool)
    mcp.tool()(create_task_tool)
    mcp.tool()(update_task_tool)
    mcp.tool()(complete_task_tool)
    mcp.tool()(delete_task_tool)
    mcp.tool()(create_task_list_tool)
    mcp.tool()(delete_task_list_tool)

    # Register resources
    mcp.resource("tasks://lists/{task_list_id}")(get_task_list)
    mcp.resource("tasks://lists/{task_list_id}/tasks/{task_id}")(get_task)
