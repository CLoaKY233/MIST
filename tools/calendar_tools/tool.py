"""
Calendar MCP Server Implementation

This module provides a Model Context Protocol server for interacting with Google Calendar.
It exposes Calendar events as resources and provides tools for managing calendars and events.
"""

from typing import List, Optional

from tools.calendar_tools.calendar import (
    get_calendar_service,
    list_calendars,
    get_events,
    create_event,
    update_event,
    delete_event,
)

service = get_calendar_service()

# Resource functions
def get_calendar_events(calendar_id: str) -> str:
    """
    Get events from a specific calendar by its ID.

    Args:
        calendar_id: ID of the calendar

    Returns:
        Formatted string with calendar events
    """
    events = get_events(service, calendar_id)
    result = f"Calendar (ID: {calendar_id})\n"
    
    if not events:
        return result + "\nNo events found in this calendar."
        
    for event in events:
        result += f"\nTitle: {event.get('summary', 'Untitled')}\n"
        
        start = event.get('start', {})
        end = event.get('end', {})
        
        if 'dateTime' in start:
            result += f"Start: {start.get('dateTime')}\n"
        elif 'date' in start:
            result += f"Start Date: {start.get('date')}\n"
            
        if 'dateTime' in end:
            result += f"End: {end.get('dateTime')}\n"
        elif 'date' in end:
            result += f"End Date: {end.get('date')}\n"
            
        if event.get('location'):
            result += f"Location: {event.get('location')}\n"
            
        result += f"Event ID: {event.get('id')}\n"
            
    return result


def get_calendar_event(calendar_id: str, event_id: str) -> str:
    """
    Get details of a specific calendar event.

    Args:
        calendar_id: ID of the calendar
        event_id: ID of the event

    Returns:
        Formatted string with event details
    """
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    
    result = f"Event (ID: {event_id})\n"
    result += f"Title: {event.get('summary', 'Untitled')}\n"
    
    # Format start time
    start = event.get('start', {})
    if 'dateTime' in start:
        result += f"Start: {start.get('dateTime')}\n"
    elif 'date' in start:
        result += f"Start Date: {start.get('date')} (All day)\n"
    
    # Format end time
    end = event.get('end', {})
    if 'dateTime' in end:
        result += f"End: {end.get('dateTime')}\n"
    elif 'date' in end:
        result += f"End Date: {end.get('date')} (All day)\n"
    
    # Add location if available
    if event.get('location'):
        result += f"Location: {event.get('location')}\n"
    
    # Add description if available
    if event.get('description'):
        result += f"Description: {event.get('description')}\n"
    
    # Add attendees if available
    attendees = event.get('attendees', [])
    if attendees:
        result += "\nAttendees:\n"
        for attendee in attendees:
            email = attendee.get('email', 'No email')
            response_status = attendee.get('responseStatus', 'Unknown')
            result += f"- {email} ({response_status})\n"
    
    return result


# Tool functions
def list_calendars_tool() -> str:
    """
    List all calendars available to the user.

    Returns:
        Formatted string with all calendars
    """
    calendars = list_calendars(service)
    
    if not calendars:
        return "No calendars found."
        
    result = f"Found {len(calendars)} calendars:\n"
    
    for calendar in calendars:
        result += f"\nTitle: {calendar.get('summary', 'Untitled')}\n"
        result += f"ID: {calendar.get('id', 'Unknown')}\n"
        result += f"Access Role: {calendar.get('accessRole', 'Unknown')}\n"
        
        # Add primary calendar indicator
        if calendar.get('primary', False):
            result += "Primary Calendar: Yes\n"
            
    return result


