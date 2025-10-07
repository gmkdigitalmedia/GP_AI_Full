"""
Google Calendar API client for calendar management operations.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarClient:
    def __init__(self, credentials_path: str = None, token_path: str = 'token.json'):
        self.credentials_path = credentials_path or os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = token_path
        self.service = None
        self.calendar_id = os.getenv('CALENDAR_ID', 'primary')
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Calendar API")

    def get_upcoming_events(self, max_results: int = 10, days_ahead: int = 7) -> List[Dict]:
        """Get upcoming events from the calendar"""
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                timeMin=now,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return self._format_events(events)

        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return []

    def create_event(self, title: str, start_time: datetime, end_time: datetime,
                    description: str = "", location: str = "", attendees: List[str] = None) -> Dict:
        """Create a new calendar event"""
        try:
            event = {
                'summary': title,
                'location': location,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }

            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()

            logger.info(f"Event created: {created_event.get('htmlLink')}")
            return self._format_event(created_event)

        except HttpError as error:
            logger.error(f"An error occurred while creating event: {error}")
            return {}

    def update_event(self, event_id: str, **kwargs) -> Dict:
        """Update an existing event"""
        try:
            event = self.service.events().get(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            for key, value in kwargs.items():
                if key == 'title':
                    event['summary'] = value
                elif key == 'start_time':
                    event['start']['dateTime'] = value.isoformat()
                elif key == 'end_time':
                    event['end']['dateTime'] = value.isoformat()
                elif key == 'description':
                    event['description'] = value
                elif key == 'location':
                    event['location'] = value

            updated_event = self.service.events().update(
                calendarId=self.calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            logger.info(f"Event updated: {updated_event.get('htmlLink')}")
            return self._format_event(updated_event)

        except HttpError as error:
            logger.error(f"An error occurred while updating event: {error}")
            return {}

    def delete_event(self, event_id: str) -> bool:
        """Delete an event"""
        try:
            self.service.events().delete(
                calendarId=self.calendar_id,
                eventId=event_id
            ).execute()

            logger.info(f"Event deleted: {event_id}")
            return True

        except HttpError as error:
            logger.error(f"An error occurred while deleting event: {error}")
            return False

    def search_events(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for events by query"""
        try:
            events_result = self.service.events().list(
                calendarId=self.calendar_id,
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            return self._format_events(events)

        except HttpError as error:
            logger.error(f"An error occurred while searching events: {error}")
            return []

    def get_free_busy(self, start_time: datetime, end_time: datetime) -> Dict:
        """Get free/busy information for the calendar"""
        try:
            body = {
                "timeMin": start_time.isoformat() + 'Z',
                "timeMax": end_time.isoformat() + 'Z',
                "items": [{"id": self.calendar_id}]
            }

            response = self.service.freebusy().query(body=body).execute()
            return response.get('calendars', {}).get(self.calendar_id, {})

        except HttpError as error:
            logger.error(f"An error occurred while getting free/busy info: {error}")
            return {}

    def _format_events(self, events: List[Dict]) -> List[Dict]:
        """Format events for consistent output"""
        return [self._format_event(event) for event in events]

    def _format_event(self, event: Dict) -> Dict:
        """Format a single event"""
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))

        return {
            'id': event['id'],
            'title': event.get('summary', 'No Title'),
            'start_time': start,
            'end_time': end,
            'description': event.get('description', ''),
            'location': event.get('location', ''),
            'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
            'html_link': event.get('htmlLink', ''),
            'status': event.get('status', ''),
            'created': event.get('created', ''),
            'updated': event.get('updated', '')
        }