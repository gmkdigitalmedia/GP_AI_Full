"""
Specialized Agent Types for the No-Code Agent Swarm

This module contains different types of agents, each with specialized capabilities.
New agent types can be added by inheriting from BaseAgent and implementing _execute_task.
"""

import json
import asyncio
from typing import Dict, Any
from agent_base import BaseAgent, AgentConfig, TaskConfig

class ResearcherAgent(BaseAgent):
    """
    Researcher Agent specializes in gathering and analyzing information.

    Capabilities:
    - Literature research and summarization
    - Data analysis and interpretation
    - Fact-checking and verification
    - Trend identification
    """

    async def _execute_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Execute research tasks with systematic information gathering approach.

        The researcher agent breaks down complex research into structured steps:
        1. Identify key research questions
        2. Gather relevant information
        3. Analyze and synthesize findings
        4. Present conclusions with evidence
        """
        # Enhanced prompt for research tasks
        research_prompt = f"""
        As a research agent, I need to thoroughly investigate: {task.description}

        My research approach:
        1. Break down the topic into key research questions
        2. Gather relevant information and evidence
        3. Analyze patterns and connections
        4. Synthesize findings into actionable insights

        Context from other agents: {json.dumps(context, indent=2) if context else 'None'}

        Please provide a comprehensive research report with:
        - Executive summary
        - Key findings
        - Supporting evidence
        - Recommendations for next steps
        """

        self.conversation_history.append({"role": "user", "content": research_prompt})
        response = await self._call_openai(self.conversation_history)

        # Add response to conversation history for context
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

class WriterAgent(BaseAgent):
    """
    Writer Agent specializes in content creation and communication.

    Capabilities:
    - Content writing and editing
    - Format adaptation (blogs, reports, emails)
    - Style and tone adjustment
    - Documentation creation
    """

    async def _execute_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Execute writing tasks with focus on clarity and audience engagement.

        The writer agent focuses on:
        1. Understanding target audience
        2. Structuring content effectively
        3. Maintaining consistent tone and style
        4. Ensuring clarity and readability
        """
        # Enhanced prompt for writing tasks
        writing_prompt = f"""
        As a professional writer, I need to create content for: {task.description}

        My writing process:
        1. Understand the target audience and purpose
        2. Structure the content logically
        3. Use clear, engaging language
        4. Ensure proper formatting and flow

        Input from other agents: {json.dumps(context, indent=2) if context else 'None'}

        Required output format: {self.config.output_format}

        Please create well-structured, engaging content that:
        - Meets the specified requirements
        - Is appropriate for the target audience
        - Follows best practices for the content type
        - Includes proper formatting and organization
        """

        self.conversation_history.append({"role": "user", "content": writing_prompt})
        response = await self._call_openai(self.conversation_history)

        self.conversation_history.append({"role": "assistant", "content": response})

        return response

class AnalyzerAgent(BaseAgent):
    """
    Analyzer Agent specializes in data analysis and pattern recognition.

    Capabilities:
    - Data interpretation and visualization
    - Pattern and trend identification
    - Statistical analysis
    - Performance evaluation
    """

    async def _execute_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Execute analysis tasks with systematic data evaluation approach.

        The analyzer agent focuses on:
        1. Data quality assessment
        2. Pattern and trend identification
        3. Statistical analysis
        4. Actionable insights generation
        """
        # Enhanced prompt for analysis tasks
        analysis_prompt = f"""
        As a data analyzer, I need to analyze: {task.description}

        My analysis methodology:
        1. Assess data quality and completeness
        2. Identify patterns, trends, and anomalies
        3. Apply appropriate analytical techniques
        4. Generate actionable insights and recommendations

        Data/context from other agents: {json.dumps(context, indent=2) if context else 'None'}

        Please provide a thorough analysis including:
        - Data quality assessment
        - Key patterns and trends identified
        - Statistical insights (if applicable)
        - Actionable recommendations
        - Confidence levels in findings
        """

        self.conversation_history.append({"role": "user", "content": analysis_prompt})
        response = await self._call_openai(self.conversation_history)

        self.conversation_history.append({"role": "assistant", "content": response})

        return response

class CoordinatorAgent(BaseAgent):
    """
    Coordinator Agent specializes in project management and workflow coordination.

    Capabilities:
    - Task breakdown and scheduling
    - Resource allocation
    - Progress monitoring
    - Quality assurance
    """

    async def _execute_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Execute coordination tasks with focus on project management and workflow optimization.

        The coordinator agent focuses on:
        1. Task breakdown and prioritization
        2. Resource allocation and scheduling
        3. Progress monitoring and reporting
        4. Quality assurance and integration
        """
        coordination_prompt = f"""
        As a project coordinator, I need to manage: {task.description}

        My coordination approach:
        1. Break down complex tasks into manageable components
        2. Assess resource requirements and dependencies
        3. Create realistic timelines and milestones
        4. Monitor progress and adjust plans as needed

        Current project status: {json.dumps(context, indent=2) if context else 'No prior context'}

        Please provide a coordination plan including:
        - Task breakdown with priorities
        - Resource allocation recommendations
        - Timeline with key milestones
        - Risk assessment and mitigation strategies
        - Success metrics and monitoring approach
        """

        self.conversation_history.append({"role": "user", "content": coordination_prompt})
        response = await self._call_openai(self.conversation_history)

        self.conversation_history.append({"role": "assistant", "content": response})

        return response

