"""
This module provides utilities for interacting with the Notion API.
"""

from typing import Any, Dict, List, Optional, Union
import httpx
import logging
import sys
import rich
from rich.logging import RichHandler

from tools.notion_tools.config import settings
from tools.notion_tools.models.notion import Database, Page, SearchResults, PropertyValue, Block

# Set up logging to stderr to avoid breaking MCP
logger = logging.getLogger("notion_api")
logger.setLevel(logging.INFO)

# Make sure handler outputs to stderr
if not logger.handlers:
    handler = RichHandler(rich_tracebacks=True, console=rich.console.Console(file=sys.stderr))
    logger.addHandler(handler)

def get_notion_headers() -> Dict[str, str]:
    """
    Get Notion API headers with authentication.

    Returns:
        Dict with Notion API headers
    """
    if not settings["api_key"]:
        raise ValueError("NOTION_API_KEY not found in environment variables")

    return {
        "Authorization": f"Bearer {settings['api_key']}",
        "Content-Type": "application/json",
        "Notion-Version": settings["api_version"]
    }

async def list_databases() -> List[Database]:
    """
    List all databases the integration has access to.

    Returns:
        List of Database objects
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings['base_url']}/search",
                headers=get_notion_headers(),
                json={
                    "filter": {
                        "property": "object",
                        "value": "database"
                    },
                    "page_size": settings["page_size"],
                    "sort": {
                        "direction": "descending",
                        "timestamp": "last_edited_time"
                    }
                }
            )
            response.raise_for_status()
            data = response.json()
            if not data.get("results"):
                return []
            return [Database.model_validate(db) for db in data["results"]]
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error listing databases: {str(e)}")
        raise

async def get_database(database_id: str) -> Database:
    """
    Get metadata about a database.

    Args:
        database_id: The ID of the database to retrieve

    Returns:
        Database object with metadata
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings['base_url']}/databases/{database_id}",
                headers=get_notion_headers()
            )
            response.raise_for_status()
            return Database.model_validate(response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting database: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error getting database: {str(e)}")
        raise

async def query_database(
    database_id: str,
    filter: Optional[Dict[str, Any]] = None,
    sorts: Optional[List[Dict[str, Any]]] = None,
    start_cursor: Optional[str] = None,
    page_size: int = settings["page_size"]
) -> Dict[str, Any]:
    """
    Query a database with optional filter and sorting.

    Args:
        database_id: The ID of the database to query
        filter: Optional filter criteria
        sorts: Optional sort criteria
        start_cursor: Optional cursor for pagination
        page_size: Number of results to return per page

    Returns:
        Query results containing pages and pagination info
    """
    try:
        body = {
            "page_size": page_size
        }
        if filter:
            body["filter"] = filter #type:ignore
        if sorts:
            body["sorts"] = sorts#type:ignore
        if start_cursor:
            body["start_cursor"] = start_cursor#type:ignore

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings['base_url']}/databases/{database_id}/query",
                headers=get_notion_headers(),
                json=body
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error querying database {database_id}: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error querying database {database_id}: {str(e)}")
        raise

async def create_page(
    parent_id: str,
    properties: Dict[str, Any],
    children: Optional[List[Dict[str, Any]]] = None
) -> Page:
    """
    Create a new page in a database.

    Args:
        parent_id: ID of the database to create the page in
        properties: Page properties matching the database schema
        children: Optional page content blocks

    Returns:
        Created Page object
    """
    try:
        body = {
            "parent": {"database_id": parent_id},
            "properties": properties
        }
        if children:
            body["children"] = children

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings['base_url']}/pages",
                headers=get_notion_headers(),
                json=body
            )
            response.raise_for_status()
            return Page.model_validate(response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error creating page: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error creating page: {str(e)}")
        raise

async def update_page(
    page_id: str,
    properties: Dict[str, Any],
    archived: Optional[bool] = None
) -> Page:
    """
    Update an existing page.

    Args:
        page_id: ID of the page to update
        properties: Updated page properties
        archived: Whether to archive the page

    Returns:
        Updated Page object
    """
    try:
        body = {"properties": properties}
        if archived is not None:
            body["archived"] = archived#type:ignore

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{settings['base_url']}/pages/{page_id}",
                headers=get_notion_headers(),
                json=body
            )
            response.raise_for_status()
            return Page.model_validate(response.json())
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error updating page {page_id}: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error updating page {page_id}: {str(e)}")
        raise

async def get_block_children(
    block_id: str,
    start_cursor: Optional[str] = None,
    page_size: int = settings["page_size"]
) -> Dict[str, Any]:
    """
    Get children blocks of a block.

    Args:
        block_id: ID of the block to get children for
        start_cursor: Cursor for pagination
        page_size: Number of results per page

    Returns:
        Block children data
    """
    try:
        params = {"page_size": page_size}
        if start_cursor:
            params["start_cursor"] = start_cursor#type:ignore

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings['base_url']}/blocks/{block_id}/children",
                headers=get_notion_headers(),
                params=params
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting block children: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error getting block children: {str(e)}")
        raise

async def search(
    query: str = "",
    filter: Optional[Dict[str, Any]] = None,
    sort: Optional[Dict[str, Any]] = None,
    start_cursor: Optional[str] = None,
    page_size: int = settings["page_size"]
) -> SearchResults:
    """
    Search Notion content.

    Args:
        query: Search query string
        filter: Filter criteria for search results
        sort: Sort criteria for search results
        start_cursor: Cursor for pagination
        page_size: Number of results per page

    Returns:
        SearchResults object with results and pagination info
    """
    try:
        body = {
            "query": query,
            "page_size": page_size
        }
        if filter:
            body["filter"] = filter
        if sort:
            body["sort"] = sort
        if start_cursor:
            body["start_cursor"] = start_cursor

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings['base_url']}/search",
                headers=get_notion_headers(),
                json=body
            )
            response.raise_for_status()
            data = response.json()

            # Convert results based on their object type
            results = []
            for item in data.get("results", []):
                try:
                    if item["object"] == "database":
                        results.append(Database.model_validate(item))
                    elif item["object"] == "page":
                        results.append(Page.model_validate(item))
                except Exception as e:
                    logger.warning(f"Error processing search result: {str(e)}")
                    continue

            return SearchResults(
                object="list",
                results=results,
                next_cursor=data.get("next_cursor"),
                has_more=data.get("has_more", False)
            )
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during search: {e.response.status_code} - {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        raise
