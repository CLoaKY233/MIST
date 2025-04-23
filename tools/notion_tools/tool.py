"""
Notion MCP Tools Implementation

This module provides tools for interacting with the Notion API.
It exposes functions for common operations like listing databases,
querying database items, and managing pages.
"""

import json
import asyncio
import nest_asyncio
from typing import Dict, List, Optional, Any

# Patch asyncio to allow nested event loops (needed for MCP environment)
nest_asyncio.apply()

from tools.notion_tools.notion import (
    list_databases,
    get_database,
    query_database,
    create_page,
    update_page,
    get_block_children,
    search
)



# Tool functions for notion

async def list_databases_tool() -> str:
    """
    List all accessible Notion databases.

    Returns:
        Formatted string listing accessible databases
    """
    databases = await list_databases()

    result = "Available Notion Databases:\n"
    if not databases:
        result += "\nNo databases found."
        return result

    for db in databases:
        result += f"\n--- Database ---\n"
        result += f"ID: {db.id}\n"

        # Extract title if available
        title = "Untitled"
        if hasattr(db, "title") and db.title:
            # Handle different title structures
            if isinstance(db.title, list) and db.title:
                title_parts = []
                for part in db.title:
                    if isinstance(part, dict) and "text" in part and "content" in part["text"]:
                        title_parts.append(part["text"]["content"])
                if title_parts:
                    title = " ".join(title_parts)
            elif isinstance(db.title, str):
                title = db.title

        result += f"Title: {title}\n"

        if hasattr(db, "last_edited_time"):
            result += f"Last Edited: {db.last_edited_time}\n"

        if hasattr(db, "url"):
            result += f"URL: {db.url}\n"

    return result


async def get_database_tool(database_id: str) -> str:
    """
    Get details about a specific Notion database.

    Args:
        database_id: ID of the database to retrieve

    Returns:
        Formatted string with database details
    """
    database = await get_database(database_id)

    result = f"Database Details (ID: {database_id}):\n"

    # Extract title
    title = "Untitled"
    if hasattr(database, "title") and database.title:
        if isinstance(database.title, list) and database.title:
            title_parts = []
            for part in database.title:
                if isinstance(part, dict) and "text" in part and "content" in part["text"]:
                    title_parts.append(part["text"]["content"])
            if title_parts:
                title = " ".join(title_parts)
        elif isinstance(database.title, str):
            title = database.title

    result += f"\nTitle: {title}"

    # Add URL if available
    if hasattr(database, "url"):
        result += f"\nURL: {database.url}"

    # Add created/edited times
    if hasattr(database, "created_time"):
        result += f"\nCreated: {database.created_time}"
    if hasattr(database, "last_edited_time"):
        result += f"\nLast Edited: {database.last_edited_time}"

    # Properties/schema information
    if hasattr(database, "properties"):
        result += "\n\nProperties:\n"
        for name, prop in database.properties.items():
            prop_type = prop.get("type", "unknown")
            result += f"- {name} ({prop_type})\n"

    return result


