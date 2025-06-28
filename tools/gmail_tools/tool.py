"""
Gmail MCP Server Implementation

This module provides a Model Context Protocol server for interacting with Gmail.
It exposes Gmail messages as resources and provides tools for composing and sending emails.
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

from tools.gmail_tools.config import settings as gmail_settings
from tools.gmail_tools.gmail import (
    create_draft,
    get_gmail_service,
    get_headers_dict,
    get_labels,
    get_message,
    get_thread,
    list_messages,
    modify_message_labels,
    parse_message_body,
    search_messages,
)
from tools.gmail_tools.gmail import send_email as gmail_send_email
from tools.google_api import settings

service = get_gmail_service()
EMAIL_PREVIEW_LENGTH = 200


def format_message(message: Dict[str, Any]) -> str:
    """Format a Gmail message for display."""
    headers = get_headers_dict(message)
    body = parse_message_body(message)

    # Extract relevant headers
    from_header = headers.get("From", "Unknown")
    to_header = headers.get("To", "Unknown")
    subject = headers.get("Subject", "No Subject")
    date = headers.get("Date", "Unknown Date")

    return f"""
From: {from_header}
To: {to_header}
Subject: {subject}
Date: {date}

{body}
"""


def validate_date_format(date_str: str) -> bool:
    """
    Validate that a date string is in the format YYYY/MM/DD.

    Args:
        date_str: The date string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not date_str:
        return True

    # Check format with regex
    if not re.match(r"^\d{4}/\d{2}/\d{2}$", date_str):
        return False

    # Validate the date is a real date
    try:
        datetime.strptime(date_str, "%Y/%m/%d")
        return True
    except ValueError:
        return False


# Resources
def get_email_message(message_id: str) -> str:
    """
    Get the content of an email message by its ID.

    Args:
        message_id: The Gmail message ID

    Returns:
        The formatted email content
    """
    message = get_message(service, message_id, user_id=settings.user_id)
    formatted_message = format_message(message)
    return formatted_message


def get_email_thread(thread_id: str) -> str:
    """
    Get all messages in an email thread by thread ID.

    Args:
        thread_id: The Gmail thread ID

    Returns:
        The formatted thread content with all messages
    """
    thread = get_thread(service, thread_id, user_id=settings.user_id)
    messages = thread.get("messages", [])

    result = f"Email Thread (ID: {thread_id})\n"
    for i, message in enumerate(messages, 1):
        result += f"\n--- Message {i} ---\n"
        result += format_message(message)

    return result


# Tools


def compose_email(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
) -> str:
    """
    Compose a new email draft.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: Carbon copy recipients (defaults to empty string)
        bcc: Blind carbon copy recipients (defaults to empty string)

    Returns:
        The ID of the created draft and its content
    """
    sender = (
        service.users()
        .getProfile(userId=settings.user_id)
        .execute()
        .get("emailAddress")
    )
    draft = create_draft(
        service,
        sender=sender,
        to=to,
        subject=subject,
        body=body,
        user_id=settings.user_id,
        cc=cc,
        bcc=bcc,
    )

    draft_id = draft.get("id")
    return f"""
Email draft created with ID: {draft_id}
To: {to}
Subject: {subject}
CC: {cc or ""}
BCC: {bcc or ""}
Body: {body[:EMAIL_PREVIEW_LENGTH]}{"..." if len(body) > EMAIL_PREVIEW_LENGTH else ""}
"""


def send_email(
    to: str,
    subject: str,
    body: str,
    cc: str = "",
    bcc: str = "",
) -> str:
    """
    Compose and send an email.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: Carbon copy recipients (defaults to empty string)
        bcc: Blind carbon copy recipients (defaults to empty string)

    Returns:
        Content of the sent email
    """
    sender = (
        service.users()
        .getProfile(userId=settings.user_id)
        .execute()
        .get("emailAddress")
    )
    message = gmail_send_email(
        service,
        sender=sender,
        to=to,
        subject=subject,
        body=body,
        user_id=settings.user_id,
        cc=cc,
        bcc=bcc,
    )

    message_id = message.get("id")
    return f"""
Email sent successfully with ID: {message_id}
To: {to}
Subject: {subject}
CC: {cc or ""}
BCC: {bcc or ""}
Body: {body[:EMAIL_PREVIEW_LENGTH]}{"..." if len(body) > EMAIL_PREVIEW_LENGTH else ""}
"""


