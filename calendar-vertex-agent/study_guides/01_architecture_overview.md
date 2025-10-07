# 🏗️ Architecture Overview Study Guide (15 minutes)


 Google Calendar API
  gcloud services enable calendar-json.googleapis.com
    - Purpose: Read, create, update, delete calendar events
    - Required for: All calendar operations
  2. Vertex AI API
  gcloud services enable aiplatform.googleapis.com
    - Purpose: Natural language processing with Gemini models
    - Required for: Understanding user requests, generating responses
  3. Cloud Logging API (Optional but recommended)
  gcloud services enable logging.googleapis.com
    - Purpose: Application logging and monitoring
    - Required for: Debugging and monitoring

  Enable All APIs at Once:

  gcloud services enable \
    calendar-json.googleapis.com \
    aiplatform.googleapis.com \
    logging.googleapis.com

  Required Google Cloud Setup:

  1. Google Cloud Project

  - Create or use existing project
  - Enable billing (Vertex AI requires it)

  2. Authentication Methods:

  Option A: OAuth 2.0 (Recommended for personal use)
  # Go to Google Cloud Console → APIs & Services → Credentials
  # Create OAuth 2.0 Client ID
  # Download as credentials/credentials.json

  Option B: Service Account (For server deployment)
  gcloud iam service-accounts create calendar-ai-agent

  gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:calendar-ai-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

  gcloud iam service-accounts keys create credentials/service-account.json \
    --iam-account=calendar-ai-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com

  Required Scopes/Permissions:

  Calendar API Scopes:

  - https://www.googleapis.com/auth/calendar - Full calendar access
  - Or more restrictive: https://www.googleapis.com/auth/calendar.events

  Vertex AI Permissions:

  - roles/aiplatform.user - Use Vertex AI models
  - roles/ml.developer - (Alternative, broader access)

  Cost Considerations:

  Calendar API:

  - Free tier: 1,000,000 requests/day
  - Cost: Free for most personal use

  Vertex AI API:

  - Gemini 1.5 Pro: ~$7 per 1M input tokens, ~$21 per 1M output tokens
  - Estimated cost: $0.01-0.10 per conversation for typical usage

  Cloud Logging:

  - Free tier: 50 GB/month
  - Cost: Minimal for this application

  Quick Setup Commands:

  # 1. Set your project
  gcloud config set project YOUR_PROJECT_ID

  # 2. Enable APIs
  gcloud services enable calendar-json.googleapis.com aiplatform.googleapis.com

  # 3. Create OAuth credentials (manual step in console)
  # Go to: https://console.cloud.google.com/apis/credentials

  # 4. Verify APIs are enabled
  gcloud services list --enabled

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │  Natural Lang   │    │  Calendar API   │
│   (CLI/Text)    ├───►│  Processing     ├───►│   Operations    │
│                 │    │  (Vertex AI)    │    │  (Google Cal)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  CLI Interface  │    │   AI Agent      │    │   Auth Manager  │
│   (main.py)     │◄───┤  Orchestrator   │◄───┤   (Security)    │
│                 │    │(calendar_ai.py) │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. **Entry Point - main.py**
```python
# Purpose: User interface and application lifecycle
class CalendarAgentCLI:
    - initialize(): Set up agent
    - run_interactive(): Handle user conversations
    - process_request(): Route user input to agent
    - display_response(): Format and show results
```

### 2. **Orchestrator - calendar_ai_agent.py**
```python
# Purpose: Business logic coordinator
class CalendarAIAgent:
    - process_natural_language_request(): Main entry point
    - _execute_action(): Route to specific calendar operations
    - _create_event(), _list_events(), etc.: Calendar actions
```

### 3. **Calendar Integration - calendar_client.py**
```python
# Purpose: Google Calendar API wrapper
class CalendarClient:
    - get_upcoming_events(): Fetch calendar data
    - create_event(): Add new events
    - update_event(), delete_event(): Modify existing
    - search_events(): Find specific events
```

### 4. **AI Processing - vertex_ai_client.py**
```python
# Purpose: Natural language understanding
class VertexAIClient:
    - analyze_calendar_request(): Parse user intent
    - parse_datetime(): Convert natural language to dates
    - suggest_meeting_times(): AI-powered scheduling
```

## Data Flow

1. **User Input:** Natural language text
2. **AI Analysis:** Extract intent and parameters
3. **Action Routing:** Determine calendar operation
4. **API Execution:** Call Google Calendar API
5. **Response Generation:** Create user-friendly response
6. **Display:** Show formatted results in CLI

## Key Design Patterns

### **Dependency Injection**
- Each component receives its dependencies
- Easy to test and mock components
- Clear separation of concerns

### **Command Pattern**
- User requests mapped to specific actions
- Extensible for new calendar operations
- Consistent error handling

### **Strategy Pattern**
- Different AI models can be swapped
- Multiple authentication methods supported
- Flexible calendar backends

## Study Questions (5 minutes)

1. **Why is the agent separated from the calendar client?**
   - Allows swapping calendar providers (Outlook, etc.)
   - Easier testing with mocked calendar data
   - Clear business logic separation

2. **How does the AI processing integrate with calendar operations?**
   - AI extracts structured data from natural language
   - Agent maps AI output to calendar API calls
   - AI generates human-friendly responses

3. **What makes this architecture extensible?**
   - Plugin-style component design
   - Clear interfaces between components
   - Centralized configuration management

## Next Steps
- Dive into calendar_client.py implementation
- Understand Google Calendar API integration patterns
- Study authentication flow