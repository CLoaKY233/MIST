# server.py
import os
import time
import datetime
import json
from pathlib import Path
import re
from typing import List, Dict, Optional
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("M.I.S.T.")

# Notes App Configuration
NOTES_DIR = os.path.join(os.path.dirname(__file__), "notes")
INDEX_FILE = os.path.join(NOTES_DIR, "index.json")
TAGS_FILE = os.path.join(NOTES_DIR, "tags.json")

# Ensure the notes directory and index file exist
def ensure_notes_directory():
    """Create notes directory and required files if they don't exist."""
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)
    
    # Create index file if it doesn't exist
    if not os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'w') as file:
            json.dump([], file)
    
    # Create tags file if it doesn't exist
    if not os.path.exists(TAGS_FILE):
        with open(TAGS_FILE, 'w') as file:
            json.dump({}, file)

# Helper functions
def get_note_index() -> List[Dict]:
    """Load the note index."""
    with open(INDEX_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_note_index(index: List[Dict]):
    """Save the note index."""
    with open(INDEX_FILE, 'w') as file:
        json.dump(index, file, indent=2)

def get_tags() -> Dict:
    """Load the tags index."""
    with open(TAGS_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_tags(tags: Dict):
    """Save the tags index."""
    with open(TAGS_FILE, 'w') as file:
        json.dump(tags, file, indent=2)

def extract_tags(content: str) -> List[str]:
    """Extract hashtags from content."""
    return re.findall(r'#(\w+)', content)

def update_tags(note_id: str, tags: List[str]):
    """Update tags index with the given tags."""
    tags_index = get_tags()
    
    # Remove note_id from all existing tags
    for tag in tags_index.values():
        if note_id in tag:
            tag.remove(note_id)
    
    # Add note_id to the appropriate tags
    for tag in tags:
        if tag not in tags_index:
            tags_index[tag] = []
        if note_id not in tags_index[tag]:
            tags_index[tag].append(note_id)
    
    # Clean up empty tag entries
    tags_index = {k: v for k, v in tags_index.items() if v}
    
    save_tags(tags_index)

# MCP Tools
@mcp.tool()
def add_note(title: str, content: str, subject: Optional[str] = None) -> str:
    """
    Create a new note with a title and content.
    
    Args:
        title (str): The title of the note.
        content (str): The content of the note.
        subject (str, optional): The subject/category of the note.
    
    Returns:
        str: A success message with the created note ID.
    """
    ensure_notes_directory()
    
    # Generate a unique filename based on timestamp and title
    timestamp = int(time.time())
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    # Sanitize title for filename
    safe_title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
    note_id = f"{date_str}-{safe_title}-{timestamp}"
    filename = f"{note_id}.md"
    filepath = os.path.join(NOTES_DIR, filename)
    
    # Extract tags from content
    tags = extract_tags(content)
    
    # Create note metadata
    metadata = {
        "id": note_id,
        "title": title,
        "created": timestamp,
        "modified": timestamp,
        "subject": subject,
        "tags": tags,
        "filename": filename
    }
    
    # Add formatted header to content
    formatted_content = f"# {title}\n\nDate: {date_str}\n"
    if subject:
        formatted_content += f"Subject: {subject}\n"
    if tags:
        formatted_content += f"Tags: {', '.join(['#'+tag for tag in tags])}\n"
    formatted_content += f"\n{content}\n"
    
    # Write the note to a file
    with open(filepath, 'w') as file:
        file.write(formatted_content)
    
    # Update index
    index = get_note_index()
    index.append(metadata)
    save_note_index(index)
    
    # Update tags
    update_tags(note_id, tags)
    
    return f"Note '{title}' saved with ID: {note_id}"

@mcp.tool()
def read_note(note_id: Optional[str] = None, title: Optional[str] = None) -> str:
    """
    Read a note by its ID or title.
    
    Args:
        note_id (str, optional): The ID of the note to read.
        title (str, optional): The title of the note to read.
    
    Returns:
        str: The content of the note or an error message.
    """
    ensure_notes_directory()
    index = get_note_index()
    
    # Find the note in the index
    note_meta = None
    if note_id:
        note_meta = next((note for note in index if note["id"] == note_id), None)
    elif title:
        note_meta = next((note for note in index if note["title"].lower() == title.lower()), None)
    
    if not note_meta:
        return f"Note not found. Please check the ID or title."
    
    # Read the note content
    filepath = os.path.join(NOTES_DIR, note_meta["filename"])
    if not os.path.exists(filepath):
        return f"Note file not found: {filepath}"
    
    with open(filepath, 'r') as file:
        content = file.read()
    
    return content

@mcp.tool()
def list_notes(subject: Optional[str] = None, tag: Optional[str] = None, limit: int = 10) -> str:
    """
    List notes, optionally filtered by subject or tag.
    
    Args:
        subject (str, optional): Filter notes by subject.
        tag (str, optional): Filter notes by tag.
        limit (int): Maximum number of notes to return.
    
    Returns:
        str: A formatted list of notes.
    """
    ensure_notes_directory()
    index = get_note_index()
    
    # Apply filters
    if subject:
        index = [note for note in index if note.get("subject") == subject]
    
    if tag:
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
        date = datetime.datetime.fromtimestamp(note["created"]).strftime("%Y-%m-%d")
        output += f"{i}. **{note['title']}** ({date})\n"
        output += f"   ID: {note['id']}\n"
        if note.get("subject"):
            output += f"   Subject: {note['subject']}\n"
        if note.get("tags"):
            output += f"   Tags: {', '.join(['#'+tag for tag in note['tags']])}\n"
        output += "\n"
    
    return output

@mcp.tool()
def generate_summary(note_id: Optional[str] = None, title: Optional[str] = None) -> str:
    """
    Generate a summary of a note by extracting key points.
    
    Args:
        note_id (str, optional): The ID of the note to summarize.
        title (str, optional): The title of the note to summarize.
    
    Returns:
        str: A summary of the note or an error message.
    """
    # First read the note
    note_content = read_note(note_id, title)
    if note_content.startswith("Note not found") or note_content.startswith("Note file not found"):
        return note_content
    
    # Extract the title from the content
    title_match = re.search(r'^# (.+)$', note_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "Unknown Title"
    
    # Extract headings as key points
    headings = re.findall(r'^## (.+)$', note_content, re.MULTILINE)
    
    # Extract the first sentence of each paragraph as key points
    paragraphs = re.split(r'\n\n+', note_content)
    first_sentences = []
    for para in paragraphs:
        if para.startswith('#') or not para.strip():
            continue
        # Try to get the first sentence
        sentence_match = re.search(r'^([^.!?]+[.!?])', para.replace('\n', ' '))
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

@mcp.tool()
def search_notes(query: str) -> str:
    """
    Search notes for a specific query string.
    
    Args:
        query (str): The search query.
    
    Returns:
        str: A list of notes matching the search query.
    """
    ensure_notes_directory()
    index = get_note_index()
    results = []
    
    query = query.lower()
    
    # Check if query is a tag search
    if query.startswith('#'):
        tag = query[1:]
        tags_index = get_tags()
        tag_notes = tags_index.get(tag, [])
        if tag_notes:
            # Get full note details for the tag matches
            matching_notes = [note for note in index if note["id"] in tag_notes]
            results.extend(matching_notes)
    else:
        # Search in titles
        title_matches = [note for note in index if query in note["title"].lower()]
        results.extend(title_matches)
        
        # Search in content
        for note in index:
            if note in results:
                continue
                
            filepath = os.path.join(NOTES_DIR, note["filename"])
            try:
                with open(filepath, 'r') as file:
                    content = file.read().lower()
                    if query in content:
                        results.append(note)
            except:
                continue
    
    if not results:
        return f"No notes found matching '{query}'."
    
    # Format the output
    output = f"# Search Results for: {query}\n\n"
    for i, note in enumerate(results, 1):
        date = datetime.datetime.fromtimestamp(note["created"]).strftime("%Y-%m-%d")
        output += f"{i}. **{note['title']}** ({date})\n"
        output += f"   ID: {note['id']}\n"
        if note.get("subject"):
            output += f"   Subject: {note['subject']}\n"
        if note.get("tags"):
            output += f"   Tags: {', '.join(['#'+tag for tag in note['tags']])}\n"
        output += "\n"
    
    return output

@mcp.tool()
def edit_note(note_id: str, new_content: str) -> str:
    """
    Edit an existing note.
    
    Args:
        note_id (str): The ID of the note to edit.
        new_content (str): The new content for the note.
    
    Returns:
        str: A success message or an error message.
    """
    ensure_notes_directory()
    index = get_note_index()
    
    # Find the note in the index
    note_meta = next((note for note in index if note["id"] == note_id), None)
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
    date_str = datetime.datetime.fromtimestamp(note_meta["created"]).strftime("%Y-%m-%d")
    formatted_content = f"# {note_meta['title']}\n\nDate: {date_str}\n"
    if note_meta.get("subject"):
        formatted_content += f"Subject: {note_meta['subject']}\n"
    if tags:
        formatted_content += f"Tags: {', '.join(['#'+tag for tag in tags])}\n"
    formatted_content += f"\n{new_content}\n"
    
    # Write the updated content
    with open(filepath, 'w') as file:
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

@mcp.tool()
def delete_note(note_id: str) -> str:
    """
    Delete a note by its ID.
    
    Args:
        note_id (str): The ID of the note to delete.
    
    Returns:
        str: A success message or an error message.
    """
    ensure_notes_directory()
    index = get_note_index()
    
    # Find the note in the index
    note_meta = next((note for note in index if note["id"] == note_id), None)
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
    for tag, notes in tags_index.items():
        if note_id in notes:
            notes.remove(note_id)
    save_tags(tags_index)
    
    return f"Note '{note_meta['title']}' deleted successfully."

@mcp.tool()
def organize_notes_by_subject() -> str:
    """
    Create a summary of notes organized by subject.
    
    Returns:
        str: A summary of notes organized by subject.
    """
    ensure_notes_directory()
    index = get_note_index()
    
    # Group notes by subject
    subjects = {}
    for note in index:
        subject = note.get("subject") or "Uncategorized"
        if subject not in subjects:
            subjects[subject] = []
        subjects[subject].append(note)
    
    # Sort notes within each subject by creation time (newest first)
    for subject in subjects:
        subjects[subject].sort(key=lambda x: x["created"], reverse=True)
    
    # Format the output
    output = "# Notes Organized by Subject\n\n"
    for subject, notes in sorted(subjects.items()):
        output += f"## {subject}\n\n"
        for note in notes:
            date = datetime.datetime.fromtimestamp(note["created"]).strftime("%Y-%m-%d")
            output += f"- **{note['title']}** ({date}) - ID: {note['id']}\n"
        output += "\n"
    
    return output
