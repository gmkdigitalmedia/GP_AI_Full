"""
Base classes for the No-Code Agent Swarm System

This module provides the foundation for creating configurable AI agents
that can work together in swarms without requiring code changes.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AgentConfig(BaseModel):
    """
    Configuration model for defining agents through no-code YAML/JSON files.

    This allows users to create new agents by simply editing configuration files
    without writing any Python code.
    """
    name: str = Field(description="Unique name for the agent")
    role: str = Field(description="Agent's role (researcher, writer, analyzer, etc.)")
    system_prompt: str = Field(description="System prompt defining agent behavior")
    model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    temperature: float = Field(default=0.7, description="Response randomness (0-1)")
    max_tokens: int = Field(default=1000, description="Maximum response length")
    skills: List[str] = Field(default=[], description="List of agent capabilities")
    dependencies: List[str] = Field(default=[], description="Other agents this agent depends on")
    output_format: str = Field(default="text", description="Output format (text, json, markdown)")

class TaskConfig(BaseModel):
    """
    Configuration for tasks that can be assigned to agent swarms.

    Defines what work needs to be done and how agents should collaborate.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(description="Task name")
    description: str = Field(description="Detailed task description")
    assigned_agents: List[str] = Field(description="List of agent names to work on this task")
    workflow: List[Dict[str, Any]] = Field(description="Step-by-step workflow")
    expected_output: str = Field(description="Description of expected results")
    priority: int = Field(default=1, description="Task priority (1=highest)")

class AgentResult(BaseModel):
    """
    Standardized result format for agent outputs.

    Ensures consistent communication between agents in the swarm.
    """
    agent_name: str
    task_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool
    content: str
    metadata: Dict[str, Any] = Field(default={})
    next_steps: List[str] = Field(default=[])

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the swarm.

    This class provides the common functionality that all agent types share:
    - Configuration loading from files
    - OpenAI API integration
    - Result formatting
    - Inter-agent communication
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize the agent with configuration.

        Args:
            config: AgentConfig object defining agent behavior and capabilities
        """
        self.config = config
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.conversation_history: List[Dict[str, str]] = []
        self.results: List[AgentResult] = []

        # Initialize conversation with system prompt
        self.conversation_history.append({
            "role": "system",
            "content": self.config.system_prompt
        })

    async def process_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> AgentResult:
        """
        Process a task assigned to this agent.

        This is the main method that coordinates task execution:
        1. Prepare the task input with context
        2. Execute the agent's specific processing logic
        3. Format and return results

        Args:
            task: TaskConfig object describing the work to be done
            context: Optional context from other agents or previous steps

        Returns:
            AgentResult containing the agent's output and metadata
        """
        try:
            # Add task to conversation history
            task_message = self._prepare_task_message(task, context)
            self.conversation_history.append({"role": "user", "content": task_message})

            # Execute the agent's specific processing
            response = await self._execute_task(task, context)

            # Create result object
            result = AgentResult(
                agent_name=self.config.name,
                task_id=task.id,
                success=True,
                content=response,
                metadata={
                    "model_used": self.config.model,
                    "temperature": self.config.temperature,
                    "agent_role": self.config.role
                }
            )

            self.results.append(result)
            return result

        except Exception as e:
            # Handle errors gracefully
            error_result = AgentResult(
                agent_name=self.config.name,
                task_id=task.id,
                success=False,
                content=f"Error processing task: {str(e)}",
                metadata={"error": True, "error_type": type(e).__name__}
            )

            self.results.append(error_result)
            return error_result

    def _prepare_task_message(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Prepare the task message for the AI model.

        Combines task description with any context from other agents.
        """
        message = f"Task: {task.name}\n\nDescription: {task.description}\n\n"

        if context:
            message += "Context from other agents:\n"
            for agent_name, agent_output in context.items():
                message += f"- {agent_name}: {agent_output}\n"
            message += "\n"

        message += f"Please complete this task according to your role as a {self.config.role}."
        message += f"\nOutput format: {self.config.output_format}"

        return message

    @abstractmethod
    async def _execute_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Abstract method for task execution.

        Each agent type implements this method differently based on their role.
        This is where the agent-specific logic goes.
        """
        pass

    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """
        Make an API call to OpenAI with proper error handling.

        Centralizes OpenAI API calls for consistency and error handling.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )

            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and statistics.

        Useful for monitoring swarm performance and debugging.
        """
        successful_tasks = sum(1 for result in self.results if result.success)
        failed_tasks = len(self.results) - successful_tasks

        return {
            "name": self.config.name,
            "role": self.config.role,
            "total_tasks": len(self.results),
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "skills": self.config.skills,
            "dependencies": self.config.dependencies
        }

class SwarmMessage(BaseModel):
    """
    Standard message format for inter-agent communication.

    Enables agents to pass information to each other in a structured way.
    """
    from_agent: str
    to_agent: str
    message_type: str  # "task_result", "request", "notification"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default={})