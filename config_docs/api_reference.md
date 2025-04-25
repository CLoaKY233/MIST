# MIST API Reference

This document provides comprehensive documentation for all APIs available in the MIST (Model Intelligence System for Tasks) server.

## Note Management API

### `add_note`

Creates a new note with title, content, and optional metadata.

**Parameters:**
- `title` (string, required): The title of the note
- `content` (string, required): The main content of the note
- `subject` (string, optional): The subject or category of the note

**Returns:**
- Success message with the created note ID

**Example:**
```python
add_note(
    title="Meeting Notes",
    content="Discussed project timeline and assigned tasks to team members.",
    subject="Work"
)
```

### `read_note`

Retrieves a note by its ID or title.

**Parameters:**
- `note_id` (string, optional): The unique identifier of the note
- `title` (string, optional): The title of the note

Either `note_id` or `title` must be provided.

**Returns:**
- The full content of the note if found
- Error message if the note doesn't exist

**Example:**
```python
read_note(note_id="2023-10-15-meeting-notes-1697392485")
# or
read_note(title="Meeting Notes")
```

### `list_notes`

Lists notes, optionally filtered by subject or tag.

**Parameters:**
- `subject` (string, optional): Filter notes by this subject
- `tag` (string, optional): Filter notes by this tag
- `limit` (integer, optional): Maximum number of notes to return (default: 10)

**Returns:**
- A formatted list of notes matching the criteria

**Example:**
```python
list_notes(subject="Work", limit=5)
```

### `search_notes`

Searches notes for specific content or tags.