async def query_database_tool(
    database_id: str,
    filter: Optional[Dict[str, Any]] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
    start_cursor: Optional[str] = None,
    page_size: int = 100
) -> str:
    """
    Query items from a Notion database.

    Args:
        database_id: ID of the database to query
        filter: Optional filter criteria
        sorts: Optional sort criteria
        start_cursor: Cursor for pagination
        page_size: Number of results per page

    Returns:
        Formatted string with query results
    """
    results = await query_database(
        database_id=database_id,
        filter=filter,
        sorts=sorts,
        start_cursor=start_cursor,
        page_size=page_size
    )

    result = f"Database Query Results (Database ID: {database_id}):\n"
    result += f"Found {len(results.get('results', []))} items\n"

    # Add pagination info
    if results.get("has_more"):
        result += f"Has more results available. Next cursor: {results.get('next_cursor')}\n"

    # Format each result page
    for i, page in enumerate(results.get("results", []), 1):
        result += f"\n--- Result {i} ---\n"
        result += f"Page ID: {page.get('id')}\n"

        # Format properties
        properties = page.get("properties", {})
        if properties:
            result += "Properties:\n"
            for prop_name, prop_data in properties.items():
                prop_type = prop_data.get("type", "unknown")

                # Format different property types
                if prop_type == "title" and "title" in prop_data:
                    title_content = []
                    for title_part in prop_data["title"]:
                        if "plain_text" in title_part:
                            title_content.append(title_part["plain_text"])
                    result += f"  {prop_name}: {' '.join(title_content)}\n"

                elif prop_type == "rich_text" and "rich_text" in prop_data:
                    text_content = []
                    for text_part in prop_data["rich_text"]:
                        if "plain_text" in text_part:
                            text_content.append(text_part["plain_text"])
                    result += f"  {prop_name}: {' '.join(text_content)}\n"

                elif prop_type == "select" and "select" in prop_data and prop_data["select"]:
                    select_name = prop_data["select"].get("name", "")
                    result += f"  {prop_name}: {select_name}\n"

                elif prop_type == "multi_select" and "multi_select" in prop_data:
                    select_names = [item.get("name", "") for item in prop_data["multi_select"]]
                    result += f"  {prop_name}: {', '.join(select_names)}\n"

                elif prop_type == "date" and "date" in prop_data and prop_data["date"]:
                    start = prop_data["date"].get("start", "")
                    end = prop_data["date"].get("end", "")
                    date_str = start
                    if end:
                        date_str += f" to {end}"
                    result += f"  {prop_name}: {date_str}\n"

                elif prop_type == "checkbox" and "checkbox" in prop_data:
                    result += f"  {prop_name}: {'✓' if prop_data['checkbox'] else '✗'}\n"

                elif prop_type == "number" and "number" in prop_data:
                    result += f"  {prop_name}: {prop_data['number']}\n"

                else:
                    # Just show the type for other property types
                    result += f"  {prop_name}: [{prop_type}]\n"

        # Add URL
        if "url" in page:
            result += f"URL: {page['url']}\n"

    return result


