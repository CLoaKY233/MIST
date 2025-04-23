"""
Notion MCP Tools Implementation

This module provides tools for interacting with the Notion API.
It exposes functions for common operations like listing databases,
querying database items, and managing pages.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any

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
        JSON formatted string of accessible databases
    """
    databases = await list_databases()
    return json.dumps({
        "databases": [db.model_dump() for db in databases]
    }, indent=2)


async def get_database_tool(database_id: str) -> str:
    """
    Get details about a specific Notion database.

    Args:
        database_id: ID of the database to retrieve

    Returns:
        JSON formatted database details
    """
    database = await get_database(database_id)
    return database.model_dump_json(indent=2)


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
        JSON formatted query results
    """
    results = await query_database(
        database_id=database_id,
        filter=filter,
        sorts=sorts,
        start_cursor=start_cursor,
        page_size=page_size
    )
    return json.dumps(results, indent=2)


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
        JSON formatted created page data
    """
    page = await create_page(
        parent_id=database_id,
        properties=properties,
        children=children
    )
    return page.model_dump_json(indent=2)


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
        JSON formatted updated page data
    """
    page = await update_page(
        page_id=page_id,
        properties=properties,
        archived=archived
    )
    return page.model_dump_json(indent=2)


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
        JSON formatted block children data
    """
    results = await get_block_children(
        block_id=block_id,
        start_cursor=start_cursor,
        page_size=page_size
    )
    return json.dumps(results, indent=2)


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
        JSON formatted search results
    """
    results = await search(
        query=query,
        filter=filter,
        sort=sort,
        start_cursor=start_cursor,
        page_size=page_size
    )
    return results.model_dump_json(indent=2)


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

    # Resource registration could be added in the future
    # when MCP supports it better
