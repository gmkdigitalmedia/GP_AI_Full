# 🤖 Calendar AI Agent

An intelligent calendar management system that combines Google Calendar API with Google Vertex AI to provide natural language calendar interactions.

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

## ✨ Features

- **Natural Language Processing**: Interact with your calendar using plain English
- **Smart Event Creation**: AI-powered event descriptions and scheduling
- **Intelligent Time Suggestions**: Find optimal meeting times based on availability
- **Event Management**: Create, update, delete, and search calendar events
- **Free Time Finding**: Identify available time slots automatically
- **Conversation History**: Track interactions for better context
- **Security**: Built-in authentication and input sanitization

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Project** with the following APIs enabled:
   - Calendar API
   - Vertex AI API
   - Cloud Logging API

2. **Authentication Credentials**:
   - OAuth 2.0 credentials (for user authentication)
   - Service account key (optional, for server-to-server)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd calendar-vertex-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up Google credentials:**
   ```bash
   mkdir credentials
   # Place your credentials.json (OAuth) or service-account.json in the credentials folder
   ```

### Configuration

#### Environment Variables (.env)

```env
PROJECT_ID=your-gcp-project-id
REGION=us-central1
CALENDAR_ID=primary
VERTEX_AI_MODEL=gemini-1.5-pro
GOOGLE_APPLICATION_CREDENTIALS=credentials/service-account.json
```

#### Google Cloud Setup

1. **Enable APIs:**
   ```bash
   gcloud services enable calendar-json.googleapis.com
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable logging.googleapis.com
   ```

2. **Create OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Download as `credentials.json`

3. **Create Service Account (optional):**
   ```bash
   gcloud iam service-accounts create calendar-ai-agent
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:calendar-ai-agent@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

## 📖 Usage

### Command Line Interface

Start the interactive CLI:
```bash
python main.py
```

Or process a single request:
```bash
python main.py --request "Schedule a team meeting tomorrow at 2 PM"
```

### Example Interactions

```
🤖 Calendar AI Agent
Your intelligent calendar assistant powered by Vertex AI

You: Schedule a meeting with John tomorrow at 2 PM
🤖 Agent: ✅ Event 'Meeting with John' created successfully for December 15 at 02:00 PM

You: What's on my calendar this week?
🤖 Agent: You have 5 events this week. Here are the highlights:
- Team Standup (Monday at 9:00 AM)
- Client Review (Wednesday at 2:00 PM)
- Project Planning (Friday at 10:00 AM)

You: When am I free on Friday afternoon?
🤖 Agent: Here are some available time slots:
1. Friday, December 15 at 02:00 PM - Good afternoon slot after lunch
2. Friday, December 15 at 04:00 PM - End of day availability
```

### Natural Language Examples

The agent understands various natural language patterns:

- **Creating Events:**
  - "Schedule a dentist appointment next Tuesday at 10 AM"
  - "Set up a team retrospective for Friday afternoon"
  - "Book a lunch meeting with Sarah tomorrow"

- **Finding Information:**
  - "What meetings do I have today?"
  - "Find my appointment with Dr. Smith"
  - "Show me next week's schedule"

- **Managing Events:**
  - "Cancel my 3 PM meeting"
  - "Move the standup to 9:30 AM"
  - "Add location to my client meeting"

- **Finding Time:**
  - "When am I free tomorrow afternoon?"
  - "Find a 30-minute slot this week for a call"
  - "What's my availability on Monday?"

## 🏗️ Architecture

### Core Components

1. **CalendarClient** (`calendar_client.py`)
   - Google Calendar API integration
   - Event CRUD operations
   - Free/busy time queries

2. **VertexAIClient** (`vertex_ai_client.py`)
   - Natural language processing
   - Intent recognition and parameter extraction
   - Smart suggestions and summaries

3. **CalendarAIAgent** (`calendar_ai_agent.py`)
   - Main orchestrator
   - Business logic coordination
   - Response formatting

4. **AuthManager** (`auth_manager.py`)
   - Authentication and security
   - Rate limiting and input sanitization
   - Session management

### Data Flow

```
User Input → AI Analysis → Intent Recognition → Calendar Action → AI Response
```

1. User provides natural language input
2. Vertex AI analyzes intent and extracts parameters
3. Agent determines appropriate calendar action
4. Calendar API executes the action
5. AI generates human-friendly response

## 🔧 API Reference

### CalendarAIAgent Methods

```python
# Process natural language request
response = await agent.process_natural_language_request("Schedule a meeting tomorrow")

# Get conversation history
history = agent.get_conversation_history()

# Clear conversation history
agent.clear_conversation_history()
```

### AgentResponse Structure

```python
@dataclass
class AgentResponse:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
```

## 🔒 Security Features

- **Input Sanitization**: Prevents injection attacks
- **Rate Limiting**: Protects against abuse
- **Authentication**: Secure Google OAuth integration
- **Session Management**: Secure session handling
- **Audit Logging**: Security event tracking

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Test individual components:
```bash
# Test calendar integration
python -c "from calendar_client import CalendarClient; client = CalendarClient(); print(client.get_upcoming_events())"

# Test AI analysis
python -c "from vertex_ai_client import VertexAIClient; client = VertexAIClient(); print(client.analyze_calendar_request('Schedule a meeting tomorrow'))"
```

## 📊 Monitoring and Logging

The agent includes comprehensive logging:

- **Application Logs**: Standard Python logging
- **Security Events**: Authentication and authorization
- **API Calls**: Google Calendar and Vertex AI interactions
- **User Interactions**: Request/response tracking

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Docker Deployment
```bash
# Build image
docker build -t calendar-ai-agent .

# Run container
docker run -it --env-file .env calendar-ai-agent
```

### Cloud Run Deployment
```bash
gcloud run deploy calendar-ai-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check the inline code documentation
- **Examples**: See the `examples/` directory for more use cases

## 🗺️ Roadmap

- [ ] Web interface with FastAPI
- [ ] Multi-calendar support
- [ ] Recurring event intelligence
- [ ] Meeting transcription integration
- [ ] Slack/Teams integration
- [ ] Voice input support
- [ ] Advanced scheduling algorithms
- [ ] Calendar analytics and insights