# 📅 Calendar API Integration Deep Dive (15 minutes)

## Google Calendar API Implementation Analysis

### **Authentication Flow**

```python
def _authenticate(self):
    """Detailed authentication process"""
    creds = None

    # 1. Try to load existing token
    if os.path.exists(self.token_path):
        creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

    # 2. Refresh if expired
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # 3. Run OAuth flow for new credentials
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

    # 4. Save for future use
    with open(self.token_path, 'w') as token:
        token.write(creds.to_json())
```

**Key Learning Points:**
- **Token Persistence:** Saves OAuth tokens to avoid re-authentication
- **Automatic Refresh:** Handles expired tokens gracefully
- **Scope Management:** Uses minimum required permissions
- **Error Handling:** Robust fallback to re-authentication

### **Event CRUD Operations**

#### **Create Event Pattern**
```python
def create_event(self, title: str, start_time: datetime, end_time: datetime,
                description: str = "", location: str = "", attendees: List[str] = None):

    # 1. Build event object matching Google Calendar API schema
    event = {
        'summary': title,           # Required: Event title
        'location': location,       # Optional: Physical/virtual location
        'description': description, # Optional: Event details
        'start': {
            'dateTime': start_time.isoformat(),  # ISO 8601 format
            'timeZone': 'UTC',                   # Timezone handling
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
    }

    # 2. Add attendees if provided
    if attendees:
        event['attendees'] = [{'email': email} for email in attendees]

    # 3. API call with error handling
    try:
        created_event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event
        ).execute()

        return self._format_event(created_event)
    except HttpError as error:
        logger.error(f"API error: {error}")
        return {}
```

#### **Query Patterns**
```python
def get_upcoming_events(self, max_results: int = 10, days_ahead: int = 7):
    """Efficient event fetching with time bounds"""

    # 1. Calculate time window
    now = datetime.utcnow().isoformat() + 'Z'  # RFC 3339 timestamp
    time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'

    # 2. Optimized API call
    events_result = self.service.events().list(
        calendarId=self.calendar_id,
        timeMin=now,           # Only future events
        timeMax=time_max,      # Limit time range
        maxResults=max_results, # Limit result size
        singleEvents=True,     # Expand recurring events
        orderBy='startTime'    # Sort chronologically
    ).execute()

    return self._format_events(events_result.get('items', []))
```

### **Data Transformation Patterns**

#### **Event Formatting Strategy**
```python
def _format_event(self, event: Dict) -> Dict:
    """Standardize Google Calendar event format for internal use"""

    # Handle both datetime and date-only events
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))

    # Create consistent internal format
    return {
        'id': event['id'],                           # Google's unique identifier
        'title': event.get('summary', 'No Title'),  # Handle missing titles
        'start_time': start,                         # Preserve original format
        'end_time': end,
        'description': event.get('description', ''),
        'location': event.get('location', ''),
        'attendees': [attendee.get('email', '') for attendee in event.get('attendees', [])],
        'html_link': event.get('htmlLink', ''),     # Direct calendar link
        'status': event.get('status', ''),          # confirmed, cancelled, etc.
        'created': event.get('created', ''),        # Creation timestamp
        'updated': event.get('updated', '')         # Last modified timestamp
    }
```

### **Advanced Calendar Features**

#### **Free/Busy Query Implementation**
```python
def get_free_busy(self, start_time: datetime, end_time: datetime) -> Dict:
    """Query availability for intelligent scheduling"""

    body = {
        "timeMin": start_time.isoformat() + 'Z',
        "timeMax": end_time.isoformat() + 'Z',
        "items": [{"id": self.calendar_id}]  # Can query multiple calendars
    }

    response = self.service.freebusy().query(body=body).execute()

    # Returns busy periods that can be used for scheduling
    return response.get('calendars', {}).get(self.calendar_id, {})
```

#### **Search Implementation**
```python
def search_events(self, query: str, max_results: int = 10) -> List[Dict]:
    """Full-text search across calendar events"""

    events_result = self.service.events().list(
        calendarId=self.calendar_id,
        q=query,                # Google's full-text search
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
```

### **Error Handling Patterns**

```python
# Consistent error handling across all methods
try:
    # API operation
    result = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
    logger.info(f"Success: {result.get('htmlLink')}")
    return self._format_event(result)

except HttpError as error:
    # Google API specific errors
    logger.error(f"HTTP {error.resp.status}: {error.content}")
    return {}

except Exception as error:
    # General errors (network, JSON parsing, etc.)
    logger.error(f"Unexpected error: {error}")
    return {}
```

## Study Questions (5 minutes)

1. **Why use ISO 8601 datetime format?**
   - Google Calendar API requirement
   - Timezone-aware representation
   - International standard for date/time interchange

2. **How does the client handle recurring events?**
   - `singleEvents=True` expands recurring events into individual instances
   - Each instance gets unique ID and timing
   - Allows modification of individual occurrences

3. **What are the rate limiting considerations?**
   - Google Calendar API: 250 quota units/user/100 seconds
   - Batch operations for efficiency
   - Implement backoff strategies for production

4. **How does the formatting layer help?**
   - Abstracts Google's API format from application logic
   - Handles missing fields gracefully
   - Consistent data structure for AI processing

## Performance Optimization Notes

- **Time Window Queries:** Always specify timeMin/timeMax to limit data
- **Field Selection:** Use 'fields' parameter to fetch only needed data
- **Batch Operations:** Group multiple operations when possible
- **Caching:** Consider caching frequently accessed events locally