def create_event_tool(
    calendar_id: str,
    title: str,
    start_datetime: str,
    end_datetime: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[List[str]] = None,
    timezone: Optional[str] = None,
) -> str:
    """
    Create a new event in a specified calendar.

    Args:
        calendar_id: ID of the calendar
        title: Title of the event
        start_datetime: Start time in RFC3339 format (e.g., "2023-06-03T10:00:00-07:00")
        end_datetime: End time in RFC3339 format
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of attendee email addresses (optional)
        timezone: Timezone for the event (optional)

    Returns:
        Confirmation message with event details
    """
    event = create_event(
        service, calendar_id, title, start_datetime, end_datetime, description, 
        location, attendees, timezone
    )
    
    result = "Event created successfully:\n"
    result += f"ID: {event.get('id', 'Unknown')}\n"
    result += f"Title: {title}\n"
    result += f"Start: {start_datetime}\n"
    result += f"End: {end_datetime}\n"
    
    if description:
        result += f"Description: {description}\n"
    if location:
        result += f"Location: {location}\n"
    if attendees:
        result += f"Attendees: {', '.join(attendees)}\n"
    if timezone:
        result += f"Timezone: {timezone}\n"
    
    # Add link to the event
    if event.get('htmlLink'):
        result += f"\nEvent Link: {event.get('htmlLink')}\n"
        
    return result


def update_event_tool(
    calendar_id: str,
    event_id: str,
    title: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """
    Update an existing calendar event.

    Args:
        calendar_id: ID of the calendar containing the event
        event_id: ID of the event to update
        title: New title of the event (optional)
        start_datetime: New start time in RFC3339 format (optional)
        end_datetime: New end time in RFC3339 format (optional)
        description: New event description (optional)
        location: New event location (optional)

    Returns:
        Confirmation message with updated event details
    """
    event = update_event(
        service, calendar_id, event_id, title, start_datetime, end_datetime, 
        description, location
    )
    
    result = "Event updated successfully:\n"
    result += f"ID: {event_id}\n"
    
    if title:
        result += f"New Title: {title}\n"
    if start_datetime:
        result += f"New Start Time: {start_datetime}\n"
    if end_datetime:
        result += f"New End Time: {end_datetime}\n"
    if description:
        result += f"New Description: {description}\n"
    if location:
        result += f"New Location: {location}\n"
        
    # Add link to the event
    if event.get('htmlLink'):
        result += f"\nEvent Link: {event.get('htmlLink')}\n"
        
    return result


def delete_event_tool(calendar_id: str, event_id: str) -> str:
    """
    Delete a calendar event.

    Args:
        calendar_id: ID of the calendar containing the event
        event_id: ID of the event to delete

    Returns:
        Confirmation message
    """
    delete_event(service, calendar_id, event_id)
    return f"Event (ID: {event_id}) has been deleted successfully from calendar {calendar_id}."


def search_events_tool(
    calendar_id: str,
    query: str,
    max_results: int = 10,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
) -> str:
    """
    Search for events in a calendar.

    Args:
        calendar_id: ID of the calendar to search in
        query: Search terms to find events
        max_results: Maximum number of events to return
        time_min: Start time in RFC3339 format (optional)
        time_max: End time in RFC3339 format (optional)

    Returns:
        Formatted list of matching events
    """
    events = get_events(
        service, calendar_id, max_results, time_min, time_max, query
    )
    
    result = f"Search results for '{query}' in calendar {calendar_id}:\n"
    
    if not events:
        return result + "\nNo matching events found."
        
    for event in events:
        result += f"\nTitle: {event.get('summary', 'Untitled')}\n"
        
        start = event.get('start', {})
        end = event.get('end', {})
        
        if 'dateTime' in start:
            result += f"Start: {start.get('dateTime')}\n"
        elif 'date' in start:
            result += f"Start Date: {start.get('date')}\n"
            
        if 'dateTime' in end:
            result += f"End: {end.get('dateTime')}\n"
        elif 'date' in end:
            result += f"End Date: {end.get('date')}\n"
            
        if event.get('location'):
            result += f"Location: {event.get('location')}\n"
            
        result += f"Event ID: {event.get('id')}\n"
            
    return result


# Register all tools with MCP
def register_tools_calendar(mcp):
    """Register all calendar tools with the MCP server."""
    # Register tools
    mcp.tool()(list_calendars_tool)
    mcp.tool()(create_event_tool)
    mcp.tool()(update_event_tool)
    mcp.tool()(delete_event_tool)
    mcp.tool()(search_events_tool)
    
    # Register resources
    mcp.resource("calendar://calendars/{calendar_id}/events")(get_calendar_events)
    mcp.resource("calendar://calendars/{calendar_id}/events/{event_id}")(get_calendar_event)