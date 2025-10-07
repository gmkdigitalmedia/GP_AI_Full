"""
Vertex AI client for natural language processing and AI capabilities.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
from google.cloud import logging as cloud_logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VertexAIClient:
    def __init__(self, project_id: str = None, region: str = None, model_name: str = None):
        self.project_id = project_id or os.getenv('PROJECT_ID')
        self.region = region or os.getenv('REGION', 'us-central1')
        self.model_name = model_name or os.getenv('VERTEX_AI_MODEL', 'gemini-1.5-pro')

        if not self.project_id:
            raise ValueError("PROJECT_ID must be set in environment or passed as parameter")

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.region)

        # Initialize the model
        self.model = GenerativeModel(self.model_name)

        # Configure generation parameters
        self.generation_config = {
            "max_output_tokens": 8192,
            "temperature": 0.6,
            "top_p": 0.95,
        }

        # Configure safety settings
        self.safety_settings = {
            generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        }

        logger.info(f"Initialized Vertex AI client with model: {self.model_name}")

    def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate a response using Vertex AI"""
        try:
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            response = self.model.generate_content(
                [full_prompt],
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                stream=False
            )

            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            else:
                logger.warning("No response generated from Vertex AI")
                return "I'm sorry, I couldn't generate a response. Please try again."

        except Exception as error:
            logger.error(f"Error generating response: {error}")
            return f"Error: {str(error)}"

    def analyze_calendar_request(self, user_input: str, calendar_context: str = "") -> Dict[str, Any]:
        """Analyze user input to determine calendar action and extract parameters"""

        analysis_prompt = f"""
        You are an AI assistant that analyzes user requests related to calendar management.

        Current calendar context: {calendar_context}

        User request: "{user_input}"

        Analyze the user's request and determine:
        1. The intended action (create, update, delete, search, list, get_free_time)
        2. Extract relevant parameters like:
           - Event title/summary
           - Date and time information
           - Duration
           - Location
           - Attendees
           - Description
           - Any specific constraints or preferences

        Respond with a JSON object in this format:
        {{
            "action": "create|update|delete|search|list|get_free_time",
            "confidence": 0.0-1.0,
            "parameters": {{
                "title": "event title",
                "start_time": "ISO datetime or natural language",
                "end_time": "ISO datetime or natural language",
                "duration": "duration in minutes",
                "date": "date if specified",
                "time": "time if specified",
                "location": "location",
                "attendees": ["email1", "email2"],
                "description": "description",
                "search_query": "search terms",
                "event_id": "id for update/delete"
            }},
            "clarifications_needed": ["list of any information that needs clarification"],
            "natural_language_response": "friendly response to the user"
        }}

        Only include parameters that are clearly specified in the request.
        """

        try:
            response = self.generate_response(analysis_prompt)

            # Try to parse JSON response
            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "").strip()

            result = json.loads(response)
            return result

        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response}")
            return {
                "action": "unknown",
                "confidence": 0.0,
                "parameters": {},
                "clarifications_needed": ["Could not understand the request"],
                "natural_language_response": "I'm sorry, I couldn't understand your request. Could you please rephrase it?"
            }
        except Exception as error:
            logger.error(f"Error analyzing calendar request: {error}")
            return {
                "action": "error",
                "confidence": 0.0,
                "parameters": {},
                "clarifications_needed": ["System error occurred"],
                "natural_language_response": "I encountered an error while processing your request. Please try again."
            }

    def parse_datetime(self, datetime_str: str, reference_time: datetime = None) -> Optional[datetime]:
        """Parse natural language datetime using AI"""

        if reference_time is None:
            reference_time = datetime.now()

        parse_prompt = f"""
        Parse the following date/time expression into an ISO datetime format.

        Current time: {reference_time.isoformat()}
        Expression to parse: "{datetime_str}"

        Consider:
        - Relative expressions like "tomorrow", "next week", "in 2 hours"
        - Specific dates like "January 15th", "12/25"
        - Times like "2 PM", "14:30", "noon"
        - Combined expressions like "tomorrow at 3 PM"

        Respond with only the ISO datetime string (YYYY-MM-DDTHH:MM:SS) or "INVALID" if cannot parse.
        Example: 2024-01-15T15:00:00
        """

        try:
            response = self.generate_response(parse_prompt).strip()

            if response == "INVALID":
                return None

            # Try to parse the response as datetime
            return datetime.fromisoformat(response)

        except Exception as error:
            logger.error(f"Error parsing datetime '{datetime_str}': {error}")
            return None

    def suggest_meeting_times(self, request: str, busy_periods: List[Dict],
                            duration_minutes: int = 60, days_ahead: int = 7) -> List[Dict]:
        """Suggest optimal meeting times based on availability and preferences"""

        suggestion_prompt = f"""
        You are a smart calendar assistant. Based on the meeting request and availability information,
        suggest optimal meeting times.

        Meeting request: "{request}"
        Duration needed: {duration_minutes} minutes
        Days to look ahead: {days_ahead}

        Current busy periods: {json.dumps(busy_periods, indent=2)}

        Consider:
        - Business hours (9 AM - 6 PM typically)
        - Avoiding lunch time (12 PM - 1 PM)
        - Preference for morning vs afternoon based on request
        - Buffer time between meetings
        - Weekday vs weekend preferences

        Provide 3-5 suggested time slots in JSON format:
        {{
            "suggestions": [
                {{
                    "start_time": "ISO datetime",
                    "end_time": "ISO datetime",
                    "reason": "why this time is good",
                    "confidence": 0.0-1.0
                }}
            ],
            "explanation": "brief explanation of the suggestions"
        }}
        """

        try:
            response = self.generate_response(suggestion_prompt)

            if response.startswith("```json"):
                response = response.replace("```json", "").replace("```", "").strip()

            result = json.loads(response)
            return result.get("suggestions", [])

        except Exception as error:
            logger.error(f"Error suggesting meeting times: {error}")
            return []

    def summarize_calendar_events(self, events: List[Dict]) -> str:
        """Generate a natural language summary of calendar events"""

        summary_prompt = f"""
        Create a concise, friendly summary of the following calendar events:

        {json.dumps(events, indent=2)}

        Include:
        - Total number of events
        - Key highlights (important meetings, deadlines, etc.)
        - Time conflicts if any
        - Overall schedule density
        - Any patterns or observations

        Keep the summary conversational and helpful.
        """

        return self.generate_response(summary_prompt)

    def generate_smart_description(self, title: str, context: str = "") -> str:
        """Generate a smart event description based on title and context"""

        description_prompt = f"""
        Generate a professional and helpful description for a calendar event.

        Event title: "{title}"
        Additional context: "{context}"

        Create a brief, informative description that includes:
        - Purpose or objective if inferrable
        - Suggested agenda items if appropriate
        - Any preparation notes if relevant

        Keep it concise but useful (2-4 sentences).
        """

        return self.generate_response(description_prompt)