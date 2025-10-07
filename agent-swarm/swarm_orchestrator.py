"""
Swarm Orchestrator - Coordinates Multiple AI Agents

This module manages the execution of tasks across multiple agents,
handling dependencies, communication, and result aggregation.
"""

import asyncio
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.live import Live

from agent_base import BaseAgent, AgentConfig, TaskConfig, AgentResult, SwarmMessage
from agent_types import create_agent

class SwarmOrchestrator:
    """
    Central coordinator for managing agent swarms.

    The orchestrator handles:
    - Agent lifecycle management
    - Task distribution and scheduling
    - Inter-agent communication
    - Result aggregation and reporting
    - Workflow execution
    """

    def __init__(self):
        """
        Initialize the swarm orchestrator.

        Sets up the management infrastructure for coordinating multiple agents
        working together on complex tasks.
        """
        self.agents: Dict[str, BaseAgent] = {}
        self.tasks: Dict[str, TaskConfig] = {}
        self.results: Dict[str, List[AgentResult]] = {}
        self.messages: List[SwarmMessage] = []
        self.console = Console()

        # Create output directory if it doesn't exist
        Path("outputs").mkdir(exist_ok=True)

    async def load_agents_from_config(self, config_dir: str = "configs") -> None:
        """
        Load agent configurations from YAML/JSON files in the config directory.

        This enables no-code agent creation - users can define new agents
        by simply adding configuration files without writing Python code.

        Args:
            config_dir: Directory containing agent configuration files
        """
        config_path = Path(config_dir)

        if not config_path.exists():
            self.console.print(f"[yellow]Warning: Config directory '{config_dir}' not found[/yellow]")
            return

        # Load all YAML and JSON configuration files
        config_files = list(config_path.glob("*.yaml")) + list(config_path.glob("*.yml")) + list(config_path.glob("*.json"))

        if not config_files:
            self.console.print(f"[yellow]No configuration files found in '{config_dir}'[/yellow]")
            return

        for config_file in config_files:
            try:
                # Load configuration based on file type
                if config_file.suffix.lower() in ['.yaml', '.yml']:
                    with open(config_file, 'r') as f:
                        config_data = yaml.safe_load(f)
                else:  # JSON
                    with open(config_file, 'r') as f:
                        config_data = json.load(f)

                # Create agent configuration
                agent_config = AgentConfig(**config_data)

                # Create and register the agent
                agent = create_agent(agent_config)
                self.agents[agent_config.name] = agent

                self.console.print(f"[green]Loaded agent: {agent_config.name} ({agent_config.role})[/green]")

            except Exception as e:
                self.console.print(f"[red]Error loading {config_file}: {str(e)}[/red]")

    def add_agent(self, agent_config: AgentConfig) -> None:
        """
        Manually add an agent to the swarm.

        Args:
            agent_config: Configuration for the agent to add
        """
        agent = create_agent(agent_config)
        self.agents[agent_config.name] = agent
        self.console.print(f"[green]Added agent: {agent_config.name} ({agent_config.role})[/green]")

    async def execute_task(self, task_config: TaskConfig) -> Dict[str, AgentResult]:
        """
        Execute a task using the assigned agents.

        Coordinates the execution of a task across multiple agents,
        handling dependencies and passing results between agents.

        Args:
            task_config: Configuration describing the task to execute

        Returns:
            Dictionary mapping agent names to their results
        """
        self.console.print(Panel(f"Executing Task: {task_config.name}", style="bold blue"))

        task_results = {}
        context = {}

        # Execute workflow steps in order
        for step in task_config.workflow:
            agent_name = step.get("agent")
            step_description = step.get("description", "")

            if agent_name not in self.agents:
                self.console.print(f"[red]Error: Agent '{agent_name}' not found[/red]")
                continue

            # Create a sub-task for this step
            step_task = TaskConfig(
                name=f"{task_config.name} - {step_description}",
                description=step.get("instruction", step_description),
                assigned_agents=[agent_name],
                workflow=[],
                expected_output=step.get("expected_output", "")
            )

            self.console.print(f"[cyan]Step: {agent_name} - {step_description}[/cyan]")

            # Execute the step with current context
            result = await self.agents[agent_name].process_task(step_task, context)
            task_results[agent_name] = result

            # Add result to context for next agents
            if result.success:
                context[agent_name] = result.content
                self.console.print(f"[green]✓ {agent_name} completed successfully[/green]")
            else:
                self.console.print(f"[red]✗ {agent_name} failed: {result.content}[/red]")

            # Optional delay between steps
            if step.get("delay"):
                await asyncio.sleep(step["delay"])

        # Store results
        self.results[task_config.id] = list(task_results.values())

        return task_results

    async def execute_parallel_task(self, task_config: TaskConfig) -> Dict[str, AgentResult]:
        """
        Execute a task with agents working in parallel.

        All assigned agents work on the task simultaneously,
        useful for brainstorming or getting multiple perspectives.

        Args:
            task_config: Configuration describing the task to execute

        Returns:
            Dictionary mapping agent names to their results
        """
        self.console.print(Panel(f"Executing Parallel Task: {task_config.name}", style="bold green"))

        # Create tasks for all assigned agents
        agent_tasks = []
        for agent_name in task_config.assigned_agents:
            if agent_name in self.agents:
                agent_tasks.append(
                    self.agents[agent_name].process_task(task_config)
                )
            else:
                self.console.print(f"[red]Warning: Agent '{agent_name}' not found[/red]")

        # Execute all tasks in parallel
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)

        # Process results
        task_results = {}
        for i, result in enumerate(results):
            agent_name = task_config.assigned_agents[i]
            if isinstance(result, Exception):
                self.console.print(f"[red]Error in {agent_name}: {str(result)}[/red]")
            else:
                task_results[agent_name] = result
                if result.success:
                    self.console.print(f"[green]✓ {agent_name} completed[/green]")
                else:
                    self.console.print(f"[red]✗ {agent_name} failed[/red]")

        # Store results
        self.results[task_config.id] = list(task_results.values())

        return task_results

    def save_results(self, task_id: str, filename: str = None) -> str:
        """
        Save task results to a file.

        Args:
            task_id: ID of the task whose results to save
            filename: Optional custom filename

        Returns:
            Path to the saved file
        """
        if task_id not in self.results:
            raise ValueError(f"No results found for task ID: {task_id}")

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"swarm_results_{task_id[:8]}_{timestamp}.json"

        filepath = Path("outputs") / filename

        # Prepare results for JSON serialization
        results_data = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "results": []
        }

        for result in self.results[task_id]:
            results_data["results"].append({
                "agent_name": result.agent_name,
                "success": result.success,
                "content": result.content,
                "timestamp": result.timestamp.isoformat(),
                "metadata": result.metadata
            })

        # Save to file
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)

        self.console.print(f"[green]Results saved to: {filepath}[/green]")
        return str(filepath)

    def show_swarm_status(self) -> None:
        """
        Display current status of all agents in the swarm.

        Shows a comprehensive overview of agent performance and capabilities.
        """
        if not self.agents:
            self.console.print("[yellow]No agents loaded[/yellow]")
            return

        # Create status table
        table = Table(title="Swarm Status", show_header=True, header_style="bold magenta")
        table.add_column("Agent Name", style="cyan")
        table.add_column("Role", style="green")
        table.add_column("Total Tasks", justify="right")
        table.add_column("Success Rate", justify="right")
        table.add_column("Skills", style="dim")

        for agent_name, agent in self.agents.items():
            status = agent.get_status()
            success_rate = 0 if status["total_tasks"] == 0 else \
                         (status["successful_tasks"] / status["total_tasks"]) * 100

            table.add_row(
                agent_name,
                status["role"].title(),
                str(status["total_tasks"]),
                f"{success_rate:.1f}%",
                ", ".join(status["skills"][:3])  # Show first 3 skills
            )

        self.console.print(table)

    def create_workflow_from_template(self, template_name: str, **kwargs) -> TaskConfig:
        """
        Create a task workflow from a predefined template.

        Templates provide common workflow patterns that can be reused
        with different parameters.

        Args:
            template_name: Name of the workflow template
            **kwargs: Parameters to customize the template

        Returns:
            TaskConfig ready for execution
        """
        templates = {
            "research_and_write": [
                {"agent": "researcher", "description": "Research the topic",
                 "instruction": f"Research {kwargs.get('topic', 'the assigned topic')} thoroughly"},
                {"agent": "writer", "description": "Create content based on research",
                 "instruction": f"Write a {kwargs.get('content_type', 'article')} based on the research"},
                {"agent": "reviewer", "description": "Review and improve the content",
                 "instruction": "Review the content for quality and suggest improvements"}
            ],

            "brainstorm_and_analyze": [
                {"agent": "creative", "description": "Generate creative ideas",
                 "instruction": f"Brainstorm creative solutions for {kwargs.get('problem', 'the given problem')}"},
                {"agent": "analyzer", "description": "Analyze the feasibility of ideas",
                 "instruction": "Analyze the proposed ideas for feasibility and potential impact"},
                {"agent": "coordinator", "description": "Create implementation plan",
                 "instruction": "Create a plan to implement the best ideas"}
            ],

            "content_pipeline": [
                {"agent": "researcher", "description": "Gather information",
                 "instruction": f"Research {kwargs.get('topic', 'the topic')} and gather relevant information"},
                {"agent": "creative", "description": "Generate content ideas",
                 "instruction": "Generate creative angles and approaches for the content"},
                {"agent": "writer", "description": "Create the content",
                 "instruction": f"Write engaging {kwargs.get('content_type', 'content')} incorporating the research and creative ideas"},
                {"agent": "reviewer", "description": "Final review and polish",
                 "instruction": "Review, edit, and polish the content for publication"}
            ]
        }

        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}. Available: {list(templates.keys())}")

        workflow = templates[template_name]

        return TaskConfig(
            name=kwargs.get('task_name', f"{template_name.replace('_', ' ').title()} Task"),
            description=kwargs.get('description', f"Execute {template_name} workflow"),
            assigned_agents=[step["agent"] for step in workflow],
            workflow=workflow,
            expected_output=kwargs.get('expected_output', "Completed workflow results")
        )