"""
AI-powered Calendar Agent that combines Google Calendar API with Vertex AI
for intelligent calendar management and natural language interactions.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import asyncio
from dataclasses import dataclass

from calendar_client import CalendarClient
from vertex_ai_client import VertexAIClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentResponse:
    """Response from the calendar agent"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None

class CalendarAIAgent:
    """AI-powered calendar management agent"""

    def __init__(self, project_id: str = None, region: str = None):
        self.calendar_client = CalendarClient()
        self.vertex_client = VertexAIClient(project_id=project_id, region=region)
        self.conversation_history = []

        logger.info("Calendar AI Agent initialized successfully")

    async def process_natural_language_request(self, user_input: str) -> AgentResponse:
        """Process a natural language request and execute appropriate calendar actions"""

        try:
            # Get current calendar context
            upcoming_events = self.calendar_client.get_upcoming_events(max_results=5)
            calendar_context = self._format_context(upcoming_events)

            # Analyze the user's request
            analysis = self.vertex_client.analyze_calendar_request(user_input, calendar_context)

            # Store in conversation history
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "analysis": analysis
            })

            if analysis["action"] == "unknown" or analysis["confidence"] < 0.3:
                return AgentResponse(
                    success=False,
                    message=analysis["natural_language_response"],
                    suggestions=analysis["clarifications_needed"]
                )

            # Execute the appropriate action
            return await self._execute_action(analysis)

        except Exception as error:
            logger.error(f"Error processing request: {error}")
            return AgentResponse(
                success=False,
                message="I encountered an error while processing your request. Please try again.",
                data={"error": str(error)}
            )

    async def _execute_action(self, analysis: Dict[str, Any]) -> AgentResponse:
        """Execute the calendar action based on analysis"""

        action = analysis["action"]
        params = analysis["parameters"]

        try:
            if action == "create":
                return await self._create_event(params, analysis["natural_language_response"])

            elif action == "list":
                return await self._list_events(params, analysis["natural_language_response"])

            elif action == "search":
                return await self._search_events(params, analysis["natural_language_response"])

            elif action == "update":
                return await self._update_event(params, analysis["natural_language_response"])

            elif action == "delete":
                return await self._delete_event(params, analysis["natural_language_response"])

            elif action == "get_free_time":
                return await self._get_free_time(params, analysis["natural_language_response"])

            else:
                return AgentResponse(
                    success=False,
                    message="I'm not sure how to handle that request. Could you please rephrase it?"
                )

        except Exception as error:
            logger.error(f"Error executing action {action}: {error}")
            return AgentResponse(
                success=False,
                message=f"I encountered an error while {action}ing. Please try again.",
                data={"error": str(error)}
            )

    async def _create_event(self, params: Dict[str, Any], ai_response: str) -> AgentResponse:
        """Create a new calendar event"""

        # Parse required parameters
        title = params.get("title", "New Event")

        # Handle datetime parsing
        start_time = await self._parse_datetime_param(params.get("start_time") or params.get("date", ""))
        if not start_time:
            return AgentResponse(
                success=False,
                message="I need a start date and time to create the event. When would you like to schedule it?",
                suggestions=["Please specify the date and time"]
            )

        # Calculate end time
        end_time = await self._parse_datetime_param(params.get("end_time", ""))
        if not end_time:
            duration = params.get("duration", 60)  # Default 1 hour
            if isinstance(duration, str):
                try:
                    duration = int(duration)
                except ValueError:
                    duration = 60
            end_time = start_time + timedelta(minutes=duration)

        # Generate smart description if not provided
        description = params.get("description", "")
        if not description and title:
            description = self.vertex_client.generate_smart_description(title)

        # Create the event
        event_data = self.calendar_client.create_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            location=params.get("location", ""),
            attendees=params.get("attendees", [])
        )

        if event_data:
            return AgentResponse(
                success=True,
                message=f"✅ Event '{title}' created successfully for {start_time.strftime('%B %d at %I:%M %p')}",
                data={"event": event_data}
            )
        else:
            return AgentResponse(
                success=False,
                message="I couldn't create the event. Please try again or check your calendar permissions."
            )

    async def _list_events(self, params: Dict[str, Any], ai_response: str) -> AgentResponse:
        """List upcoming events"""

        max_results = params.get("max_results", 10)
        days_ahead = params.get("days_ahead", 7)

        events = self.calendar_client.get_upcoming_events(
            max_results=max_results,
            days_ahead=days_ahead
        )

        if not events:
            return AgentResponse(
                success=True,
                message="You have no upcoming events in the next week. Your calendar is clear! 📅",
                data={"events": []}
            )

        # Generate AI summary
        summary = self.vertex_client.summarize_calendar_events(events)

        return AgentResponse(
            success=True,
            message=summary,
            data={"events": events, "count": len(events)}
        )

    async def _search_events(self, params: Dict[str, Any], ai_response: str) -> AgentResponse:
        """Search for events"""

        query = params.get("search_query", "")
        if not query:
            return AgentResponse(
                success=False,
                message="What would you like to search for in your calendar?",
                suggestions=["Please specify search terms"]
            )

        events = self.calendar_client.search_events(query, max_results=10)

        if not events:
            return AgentResponse(
                success=True,
                message=f"No events found matching '{query}' 🔍",
                data={"events": [], "query": query}
            )

        return AgentResponse(
            success=True,
            message=f"Found {len(events)} event(s) matching '{query}':",
            data={"events": events, "query": query}
        )

    async def _update_event(self, params: Dict[str, Any], ai_response: str) -> AgentResponse:
        """Update an existing event"""

        event_id = params.get("event_id")
        if not event_id:
            return AgentResponse(
                success=False,
                message="I need to know which event to update. Could you search for it first?",
                suggestions=["Search for the event you want to update"]
            )

        # Prepare update parameters
        update_params = {}
        if "title" in params:
            update_params["title"] = params["title"]
        if "start_time" in params:
            update_params["start_time"] = await self._parse_datetime_param(params["start_time"])
        if "end_time" in params:
            update_params["end_time"] = await self._parse_datetime_param(params["end_time"])
        if "description" in params:
            update_params["description"] = params["description"]
        if "location" in params:
            update_params["location"] = params["location"]

        event_data = self.calendar_client.update_event(event_id, **update_params)

        if event_data:
            return AgentResponse(
                success=True,
                message=f"✅ Event updated successfully",
                data={"event": event_data}
            )
        else:
            return AgentResponse(
                success=False,
                message="I couldn't update the event. Please check if the event exists and try again."
            )

    async def _delete_event(self, params: Dict[str, Any], ai_response: str) -> AgentResponse:
        """Delete an event"""

        event_id = params.get("event_id")
        if not event_id:
            return AgentResponse(
                success=False,
                message="I need to know which event to delete. Could you search for it first?",
                suggestions=["Search for the event you want to delete"]
            )

        success = self.calendar_client.delete_event(event_id)

        if success:
            return AgentResponse(
                success=True,
                message="✅ Event deleted successfully",
                data={"deleted_event_id": event_id}
            )
        else:
            return AgentResponse(
                success=False,
                message="I couldn't delete the event. Please check if the event exists and try again."
            )

    async def _get_free_time(self, params: Dict[str, Any], ai_response: str) -> AgentResponse:
        """Find available time slots"""

        # Default to looking for time in the next 7 days
        start_time = datetime.now()
        end_time = start_time + timedelta(days=7)

        # Get busy periods
        free_busy = self.calendar_client.get_free_busy(start_time, end_time)
        busy_periods = free_busy.get('busy', [])

        # Get AI suggestions for meeting times
        duration = params.get("duration", 60)
        user_request = params.get("request", "find available time")

        suggestions = self.vertex_client.suggest_meeting_times(
            request=user_request,
            busy_periods=busy_periods,
            duration_minutes=duration,
            days_ahead=7
        )

        if suggestions:
            suggestion_text = "Here are some available time slots:\n"
            for i, slot in enumerate(suggestions[:3], 1):
                start = datetime.fromisoformat(slot["start_time"])
                suggestion_text += f"{i}. {start.strftime('%A, %B %d at %I:%M %p')} - {slot['reason']}\n"

            return AgentResponse(
                success=True,
                message=suggestion_text,
                data={"suggestions": suggestions, "busy_periods": busy_periods}
            )
        else:
            return AgentResponse(
                success=True,
                message="I'm having trouble finding good time slots. Your calendar seems quite busy!",
                data={"busy_periods": busy_periods}
            )

    async def _parse_datetime_param(self, datetime_str: str) -> Optional[datetime]:
        """Parse datetime parameter using AI"""
        if not datetime_str:
            return None
        return self.vertex_client.parse_datetime(datetime_str)

    def _format_context(self, events: List[Dict]) -> str:
        """Format events for context"""
        if not events:
            return "No upcoming events"

        context = f"Upcoming events ({len(events)}):\n"
        for event in events[:3]:  # Limit to 3 events for context
            start_time = event.get('start_time', '')
            if 'T' in start_time:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                formatted_time = dt.strftime('%m/%d at %I:%M %p')
            else:
                formatted_time = start_time

            context += f"- {event['title']} ({formatted_time})\n"

        return context

    def get_conversation_history(self) -> List[Dict]:
        """Get the conversation history"""
        return self.conversation_history

    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history = []