async def create_page_tool(
    database_id: str,
    properties: Dict[str, Any],
    children: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Create a new page in a database.

    Args:
        database_id: ID of the database to create the page in
        properties: Page properties matching the database schema
        children: Optional page content blocks

    Returns:
        Formatted string with created page data
    """
    page = await create_page(
        parent_id=database_id,
        properties=properties,
        children=children
    )

    result = "New Page Created Successfully:\n"
    result += f"Page ID: {page.id}\n"

    # Extract title if possible
    title = "Untitled"
    if hasattr(page, "properties"):
        for prop_name, prop_data in page.properties.items():
            if prop_data.get("type") == "title" and prop_data.get("title"):
                title_parts = []
                for part in prop_data["title"]:
                    if "plain_text" in part:
                        title_parts.append(part["plain_text"])
                if title_parts:
                    title = " ".join(title_parts)
                    break

    result += f"Title: {title}\n"

    # Add URL
    if hasattr(page, "url"):
        result += f"URL: {page.url}\n"

    # Add created/edited times
    if hasattr(page, "created_time"):
        result += f"Created: {page.created_time}\n"

    # Add summary of properties
    if hasattr(page, "properties"):
        result += "\nProperties Added:\n"
        for name in properties.keys():
            if name in page.properties:
                result += f"- {name}\n"

    # Add summary of content blocks
    if children:
        result += f"\nContent blocks added: {len(children)}\n"

    return result


async def update_page_tool(
    page_id: str,
    properties: Dict[str, Any],
    archived: Optional[bool] = None
) -> str:
    """
    Update an existing page.

    Args:
        page_id: ID of the page to update
        properties: Updated page properties
        archived: Whether to archive the page

    Returns:
        Formatted string with updated page data
    """
    page = await update_page(
        page_id=page_id,
        properties=properties,
        archived=archived
    )

    result = "Page Updated Successfully:\n"
    result += f"Page ID: {page.id}\n"

    # Extract title if possible
    title = "Untitled"
    if hasattr(page, "properties"):
        for prop_name, prop_data in page.properties.items():
            if prop_data.get("type") == "title" and prop_data.get("title"):
                title_parts = []
                for part in prop_data["title"]:
                    if "plain_text" in part:
                        title_parts.append(part["plain_text"])
                if title_parts:
                    title = " ".join(title_parts)
                    break

    result += f"Title: {title}\n"

    # Add URL
    if hasattr(page, "url"):
        result += f"URL: {page.url}\n"

    # Add last edited time
    if hasattr(page, "last_edited_time"):
        result += f"Last Edited: {page.last_edited_time}\n"

    # Add archive status
    if archived is not None:
        status = "archived" if archived else "unarchived"
        result += f"Status: {status}\n"

    # Add summary of updated properties
    if properties:
        result += "\nProperties Updated:\n"
        for name in properties.keys():
            result += f"- {name}\n"

    return result


async def get_block_children_tool(
    block_id: str,
    start_cursor: Optional[str] = None,
    page_size: int = 100
) -> str:
    """
    Get the children blocks of a block.

    Args:
        block_id: ID of the block to get children for
        start_cursor: Cursor for pagination
        page_size: Number of results per page

    Returns:
        Formatted string with block children data
    """
    results = await get_block_children(
        block_id=block_id,
        start_cursor=start_cursor,
        page_size=page_size
    )

    result = f"Block Children (Block ID: {block_id}):\n"

    # Add pagination info
    if results.get("has_more"):
        result += f"Has more children. Next cursor: {results.get('next_cursor')}\n"

    blocks = results.get("results", [])
    result += f"Found {len(blocks)} child blocks\n\n"

    # Format each block
    for i, block in enumerate(blocks, 1):
        result += f"--- Block {i} ---\n"
        result += f"ID: {block.get('id')}\n"
        block_type = block.get("type", "unknown")
        result += f"Type: {block_type}\n"

        # Format different block types
        if block_type == "paragraph" and "paragraph" in block:
            text_content = []
            for text in block["paragraph"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            result += f"Content: {' '.join(text_content)}\n"

        elif block_type == "heading_1" and "heading_1" in block:
            text_content = []
            for text in block["heading_1"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            result += f"Heading 1: {' '.join(text_content)}\n"

        elif block_type == "heading_2" and "heading_2" in block:
            text_content = []
            for text in block["heading_2"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            result += f"Heading 2: {' '.join(text_content)}\n"

        elif block_type == "heading_3" and "heading_3" in block:
            text_content = []
            for text in block["heading_3"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            result += f"Heading 3: {' '.join(text_content)}\n"

        elif block_type == "bulleted_list_item" and "bulleted_list_item" in block:
            text_content = []
            for text in block["bulleted_list_item"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            result += f"• {' '.join(text_content)}\n"

        elif block_type == "numbered_list_item" and "numbered_list_item" in block:
            text_content = []
            for text in block["numbered_list_item"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            result += f"- {' '.join(text_content)}\n"

        elif block_type == "to_do" and "to_do" in block:
            text_content = []
            for text in block["to_do"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            checked = "✓" if block["to_do"].get("checked", False) else "☐"
            result += f"{checked} {' '.join(text_content)}\n"

        elif block_type == "toggle" and "toggle" in block:
            text_content = []
            for text in block["toggle"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            result += f"Toggle: {' '.join(text_content)}\n"

        elif block_type == "code" and "code" in block:
            text_content = []
            for text in block["code"].get("rich_text", []):
                if "plain_text" in text:
                    text_content.append(text["plain_text"])
            language = block["code"].get("language", "")
            result += f"Code ({language}):\n```{language}\n{' '.join(text_content)}\n```\n"

        elif block_type == "image" and "image" in block:
            image_type = block["image"].get("type", "")
            if image_type == "external":
                url = block["image"].get("external", {}).get("url", "")
                result += f"Image (external): {url}\n"
            elif image_type == "file":
                url = block["image"].get("file", {}).get("url", "")
                result += f"Image (file): {url}\n"

        else:
            # For other block types, just note the type
            result += f"(Contains {block_type} content)\n"

        result += "\n"

    return result


async def search_notion_tool(
    query: str = "",
    filter: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
    start_cursor: Optional[str] = None,
    page_size: int = 100
) -> str:
    """
    Search Notion content.

    Args:
        query: Search query string
        filter: Filter criteria for search results
        sort: Sort criteria for search results
        start_cursor: Cursor for pagination
        page_size: Number of results per page

    Returns:
        Formatted string with search results
    """
    results = await search(
        query=query,
        filter=filter,
        sort=sort,
        start_cursor=start_cursor,
        page_size=page_size
    )

    # Get the results list
    result_items = results.get("results", [])

    result = f"Notion Search Results (Query: '{query}')\n"
    result += f"Found {len(result_items)} results\n"

    # Add pagination info
    has_more = results.get("has_more", False)
    if has_more:
        next_cursor = results.get("next_cursor", "")
        result += f"Has more results available. Next cursor: {next_cursor}\n"

    # Format each result
    for i, item in enumerate(result_items, 1):
        result += f"\n--- Result {i} ---\n"
        result += f"ID: {item.get('id', 'Unknown')}\n"
        object_type = item.get("object", "Unknown")
        result += f"Type: {object_type}\n"

        # Title extraction depends on the object type
        title = "Untitled"
        if "properties" in item and item["properties"]:
            # For database pages
            for prop_name, prop_data in item["properties"].items():
                if prop_data.get("type") == "title" and prop_data.get("title"):
                    title_parts = []
                    for part in prop_data["title"]:
                        if "plain_text" in part:
                            title_parts.append(part["plain_text"])
                    if title_parts:
                        title = " ".join(title_parts)
                        break
        elif "title" in item and item["title"]:
            # For databases or blocks with direct titles
            if isinstance(item["title"], list):
                title_parts = []
                for part in item["title"]:
                    if isinstance(part, dict) and "text" in part and "content" in part["text"]:
                        title_parts.append(part["text"]["content"])
                    elif isinstance(part, dict) and "plain_text" in part:
                        title_parts.append(part["plain_text"])
                if title_parts:
                    title = " ".join(title_parts)
            elif isinstance(item["title"], str):
                title = item["title"]

        result += f"Title: {title}\n"

        # Add URL
        if "url" in item:
            result += f"URL: {item['url']}\n"

        # Add created/edited times
        if "created_time" in item:
            result += f"Created: {item['created_time']}\n"
        if "last_edited_time" in item:
            result += f"Last Edited: {item['last_edited_time']}\n"

    return result


# Synchronous wrappers for the async functions to work with MCP
def list_databases_sync() -> str:
    """
    Synchronous wrapper for list_databases_tool.
    """
    return asyncio.run(list_databases_tool())


def get_database_sync(database_id: str) -> str:
    """
    Synchronous wrapper for get_database_tool.
    """
    return asyncio.run(get_database_tool(database_id))


def query_database_sync(
    database_id: str,
    filter: Optional[Dict[str, Any]] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
    start_cursor: Optional[str] = None,
    page_size: int = 100
) -> str:
    """
    Synchronous wrapper for query_database_tool.
    """
    return asyncio.run(query_database_tool(database_id, filter, sorts, start_cursor, page_size))


def create_page_sync(
    database_id: str,
    properties: Dict[str, Any],
    children: Optional[List[Dict[str, Any]]] = None
) -> str:
    """
    Synchronous wrapper for create_page_tool.
    """
    return asyncio.run(create_page_tool(database_id, properties, children))


def update_page_sync(
    page_id: str,
    properties: Dict[str, Any],
    archived: Optional[bool] = None
) -> str:
    """
    Synchronous wrapper for update_page_tool.
    """
    return asyncio.run(update_page_tool(page_id, properties, archived))


def get_block_children_sync(
    block_id: str,
    start_cursor: Optional[str] = None,
    page_size: int = 100
) -> str:
    """
    Synchronous wrapper for get_block_children_tool.
    """
    return asyncio.run(get_block_children_tool(block_id, start_cursor, page_size))


def search_notion_sync(
    query: str = "",
    filter: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
    start_cursor: Optional[str] = None,
    page_size: int = 100
) -> str:
    """
    Synchronous wrapper for search_notion_tool.
    """
    return asyncio.run(search_notion_tool(query, filter, sort, start_cursor, page_size))


# Register all notion tools with MCP
def register_tools_notion(mcp):
    """
    Register all notion tools with the MCP server.

    Args:
        mcp: The MCP server instance
    """
    # Register tools
    mcp.tool()(list_databases_sync)
    mcp.tool()(get_database_sync)
    mcp.tool()(query_database_sync)
    mcp.tool()(create_page_sync)
    mcp.tool()(update_page_sync)
    mcp.tool()(get_block_children_sync)
    mcp.tool()(search_notion_sync)
