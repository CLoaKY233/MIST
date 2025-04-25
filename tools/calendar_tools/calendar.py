"""
This module provides utilities for authenticating with and using the Google Calendar API.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from tools.google_api import get_google_service, settings


def get_calendar_service() -> Any:
    """
    Authenticate with Calendar API and return the service object.
    """
    return get_google_service(
        "calendar",
        "v3",
        credentials_path=settings.credentials_path,
        token_path=settings.token_path,
        scopes=settings.scopes,
    )


def list_calendars(service: Any) -> List[Dict[str, Any]]:
    """
    List all calendars the user has access to.
    
    Args:
        service: Calendar API service instance
        
    Returns:
        List of calendar objects
    """
    calendar_list = service.calendarList().list().execute()
    return calendar_list.get("items", [])


def get_events(
    service: Any, 
    calendar_id: str, 
    max_results: int = 10,
    time_min: Optional[str] = None,
    time_max: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get events from a specific calendar.
    
    Args:
        service: Calendar API service instance
        calendar_id: ID of the calendar to get events from
        max_results: Maximum number of events to return (default: 10)
        time_min: Start time for events in RFC3339 format (default: now)
        time_max: End time for events in RFC3339 format
        search_query: Free text search terms to find events that match
        
    Returns:
        List of event objects
    """
    # If no time_min provided, use current time
    if time_min is None:
        time_min = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    
    # Build the request parameters
    request_params = {
        "calendarId": calendar_id,
        "maxResults": max_results,
        "singleEvents": True,
        "orderBy": "startTime",
        "timeMin": time_min
    }
    
    # Add optional parameters if provided
    if time_max:
        request_params["timeMax"] = time_max
    if search_query:
        request_params["q"] = search_query
    
    events_result = service.events().list(**request_params).execute()
    return events_result.get("items", [])


def create_event(
    service: Any,
    calendar_id: str,
    summary: str,
    start_datetime: str,
    end_datetime: str,
    description: Optional[str] = None,
    location: Optional[str] = None,
    attendees: Optional[Union[List[str], List[Dict[str, str]]]] = None,
    timezone: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new calendar event.
    
    Args:
        service: Calendar API service instance
        calendar_id: ID of the calendar to create the event in
        summary: Title of the event
        start_datetime: Start time in RFC3339 format
        end_datetime: End time in RFC3339 format
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of attendee email addresses or already formatted attendee dicts (optional)
        timezone: Timezone for the event (optional)
        
    Returns:
        Created event object
    """
    # Create the event body
    event = {
        "summary": summary,
        "start": {"dateTime": start_datetime},
        "end": {"dateTime": end_datetime},
    }
    
    # Add timezone if provided, default to UTC if not
    timezone = timezone or "UTC"
    event["start"]["timeZone"] = timezone
    event["end"]["timeZone"] = timezone
    
    # Add optional fields if provided
    if description:
        event["description"] = description
    if location:
        event["location"] = location
    
    # Add attendees if provided
    if attendees:
        # Check if attendees are already formatted as dictionaries with email keys
        if isinstance(attendees[0], dict) and "email" in attendees[0]:
            event["attendees"] = attendees
        else:
            event["attendees"] = [{"email": email} for email in attendees]
    
    # Create the event with notifications
    return service.events().insert(
        calendarId=calendar_id, 
        body=event,
        sendUpdates='all'  # Ensure notifications are sent to attendees
    ).execute()


def update_event(
    service: Any,
    calendar_id: str,
    event_id: str,
    summary: Optional[str] = None,
    start_datetime: Optional[str] = None,
    end_datetime: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update an existing calendar event.
    
    Args:
        service: Calendar API service instance
        calendar_id: ID of the calendar containing the event
        event_id: ID of the event to update
        summary: New title of the event (optional)
        start_datetime: New start time in RFC3339 format (optional)
        end_datetime: New end time in RFC3339 format (optional)
        description: New event description (optional)
        location: New event location (optional)
        
    Returns:
        Updated event object
    """
    # Get the current event
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    
    # Update fields if provided
    if summary:
        event["summary"] = summary
    if start_datetime:
        event["start"]["dateTime"] = start_datetime
    if end_datetime:
        event["end"]["dateTime"] = end_datetime
    if description:
        event["description"] = description
    if location:
        event["location"] = location
    
    # Update the event
    return service.events().update(
        calendarId=calendar_id, eventId=event_id, body=event
    ).execute()


def delete_event(service: Any, calendar_id: str, event_id: str) -> None:
    """
    Delete a calendar event.
    
    Args:
        service: Calendar API service instance
        calendar_id: ID of the calendar containing the event
        event_id: ID of the event to delete
    """
    service.events().delete(calendarId=calendar_id, eventId=event_id).execute()