def search_emails(
    from_email: str = "",
    to_email: str = "",
    subject: str = "",
    has_attachment: bool = False,
    is_unread: bool = False,
    after_date: str = "",
    before_date: str = "",
    label: str = "",
    max_results: int = 10,
) -> str:
    """
    Search for emails using specific search criteria.

    Args:
        from_email: Filter by sender email (defaults to empty string)
        to_email: Filter by recipient email (defaults to empty string)
        subject: Filter by subject text (defaults to empty string)
        has_attachment: Filter for emails with attachments
        is_unread: Filter for unread emails
        after_date: Filter for emails after this date (format: YYYY/MM/DD, defaults to empty string)
        before_date: Filter for emails before this date (format: YYYY/MM/DD, defaults to empty string)
        label: Filter by Gmail label (defaults to empty string)
        max_results: Maximum number of results to return

    Returns:
        Formatted list of matching emails
    """
    # Validate date formats
    if after_date and not validate_date_format(after_date):
        return (
            f"Error: after_date '{after_date}' is not in the required format YYYY/MM/DD"
        )

    if before_date and not validate_date_format(before_date):
        return f"Error: before_date '{before_date}' is not in the required format YYYY/MM/DD"

    # Use search_messages to find matching emails
    messages = search_messages(
        service,
        user_id=settings.user_id,
        from_email=from_email if from_email else None,
        to_email=to_email if to_email else None,
        subject=subject if subject else None,
        has_attachment=has_attachment,
        is_unread=is_unread,
        after=after_date if after_date else None,
        before=before_date if before_date else None,
        labels=[label] if label and label.strip() else None,
        max_results=max_results,
    )

    result = f"Found {len(messages)} messages matching criteria:\n"

    for msg_info in messages:
        msg_id = msg_info.get("id")
        if msg_id is None:
            continue

        # Get full message details to properly retrieve headers
        message = get_message(service, msg_id, user_id=settings.user_id)
        headers = get_headers_dict(message)

        # Extract headers with proper error handling
        from_header = headers.get("From", "Unknown")
        subject_header = headers.get("Subject", "No Subject")
        date_header = headers.get("Date", "Unknown Date")

        # Get snippet for preview
        snippet = message.get("snippet", "")

        result += f"\nMessage ID: {msg_id}\n"
        result += f"From: {from_header}\n"
        result += f"Subject: {subject_header}\n"
        result += f"Date: {date_header}\n"
        if snippet:
            result += f"Preview: {snippet}\n"

    return result


def query_emails(query: str, max_results: int = 10) -> str:
    """
    Search for emails using a raw Gmail query string.

    Args:
        query: Gmail search query (same syntax as Gmail search box)
        max_results: Maximum number of results to return

    Returns:
        Formatted list of matching emails
    """
    messages = list_messages(
        service, user_id=settings.user_id, max_results=max_results, query=query
    )

    result = f'Found {len(messages)} messages matching query: "{query}"\n'

    for msg_info in messages:
        msg_id = msg_info.get("id")
        if msg_id is None:
            continue

        # Get full message details to properly retrieve headers
        message = get_message(service, msg_id, user_id=settings.user_id)
        headers = get_headers_dict(message)

        # Extract headers with proper error handling
        from_header = headers.get("From", "Unknown")
        subject_header = headers.get("Subject", "No Subject")
        date_header = headers.get("Date", "Unknown Date")

        # Get snippet for preview
        snippet = message.get("snippet", "")

        result += f"\nMessage ID: {msg_id}\n"
        result += f"From: {from_header}\n"
        result += f"Subject: {subject_header}\n"
        result += f"Date: {date_header}\n"
        if snippet:
            result += f"Preview: {snippet}\n"

    return result


def list_available_labels() -> str:
    """
    Get all available Gmail labels for the user.

    Returns:
        Formatted list of labels with their IDs
    """
    labels = get_labels(service, user_id=settings.user_id)

    result = "Available Gmail Labels:\n"
    for label in labels:
        label_id = label.get("id", "Unknown")
        name = label.get("name", "Unknown")
        type_info = label.get("type", "user")

        result += f"\nLabel ID: {label_id}\n"
        result += f"Name: {name}\n"
        result += f"Type: {type_info}\n"

    return result