**Parameters:**
- `query` (string, required): The search query (can be text or a tag with # prefix)

**Returns:**
- A list of notes matching the search query

**Example:**
```python
search_notes(query="project timeline")
# or search for tags
search_notes(query="#project")
```

### `edit_note`

Updates the content of an existing note.

**Parameters:**
- `note_id` (string, required): The ID of the note to edit
- `new_content` (string, required): The new content for the note

**Returns:**
- Success message if the note was updated
- Error message if the note doesn't exist

**Example:**
```python
edit_note(
    note_id="2023-10-15-meeting-notes-1697392485",
    new_content="Updated meeting notes with action items."
)
```

### `delete_note`

Deletes a note by its ID.

**Parameters:**
- `note_id` (string, required): The ID of the note to delete

**Returns:**
- Success message if the note was deleted
- Error message if the note doesn't exist

**Example:**
```python
delete_note(note_id="2023-10-15-meeting-notes-1697392485")
```

### `generate_note_summary`

Generates a summary of a note by extracting key points.

**Parameters:**
- `note_id` (string, optional): The ID of the note to summarize
- `title` (string, optional): The title of the note to summarize

Either `note_id` or `title` must be provided.

**Returns:**
- A summary of the note with key topics and points

**Example:**
```python
generate_note_summary(note_id="2023-10-15-meeting-notes-1697392485")
```

### `organize_notes_by_subject`

Creates a summary of notes organized by subject.

**Parameters:**
- None

**Returns:**
- A hierarchical organization of notes grouped by subject

**Example:**
```python
organize_notes_by_subject()
```

## Gmail API

### `get_emails`

Retrieves emails by their IDs.

**Parameters:**
- `message_ids` (list of strings, required): List of email message IDs to retrieve

**Returns:**
- Formatted content of all requested emails

**Example:**
```python
get_emails(message_ids=["183b8e73a1c75d34", "183b8e7c132fda5b"])
```

### `search_emails`

Searches for emails using specific search criteria.

**Parameters:**
- `from_email` (string, optional): Filter by sender email
- `to_email` (string, optional): Filter by recipient email
- `subject` (string, optional): Filter by subject text
- `has_attachment` (boolean, optional): Filter for emails with attachments
- `is_unread` (boolean, optional): Filter for unread emails
- `after_date` (string, optional): Filter for emails after this date (format: YYYY/MM/DD)
- `before_date` (string, optional): Filter for emails before this date (format: YYYY/MM/DD)
- `label` (string, optional): Filter by Gmail label
- `max_results` (integer, optional): Maximum number of results (default: 10)

**Returns:**
- List of matching emails with preview information

**Example:**
```python
search_emails(
    from_email="sender@example.com",
    subject="Project Update",
    is_unread=True,
    max_results=5
)
```

### `query_emails`

Searches for emails using a raw Gmail query string.

**Parameters:**
- `query` (string, required): Gmail search query 
- `max_results` (integer, optional): Maximum number of results (default: 10)

**Returns:**
- List of matching emails with preview information

**Example:**
```python
query_emails(query="subject:(meeting) is:unread", max_results=5)
```

### `send_email`

Composes and sends an email.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body content
- `cc` (string, optional): Carbon copy recipients
- `bcc` (string, optional): Blind carbon copy recipients

**Returns:**
- Confirmation message with the sent email details

**Example:**
```python
send_email(
    to="recipient@example.com",
    subject="Meeting Invitation",
    body="Hello, I'd like to schedule a meeting to discuss our project.",
    cc="manager@example.com"
)
```

### `compose_email`

Creates a new email draft.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `body` (string, required): Email body content
- `cc` (string, optional): Carbon copy recipients
- `bcc` (string, optional): Blind carbon copy recipients

**Returns:**
- Confirmation with draft ID and details

**Example:**
```python
compose_email(
    to="recipient@example.com",
    subject="Draft: Project Proposal",
    body="Here's the draft of the project proposal we discussed."
)
```

### `list_available_labels`

Gets all available Gmail labels for the user.

**Parameters:**
- None

**Returns:**
- Formatted list of labels with their IDs

**Example:**
```python
list_available_labels()
```

### `mark_message_read`

Marks a message as read.

**Parameters:**
- `message_id` (string, required): The Gmail message ID to mark as read

**Returns:**
- Confirmation message

**Example:**
```python
mark_message_read(message_id="183b8e73a1c75d34")
```

### `add_label_to_message`

Adds a label to a message.

**Parameters:**
- `message_id` (string, required): The Gmail message ID
- `label_id` (string, required): The Gmail label ID to add

**Returns:**
- Confirmation message

**Example:**
```python
add_label_to_message(
    message_id="183b8e73a1c75d34", 
    label_id="IMPORTANT"
)
```

### `remove_label_from_message`

Removes a label from a message.

**Parameters:**
- `message_id` (string, required): The Gmail message ID
- `label_id` (string, required): The Gmail label ID to remove

**Returns:**
- Confirmation message

**Example:**
```python
remove_label_from_message(
    message_id="183b8e73a1c75d34", 
    label_id="IMPORTANT"
)
```

## Calendar API

### `list_calendars_tool`

Lists all calendars available to the user.

**Parameters:**
- None

**Returns:**
- Formatted string with all calendars and their IDs

**Example:**
```python
list_calendars_tool()
```

### `create_event_tool`

Creates a new event in a specified calendar.

**Parameters:**
- `calendar_id` (string, required): ID of the calendar
- `title` (string, required): Title of the event
- `start_datetime` (string, required): Start time in RFC3339 format (e.g., "2023-06-03T10:00:00-07:00")
- `end_datetime` (string, required): End time in RFC3339 format
- `description` (string, optional): Event description
- `location` (string, optional): Event location
- `attendees` (list of strings, optional): List of attendee email addresses
- `timezone` (string, optional): Timezone for the event

**Returns:**
- Confirmation message with event details

**Example:**
```python
create_event_tool(
    calendar_id="primary",
    title="Team Meeting",
    start_datetime="2023-10-20T14:00:00-07:00",
    end_datetime="2023-10-20T15:00:00-07:00",
    description="Weekly team sync",
    location="Conference Room A",
    attendees=["team@example.com"]
)
```

### `update_event_tool`

Updates an existing calendar event.

**Parameters:**
- `calendar_id` (string, required): ID of the calendar containing the event
- `event_id` (string, required): ID of the event to update
- `title` (string, optional): New title of the event
- `start_datetime` (string, optional): New start time in RFC3339 format
- `end_datetime` (string, optional): New end time in RFC3339 format
- `description` (string, optional): New event description
- `location` (string, optional): New event location

**Returns:**
- Confirmation message with updated event details

**Example:**
```python
update_event_tool(
    calendar_id="primary",
    event_id="abc123xyz",
    title="Updated Team Meeting",
    location="Conference Room B"
)
```

### `delete_event_tool`

Deletes a calendar event.

**Parameters:**
- `calendar_id` (string, required): ID of the calendar containing the event
- `event_id` (string, required): ID of the event to delete

**Returns:**
- Confirmation message

**Example:**
```python
delete_event_tool(
    calendar_id="primary",
    event_id="abc123xyz"
)
```

### `search_events_tool`

Searches for events in a calendar.

**Parameters:**
- `calendar_id` (string, required): ID of the calendar to search in
- `query` (string, required): Search terms to find events
- `max_results` (integer, optional): Maximum number of events to return (default: 10)
- `time_min` (string, optional): Start time in RFC3339 format
- `time_max` (string, optional): End time in RFC3339 format

**Returns:**
- Formatted list of matching events

**Example:**
```python
search_events_tool(
    calendar_id="primary",
    query="meeting",
    max_results=5
)
```

## Tasks API

### `list_task_lists_tool`

Lists all task lists available to the user.

**Parameters:**
- None

**Returns:**
- Formatted string with all task lists

**Example:**
```python
list_task_lists_tool()
```

### `create_task_tool`

Creates a new task in a specified task list.

**Parameters:**
- `task_list_id` (string, required): ID of the task list
- `title` (string, required): Title of the new task
- `notes` (string, optional): Additional notes for the task
- `due` (string, optional): Due date for the task in RFC 3339 format

**Returns:**
- Confirmation message with task details

**Example:**
```python
create_task_tool(
    task_list_id="MDAxOTg4NTI1NTIyMjM4OTU5NDI6MDow",
    title="Complete project documentation",
    notes="Include API reference and setup guide",
    due="2023-10-31T00:00:00Z"
)
```

### `update_task_tool`

Updates an existing task.

**Parameters:**
- `task_list_id` (string, required): ID of the task list
- `task_id` (string, required): ID of the task to update
- `title` (string, optional): New title for the task
- `notes` (string, optional): New notes for the task
- `due` (string, optional): New due date for the task in RFC 3339 format

**Returns:**
- Confirmation message with updated task details

**Example:**
```python
update_task_tool(
    task_list_id="MDAxOTg4NTI1NTIyMjM4OTU5NDI6MDow",
    task_id="MDAyMDM4NTI1NTIyMjM4OTU5NDI6MDow",
    notes="Added more details to documentation task"
)
```

### `complete_task_tool`

Marks a task as completed.

**Parameters:**
- `task_list_id` (string, required): ID of the task list
- `task_id` (string, required): ID of the task to complete

**Returns:**
- Confirmation message

**Example:**
```python
complete_task_tool(
    task_list_id="MDAxOTg4NTI1NTIyMjM4OTU5NDI6MDow",
    task_id="MDAyMDM4NTI1NTIyMjM4OTU5NDI6MDow"
)
```

### `delete_task_tool`

Deletes a task.

**Parameters:**
- `task_list_id` (string, required): ID of the task list
- `task_id` (string, required): ID of the task to delete

**Returns:**
- Confirmation message

**Example:**
```python
delete_task_tool(
    task_list_id="MDAxOTg4NTI1NTIyMjM4OTU5NDI6MDow",
    task_id="MDAyMDM4NTI1NTIyMjM4OTU5NDI6MDow"
)
```

### `create_task_list_tool`

Creates a new task list.

**Parameters:**
- `title` (string, required): Title of the new task list

**Returns:**
- Confirmation message with task list details

**Example:**
```python
create_task_list_tool(title="Work Projects")
```

### `delete_task_list_tool`

Deletes a task list.

**Parameters:**
- `task_list_id` (string, required): ID of the task list to delete

**Returns:**
- Confirmation message

**Example:**
```python
delete_task_list_tool(task_list_id="MDAxOTg4NTI1NTIyMjM4OTU5NDI6MDow")
```

## Resource Endpoints

MIST also provides direct access to resources through MCP resource endpoints:

### Note Resources

Currently implemented as tools rather than resources.

### Gmail Resources

- `gmail://messages/{message_id}`: Get an email message by ID
- `gmail://threads/{thread_id}`: Get all messages in an email thread

### Calendar Resources

- `calendar://calendars/{calendar_id}/events`: Get events from a specific calendar
- `calendar://calendars/{calendar_id}/events/{event_id}`: Get details of a specific calendar event

### Tasks Resources

- `tasks://lists/{task_list_id}`: Get all tasks in a task list
- `tasks://lists/{task_list_id}/tasks/{task_id}`: Get details of a specific task

## Error Handling

All API functions follow standard error handling patterns:

1. If a resource is not found (e.g., note, email, event), a clear error message is returned
2. If parameters are missing or invalid, an error message indicates the issue
3. If authentication fails, an error describing the authentication problem is returned
4. If API rate limits are exceeded, an appropriate error is returned

Most errors follow this format:
```
Error: [Error Type] - [Detailed description]
```

## Pagination

For APIs that return lists of items:

- Most list operations accept a `max_results` or `limit` parameter
- Default limits are typically 10 items
- For large result sets, consider using more specific filters