class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent specializes in quality assurance and evaluation.

    Capabilities:
    - Content review and editing
    - Quality assessment
    - Compliance checking
    - Improvement recommendations
    """

    async def _execute_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Execute review tasks with focus on quality assurance and improvement.

        The reviewer agent focuses on:
        1. Comprehensive quality assessment
        2. Compliance and standards checking
        3. Improvement identification
        4. Final recommendations
        """
        review_prompt = f"""
        As a quality reviewer, I need to evaluate: {task.description}

        My review process:
        1. Assess overall quality and completeness
        2. Check for accuracy and consistency
        3. Evaluate compliance with requirements
        4. Identify areas for improvement

        Content to review: {json.dumps(context, indent=2) if context else 'No content provided'}

        Please provide a comprehensive review including:
        - Overall quality assessment (score 1-10)
        - Strengths identified
        - Areas needing improvement
        - Specific recommendations for enhancement
        - Compliance status with requirements
        """

        self.conversation_history.append({"role": "user", "content": review_prompt})
        response = await self._call_openai(self.conversation_history)

        self.conversation_history.append({"role": "assistant", "content": response})

        return response

class CreativeAgent(BaseAgent):
    """
    Creative Agent specializes in innovative thinking and creative problem-solving.

    Capabilities:
    - Brainstorming and ideation
    - Creative problem-solving
    - Design thinking
    - Innovation strategies
    """

    async def _execute_task(self, task: TaskConfig, context: Dict[str, Any] = None) -> str:
        """
        Execute creative tasks with focus on innovation and out-of-the-box thinking.

        The creative agent focuses on:
        1. Divergent thinking and ideation
        2. Creative problem-solving techniques
        3. Innovation and experimentation
        4. Artistic and design considerations
        """
        creative_prompt = f"""
        As a creative innovator, I need to generate ideas for: {task.description}

        My creative process:
        1. Explore multiple perspectives and approaches
        2. Apply creative thinking techniques (brainstorming, lateral thinking)
        3. Challenge assumptions and conventional wisdom
        4. Synthesize unique and innovative solutions

        Inspiration from other agents: {json.dumps(context, indent=2) if context else 'Starting fresh'}

        Please provide creative output including:
        - Multiple innovative ideas or solutions
        - Creative approaches to the challenge
        - Unique perspectives or angles
        - Implementation possibilities
        - Potential for further development
        """

        self.conversation_history.append({"role": "user", "content": creative_prompt})
        response = await self._call_openai(self.conversation_history)

        self.conversation_history.append({"role": "assistant", "content": response})

        return response

# Agent type registry for dynamic instantiation
AGENT_TYPES = {
    "researcher": ResearcherAgent,
    "writer": WriterAgent,
    "analyzer": AnalyzerAgent,
    "coordinator": CoordinatorAgent,
    "reviewer": ReviewerAgent,
    "creative": CreativeAgent
}

def create_agent(config: AgentConfig) -> BaseAgent:
    """
    Factory function to create agents based on configuration.

    This allows the swarm system to dynamically create agents based on
    configuration files without hardcoding agent types.

    Args:
        config: AgentConfig specifying the agent type and parameters

    Returns:
        Instance of the appropriate agent class

    Raises:
        ValueError: If the specified agent role is not supported
    """
    agent_class = AGENT_TYPES.get(config.role.lower())

    if not agent_class:
        raise ValueError(f"Unsupported agent role: {config.role}. "
                        f"Available roles: {list(AGENT_TYPES.keys())}")

    return agent_class(config)