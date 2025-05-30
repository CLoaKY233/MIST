"""
Note management tools for creating, reading, updating, and deleting notes.
"""

import datetime
import json
import os
import re
import time
from typing import Any, Dict, List, Optional, cast

# Notes App Configuration
NOTES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "notes"
)
INDEX_FILE = os.path.join(NOTES_DIR, "index.json")
TAGS_FILE = os.path.join(NOTES_DIR, "tags.json")

# Type aliases for better type safety
NoteMetadata = Dict[str, Any]
TagsIndex = Dict[str, List[str]]
TagsList = List[str]


def ensure_notes_directory() -> None:
    """Create notes directory and required files if they don't exist."""
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

    # Create index file if it doesn't exist
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "w") as file:
            json.dump([], file)

    # Create tags file if it doesn't exist
    if not os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, "w") as file:
            json.dump({}, file)


def get_note_index() -> List[NoteMetadata]:
    """Load the note index."""
    with open(INDEX_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []


def save_note_index(index: List[NoteMetadata]) -> None:
    """Save the note index."""
    with open(INDEX_FILE, "w") as file:
        json.dump(index, file, indent=2)


def get_tags() -> TagsIndex:
    """Load the tags index."""
    with open(TAGS_FILE, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}


def save_tags(tags: TagsIndex) -> None:
    """Save the tags index."""
    with open(TAGS_FILE, "w") as file:
        json.dump(tags, file, indent=2)


def extract_tags(content: str) -> List[str]:
    """Extract hashtags from content."""
    # Return a list of strings explicitly to address type warnings
    return cast(List[str], re.findall(r"#(\w+)", content))


def update_tags(note_id: str, tags: List[str]) -> None:
    """Update tags index with the given tags."""
    tags_index: TagsIndex = get_tags()

    # Remove note_id from all existing tags
    for tag_list in tags_index.values():
        if note_id in tag_list:
            tag_list.remove(note_id)

    # Add note_id to the appropriate tags
    for tag in tags:
        if tag not in tags_index:
            tags_index[tag] = []
        if note_id not in tags_index[tag]:
            tags_index[tag].append(note_id)

    # Clean up empty tag entries
    tags_index = {k: v for k, v in tags_index.items() if v}

    save_tags(tags_index)


def add_note(title: str, content: str, subject: str = "") -> str:
    """
    Create a new note with a title and content.

    Args:
        title: The title of the note.
        content: The content of the note.
        subject: The subject/category of the note. Default is empty string.

    Returns:
        A success message with the created note ID.
    """
    ensure_notes_directory()

    # Generate a unique filename based on timestamp and title
    timestamp = int(time.time())
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    # Sanitize title for filename
    safe_title = (
        re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()
    )
    note_id = f"{date_str}-{safe_title}-{timestamp}"
    filename = f"{note_id}.md"
    filepath = os.path.join(NOTES_DIR, filename)

    # Extract tags from content
    tags = extract_tags(content)

    # Create note metadata
    metadata: NoteMetadata = {
        "id": note_id,
        "title": title,
        "created": timestamp,
        "modified": timestamp,
        "subject": subject if subject else None,
        "tags": tags,
        "filename": filename,
    }

    # Add formatted header to content
    formatted_content = f"# {title}\n\nDate: {date_str}\n"
    if subject and subject.strip():
        formatted_content += f"Subject: {subject}\n"
    if tags:
        formatted_content += f"Tags: {', '.join(['#' + tag for tag in tags])}\n"
    formatted_content += f"\n{content}\n"

    # Write the note to a file
    with open(filepath, "w") as file:
        file.write(formatted_content)

    # Update index
    index: List[NoteMetadata] = get_note_index()
    index.append(metadata)
    save_note_index(index)

    # Update tags
    update_tags(note_id, tags)

    return f"Note '{title}' saved with ID: {note_id}"


def read_note(note_id: str = "", title: str = "") -> str:
    """
    Read a note by its ID or title.

    Args:
        note_id: The ID of the note to read. Default is empty string.
        title: The title of the note to read. Default is empty string.

    Returns:
        The content of the note or an error message.
    """
    ensure_notes_directory()
    index = get_note_index()

    # Find the note in the index
    note_meta: Optional[NoteMetadata] = None
    if note_id and note_id.strip():
        note_meta = next(
            (note for note in index if note["id"] == note_id), None
        )
    elif title and title.strip():
        note_meta = next(
            (note for note in index if note["title"].lower() == title.lower()),
            None,
        )

    if not note_meta:
        return "Note not found. Please check the ID or title."

    # Read the note content
    filepath = os.path.join(NOTES_DIR, note_meta["filename"])
    if not os.path.exists(filepath):
        return f"Note file not found: {filepath}"

    with open(filepath, "r") as file:
        content = file.read()

    return content


def list_notes(subject: str = "", tag: str = "", limit: int = 10) -> str:
    """
    List notes, optionally filtered by subject or tag.

    Args:
        subject: Filter notes by subject. Default is empty string.
        tag: Filter notes by tag. Default is empty string.
        limit: Maximum number of notes to return.

    Returns:
        A formatted list of notes.
    """
    ensure_notes_directory()
    index = get_note_index()

    # Apply filters
    if subject and subject.strip():
        index = [note for note in index if note.get("subject") == subject]

    if tag and tag.strip():
        tags_index = get_tags()
        tag_notes = tags_index.get(tag, [])
        index = [note for note in index if note["id"] in tag_notes]

    # Sort by creation time (newest first)
    index.sort(key=lambda x: x["created"], reverse=True)

    # Limit the number of results
    index = index[:limit]

    if not index:
        return "No notes found matching the criteria."

    # Format the output
    output = "# Notes List\n\n"
    for i, note in enumerate(index, 1):
        created_timestamp = note["created"]
        if isinstance(created_timestamp, (int, float)):
            date = datetime.datetime.fromtimestamp(created_timestamp).strftime(
                "%Y-%m-%d"
            )
        else:
            date = "Unknown"

        output += f"{i}. **{note['title']}** ({date})\n"
        output += f"   ID: {note['id']}\n"
        if note.get("subject"):
            output += f"   Subject: {note['subject']}\n"
        if note.get("tags"):
            tags_list = note["tags"]
            if isinstance(tags_list, list):
                # Format tags list without using list comprehension to avoid type warnings
                tags_str = ", ".join(
                    [f"#{str(t)}" for t in cast(List[Any], tags_list)]
                )
                output += f"   Tags: {tags_str}\n"
        output += "\n"

    return output


def generate_note_summary(note_id: str = "", title: str = "") -> str:
    """
    Generate a summary of a note by extracting key points.

    Args:
        note_id: The ID of the note to summarize. Default is empty string.
        title: The title of the note to summarize. Default is empty string.

    Returns:
        A summary of the note or an error message.
    """
    # First read the note
    note_content = read_note(note_id, title)
    if note_content.startswith("Note not found") or note_content.startswith(
        "Note file not found"
    ):
        return note_content

    # Extract the title from the content
    title_match = re.search(r"^# (.+)$", note_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Unknown Title"

    # Extract headings as key points
    headings = re.findall(r"^## (.+)$", note_content, re.MULTILINE)

    # Extract the first sentence of each paragraph as key points
    paragraphs = re.split(r"\n\n+", note_content)
    first_sentences: List[str] = []
    for para in paragraphs:
        if para.startswith("#") or not para.strip():
            continue
        # Try to get the first sentence
        sentence_match = re.search(r"^([^.!?]+[.!?])", para.replace("\n", " "))
        if sentence_match:
            first_sentences.append(sentence_match.group(1).strip())

    # Generate the summary
    summary = f"# Summary of: {title}\n\n"

    if headings:
        summary += "## Key Topics\n"
        for heading in headings:
            summary += f"- {heading}\n"
        summary += "\n"

    if first_sentences:
        summary += "## Key Points\n"
        for sentence in first_sentences[:5]:  # Limit to 5 key points
            summary += f"- {sentence}\n"

    return summary


def search_notes(query: str) -> str:
    """
    Search notes for a specific query string.

    Args:
        query: The search query.

    Returns:
        A list of notes matching the search query.
    """
    ensure_notes_directory()
    index = get_note_index()
    results: List[NoteMetadata] = []

    query = query.lower()

    # Check if query is a tag search
    if query.startswith("#"):
        tag = query[1:]
        tags_index = get_tags()
        tag_notes = tags_index.get(tag, [])
        if tag_notes:
            # Get full note details for the tag matches
            matching_notes = [note for note in index if note["id"] in tag_notes]
            results.extend(matching_notes)
    else:
        # Search in titles
        title_matches = [
            note for note in index if query in note["title"].lower()
        ]
        results.extend(title_matches)

        # Search in content
        for note in index:
            if note in results:
                continue

            filepath = os.path.join(NOTES_DIR, note["filename"])
            try:
                with open(filepath, "r") as file:
                    content = file.read().lower()
                    if query in content:
                        results.append(note)
            except (IOError, OSError, UnicodeDecodeError):
                continue

    if not results:
        return f"No notes found matching '{query}'."

    # Format the output
    output = f"# Search Results for: {query}\n\n"
    for i, note in enumerate(results, 1):
        created_timestamp = note["created"]
        if isinstance(created_timestamp, (int, float)):
            date = datetime.datetime.fromtimestamp(created_timestamp).strftime(
                "%Y-%m-%d"
            )
        else:
            date = "Unknown"

        output += f"{i}. **{note['title']}** ({date})\n"
        output += f"   ID: {note['id']}\n"
        if note.get("subject"):
            output += f"   Subject: {note['subject']}\n"
        if note.get("tags"):
            tags_list = note["tags"]
            if isinstance(tags_list, list):
                # Format tags list without using list comprehension to avoid type warnings
                tags_str = ", ".join(
                    [f"#{str(t)}" for t in cast(List[Any], tags_list)]
                )
                output += f"   Tags: {tags_str}\n"
        output += "\n"

    return output


def edit_note(note_id: str, new_content: str) -> str:
    """
    Edit an existing note.

    Args:
        note_id: The ID of the note to edit.
        new_content: The new content for the note.

    Returns:
        A success message or an error message.
    """
    ensure_notes_directory()
    index = get_note_index()

    # Find the note in the index
    note_meta: Optional[NoteMetadata] = next(
        (note for note in index if note["id"] == note_id), None
    )
    if not note_meta:
        return f"Note not found with ID: {note_id}"

    # Extract tags from new content
    tags = extract_tags(new_content)

    # Update metadata
    note_meta["modified"] = int(time.time())
    note_meta["tags"] = tags

    # Update the note file
    filepath = os.path.join(NOTES_DIR, note_meta["filename"])
    if not os.path.exists(filepath):
        return f"Note file not found: {filepath}"

    # Add formatted header to content
    created_timestamp = note_meta["created"]
    if isinstance(created_timestamp, (int, float)):
        date_str = datetime.datetime.fromtimestamp(created_timestamp).strftime(
            "%Y-%m-%d"
        )
    else:
        date_str = "Unknown"

    formatted_content = f"# {note_meta['title']}\n\nDate: {date_str}\n"
    if note_meta.get("subject"):
        formatted_content += f"Subject: {note_meta['subject']}\n"
    if tags:
        formatted_content += f"Tags: {', '.join(['#' + tag for tag in tags])}\n"
    formatted_content += f"\n{new_content}\n"

    # Write the updated content
    with open(filepath, "w") as file:
        file.write(formatted_content)

    # Update the index
    for i, note in enumerate(index):
        if note["id"] == note_id:
            index[i] = note_meta
            break
    save_note_index(index)

    # Update tags
    update_tags(note_id, tags)

    return f"Note '{note_meta['title']}' updated successfully."


def delete_note(note_id: str) -> str:
    """
    Delete a note by its ID.

    Args:
        note_id: The ID of the note to delete.

    Returns:
        A success message or an error message.
    """
    ensure_notes_directory()
    index = get_note_index()

    # Find the note in the index
    note_meta: Optional[NoteMetadata] = next(
        (note for note in index if note["id"] == note_id), None
    )
    if not note_meta:
        return f"Note not found with ID: {note_id}"

    # Remove the file
    filepath = os.path.join(NOTES_DIR, note_meta["filename"])
    if os.path.exists(filepath):
        os.remove(filepath)

    # Update the index
    index = [note for note in index if note["id"] != note_id]
    save_note_index(index)

    # Update tags
    tags_index = get_tags()
    for _tag, notes in tags_index.items():
        if note_id in notes:
            notes.remove(note_id)
    save_tags(tags_index)

    return f"Note '{note_meta['title']}' deleted successfully."


def organize_notes_by_subject() -> str:
    """
    Create a summary of notes organized by subject.

    Returns:
        A summary of notes organized by subject.
    """
    ensure_notes_directory()
    index = get_note_index()

    # Group notes by subject
    subjects: Dict[str, List[NoteMetadata]] = {}
    for note in index:
        subject = note.get("subject") or "Uncategorized"
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append(note)

    # Sort notes within each subject by creation time (newest first)
    for subject_name in subjects:
        subjects[subject_name].sort(
            key=lambda x: x["created"]
            if isinstance(x["created"], (int, float))
            else 0,
            reverse=True,
        )

    # Format the output
    output = "# Notes Organized by Subject\n\n"
    for subject_name, notes in sorted(subjects.items()):
        output += f"## {subject_name}\n\n"
        for note in notes:
            created_timestamp = note["created"]
            if isinstance(created_timestamp, (int, float)):
                date = datetime.datetime.fromtimestamp(
                    created_timestamp
                ).strftime("%Y-%m-%d")
            else:
                date = "Unknown"
            output += f"- **{note['title']}** ({date}) - ID: {note['id']}\n"
        output += "\n"

    return output


def register_tools_note(mcp: Any) -> None:
    """Register all note tools with the MCP server."""
    mcp.tool()(add_note)
    mcp.tool()(read_note)
    mcp.tool()(list_notes)
    mcp.tool()(generate_note_summary)
    mcp.tool()(search_notes)
    mcp.tool()(edit_note)
    mcp.tool()(delete_note)
    mcp.tool()(organize_notes_by_subject)