def mark_message_read(message_id: str) -> str:
    """
    Mark a message as read by removing the UNREAD label.

    Args:
        message_id: The Gmail message ID to mark as read

    Returns:
        Confirmation message
    """
    # Remove the UNREAD label
    result = modify_message_labels(
        service,
        user_id=settings.user_id,
        message_id=message_id,
        remove_labels=["UNREAD"],
        add_labels=[],
    )

    # Get message details to show what was modified
    headers = get_headers_dict(result)
    subject = headers.get("Subject", "No Subject")

    return f"""
Message marked as read:
ID: {message_id}
Subject: {subject}
"""


def add_label_to_message(message_id: str, label_id: str) -> str:
    """
    Add a label to a message.

    Args:
        message_id: The Gmail message ID
        label_id: The Gmail label ID to add (use list_available_labels to find label IDs)

    Returns:
        Confirmation message
    """
    # Add the specified label
    result = modify_message_labels(
        service,
        user_id=settings.user_id,
        message_id=message_id,
        remove_labels=[],
        add_labels=[label_id],
    )

    # Get message details to show what was modified
    headers = get_headers_dict(result)
    subject = headers.get("Subject", "No Subject")

    # Get the label name for the confirmation message
    label_name = label_id
    labels = get_labels(service, user_id=settings.user_id)
    for label in labels:
        if label.get("id") == label_id:
            label_name = label.get("name", label_id)
            break

    return f"""
Label added to message:
ID: {message_id}
Subject: {subject}
Added Label: {label_name} ({label_id})
"""


def remove_label_from_message(message_id: str, label_id: str) -> str:
    """
    Remove a label from a message.

    Args:
        message_id: The Gmail message ID
        label_id: The Gmail label ID to remove (use list_available_labels to find label IDs)

    Returns:
        Confirmation message
    """
    # Get the label name before we remove it
    label_name = label_id
    labels = get_labels(service, user_id=settings.user_id)
    for label in labels:
        if label.get("id") == label_id:
            label_name = label.get("name", label_id)
            break

    # Remove the specified label
    result = modify_message_labels(
        service,
        user_id=settings.user_id,
        message_id=message_id,
        remove_labels=[label_id],
        add_labels=[],
    )

    # Get message details to show what was modified
    headers = get_headers_dict(result)
    subject = headers.get("Subject", "No Subject")

    return f"""
Label removed from message:
ID: {message_id}
Subject: {subject}
Removed Label: {label_name} ({label_id})
"""


def get_emails(message_ids: list[str]) -> str:
    """
    Get the content of multiple email messages by their IDs.

    Args:
        message_ids: A list of Gmail message IDs

    Returns:
        The formatted content of all requested emails
    """
    if not message_ids:
        return "No message IDs provided."

    # Fetch all emails first
    # Retrieve the initial message IDs
    retrieved_emails: List[Tuple[str, Dict[str, Any]]] = []
    error_emails: List[Tuple[str, str]] = []

    # Try to get each message
    for msg_id in message_ids:
        try:
            message = get_message(service, msg_id, user_id=gmail_settings.user_id)
            retrieved_emails.append((msg_id, message))
        except Exception as e:
            error_emails.append((msg_id, str(e)))

    # Build result string after fetching all emails
    result = f"Retrieved {len(retrieved_emails)} emails:\n"

    # Format all successfully retrieved emails
    for i, (msg_id, message) in enumerate(retrieved_emails, 1):
        result += f"\n--- Email {i} (ID: {msg_id}) ---\n"
        result += format_message(message)

    # Report any errors
    if error_emails:
        result += f"\n\nFailed to retrieve {len(error_emails)} emails:\n"
        for i, (msg_id, error) in enumerate(error_emails, 1):
            result += f"\n--- Email {i} (ID: {msg_id}) ---\n"
            result += f"Error: {error}\n"

    return result


def register_tools_mail(mcp: Any) -> None:
    """Register all mail tools with the MCP server."""
    mcp.tool()(get_emails)
    mcp.tool()(remove_label_from_message)
    mcp.tool()(add_label_to_message)
    mcp.tool()(list_available_labels)
    mcp.tool()(query_emails)
    mcp.tool()(search_emails)
    mcp.tool()(send_email)
    mcp.tool()(compose_email)
    mcp.tool()(mark_message_read)

    # Register resources
    mcp.resource("gmail://threads/{thread_id}")(get_email_thread)
    mcp.resource("gmail://messages/{message_id}")(get_email_message)
