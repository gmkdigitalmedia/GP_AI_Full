#!/usr/bin/env python3
"""
Interactive Demo for No-Code Agent Swarms

This demo showcases how multiple AI agents can work together on complex tasks
using only configuration files - no coding required to create new agents!
"""

import asyncio
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from swarm_orchestrator import SwarmOrchestrator
from agent_base import TaskConfig, AgentConfig
from agent_types import create_agent

class SwarmDemo:
    """
    Interactive demonstration of the agent swarm system.

    Shows real-world scenarios where multiple AI agents collaborate
    to complete complex tasks through configuration-driven workflows.
    """

    def __init__(self):
        """Initialize the demo with console and orchestrator."""
        self.console = Console()
        self.orchestrator = SwarmOrchestrator()

    def check_setup(self):
        """
        Verify that the system is properly configured.

        Checks for OpenAI API key and configuration files.
        """
        from dotenv import load_dotenv
        load_dotenv()

        if not os.getenv('OPENAI_API_KEY'):
            self.console.print(Panel(
                "ERROR: OPENAI_API_KEY not found in .env file\n\n"
                "Please:\n"
                "1. Copy .env.example to .env\n"
                "2. Add your OpenAI API key to the .env file\n"
                "3. Run the demo again",
                style="bold red"
            ))
            return False
        return True

    def show_banner(self):
        """Display the demo banner with system overview."""
        banner = """
[bold cyan]NO-CODE AGENT SWARM DEMO[/bold cyan]
[dim]Multiple AI Agents Working Together[/dim]

This demo shows how to create AI agent swarms using only configuration files!

Key Features:
• 6 different agent types (researcher, writer, analyzer, etc.)
• No-code agent creation via YAML configs
• Workflow orchestration and task distribution
• Real-time collaboration between agents
• Automatic result aggregation and reporting

All agents are defined in simple YAML files - no Python coding required!
        """
        self.console.print(Panel(banner, expand=False))

    async def load_agents(self):
        """Load all agents from configuration files."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Loading agents from config files...", total=None)
            await self.orchestrator.load_agents_from_config("configs")
            progress.update(task, completed=True)

        if not self.orchestrator.agents:
            self.console.print("[red]No agents loaded! Check the configs directory.[/red]")
            return False

        self.console.print(f"[green]Loaded {len(self.orchestrator.agents)} agents successfully![/green]")
        return True

    def show_demo_menu(self):
        """Display available demo scenarios."""
        table = Table(title="Agent Swarm Demo Scenarios", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Scenario", style="green")
        table.add_column("Agents Involved", style="yellow")
        table.add_column("Description", style="dim")

        scenarios = [
            ("1", "Research Report", "Researcher → Writer → Reviewer", "Research a topic and create a polished report"),
            ("2", "Product Launch Plan", "Creative → Coordinator → Analyzer", "Brainstorm and plan a product launch"),
            ("3", "Content Marketing", "Researcher → Creative → Writer", "Create engaging marketing content"),
            ("4", "Business Analysis", "Analyzer → Coordinator → Reviewer", "Analyze business data and create action plan"),
            ("5", "Innovation Workshop", "Creative → Researcher → Writer", "Generate and document innovative ideas"),
            ("6", "Quality Audit", "All Agents", "Comprehensive quality review process"),
            ("7", "Custom Workflow", "User Choice", "Create your own agent workflow"),
            ("8", "Agent Status", "View Only", "Show current status of all agents")
        ]

        for option, scenario, agents, description in scenarios:
            table.add_row(option, scenario, agents, description)

        self.console.print(table)

    async def run_research_report_demo(self):
        """Demo: Research Report Creation Pipeline"""
        self.console.print(Panel("Research Report Creation Pipeline", style="bold blue"))

        topic = Prompt.ask("What topic would you like to research?", default="artificial intelligence")

        # Create workflow task
        task = self.orchestrator.create_workflow_from_template(
            "research_and_write",
            topic=topic,
            content_type="comprehensive report",
            task_name=f"Research Report: {topic}",
            description=f"Create a detailed research report about {topic}",
            expected_output="A well-researched, professionally written report"
        )

        self.console.print(f"\n[bold]Executing workflow:[/bold] {task.name}")

        # Execute the task
        results = await self.orchestrator.execute_task(task)

        # Save and display results
        filename = self.orchestrator.save_results(task.id, f"research_report_{topic.replace(' ', '_')}.json")

        self.console.print(Panel("Research Report Completed!", style="bold green"))
        self.show_workflow_results(results)

    async def run_product_launch_demo(self):
        """Demo: Product Launch Planning"""
        self.console.print(Panel("Product Launch Planning Workflow", style="bold blue"))

        product = Prompt.ask("What product are you launching?", default="AI-powered mobile app")

        # Create custom workflow for product launch
        workflow = [
            {"agent": "creative_innovator", "description": "Generate launch ideas",
             "instruction": f"Generate creative marketing and launch strategies for {product}"},
            {"agent": "project_coordinator", "description": "Create launch plan",
             "instruction": "Create a detailed project plan for the product launch"},
            {"agent": "data_analyzer", "description": "Analyze market potential",
             "instruction": "Analyze the market potential and success factors for the launch plan"}
        ]

        task = TaskConfig(
            name=f"Product Launch: {product}",
            description=f"Comprehensive launch planning for {product}",
            assigned_agents=["creative_innovator", "project_coordinator", "data_analyzer"],
            workflow=workflow,
            expected_output="Complete product launch strategy and plan"
        )

        self.console.print(f"\n[bold]Executing workflow:[/bold] {task.name}")

        # Execute the task
        results = await self.orchestrator.execute_task(task)

        # Save and display results
        filename = self.orchestrator.save_results(task.id, f"product_launch_{product.replace(' ', '_')}.json")

        self.console.print(Panel("Product Launch Plan Completed!", style="bold green"))
        self.show_workflow_results(results)

    async def run_content_marketing_demo(self):
        """Demo: Content Marketing Creation"""
        self.console.print(Panel("Content Marketing Creation Pipeline", style="bold blue"))

        brand = Prompt.ask("What brand/company are you creating content for?", default="TechStartup Inc")
        content_type = Prompt.ask("What type of content?", default="blog post", choices=["blog post", "social media", "newsletter", "website copy"])

        # Create custom workflow
        workflow = [
            {"agent": "research_specialist", "description": "Market research",
             "instruction": f"Research {brand}'s target audience, competitors, and market trends"},
            {"agent": "creative_innovator", "description": "Content strategy",
             "instruction": f"Develop creative content angles and messaging strategies for {content_type}"},
            {"agent": "content_writer", "description": "Create content",
             "instruction": f"Write engaging {content_type} content for {brand} incorporating research and creative strategy"}
        ]

        task = TaskConfig(
            name=f"Content Marketing: {brand}",
            description=f"Create {content_type} content for {brand}",
            assigned_agents=["research_specialist", "creative_innovator", "content_writer"],
            workflow=workflow,
            expected_output=f"Professional {content_type} content ready for publication"
        )

        results = await self.orchestrator.execute_task(task)
        filename = self.orchestrator.save_results(task.id, f"content_marketing_{brand.replace(' ', '_')}.json")

        self.console.print(Panel("Content Marketing Completed!", style="bold green"))
        self.show_workflow_results(results)

    async def run_parallel_brainstorm_demo(self):
        """Demo: Parallel Agent Brainstorming"""
        self.console.print(Panel("Parallel Agent Brainstorming Session", style="bold blue"))

        challenge = Prompt.ask("What challenge would you like agents to brainstorm solutions for?",
                              default="reducing office energy consumption")

        # Create task for parallel execution
        task = TaskConfig(
            name=f"Brainstorm: {challenge}",
            description=f"Generate diverse solutions and perspectives for: {challenge}",
            assigned_agents=["creative_innovator", "data_analyzer", "project_coordinator"],
            workflow=[],  # Empty workflow for parallel execution
            expected_output="Multiple unique perspectives and solution approaches"
        )

        self.console.print(f"\n[bold]Running parallel brainstorm:[/bold] {task.name}")

        # Execute in parallel mode
        results = await self.orchestrator.execute_parallel_task(task)

        filename = self.orchestrator.save_results(task.id, f"brainstorm_{challenge.replace(' ', '_')}.json")

        self.console.print(Panel("Brainstorming Session Completed!", style="bold green"))
        self.show_workflow_results(results)

    async def run_custom_workflow_demo(self):
        """Demo: User-defined custom workflow"""
        self.console.print(Panel("Custom Workflow Creator", style="bold blue"))

        # Show available agents
        self.orchestrator.show_swarm_status()

        # Get user input for custom workflow
        task_name = Prompt.ask("Enter task name", default="Custom Analysis Task")
        description = Prompt.ask("Enter task description", default="Analyze and provide recommendations")

        available_agents = list(self.orchestrator.agents.keys())
        self.console.print(f"\nAvailable agents: {', '.join(available_agents)}")

        # Build workflow interactively
        workflow = []
        step_num = 1

        while True:
            agent_name = Prompt.ask(f"Step {step_num} - Choose agent (or 'done' to finish)",
                                  choices=available_agents + ["done"])

            if agent_name == "done":
                break

            step_description = Prompt.ask(f"What should {agent_name} do in this step?")
            workflow.append({
                "agent": agent_name,
                "description": f"Step {step_num}: {step_description}",
                "instruction": step_description
            })

            step_num += 1

        if not workflow:
            self.console.print("[yellow]No workflow steps defined[/yellow]")
            return

        # Create and execute custom task
        task = TaskConfig(
            name=task_name,
            description=description,
            assigned_agents=[step["agent"] for step in workflow],
            workflow=workflow,
            expected_output="Custom workflow results"
        )

        results = await self.orchestrator.execute_task(task)
        filename = self.orchestrator.save_results(task.id, f"custom_workflow.json")

        self.console.print(Panel("Custom Workflow Completed!", style="bold green"))
        self.show_workflow_results(results)

    def show_workflow_results(self, results: dict):
        """Display the results of a workflow execution."""
        if not results:
            self.console.print("[yellow]No results to display[/yellow]")
            return

        for agent_name, result in results.items():
            status_style = "green" if result.success else "red"
            status_text = "SUCCESS" if result.success else "FAILED"

            self.console.print(f"\n[bold {status_style}]{agent_name.upper()} - {status_text}[/bold {status_style}]")
            self.console.print(Panel(result.content[:500] + "..." if len(result.content) > 500 else result.content,
                                   title=f"{agent_name} Output", style=status_style))

    async def run_demo(self):
        """Main demo runner."""
        if not self.check_setup():
            return

        self.show_banner()

        # Load agents
        if not await self.load_agents():
            return

        # Show initial agent status
        self.orchestrator.show_swarm_status()

        while True:
            self.console.print("\n" + "="*70)
            self.show_demo_menu()

            choice = Prompt.ask("\nSelect a demo scenario", choices=["1", "2", "3", "4", "5", "6", "7", "8", "quit"])

            if choice == "quit":
                break
            elif choice == "1":
                await self.run_research_report_demo()
            elif choice == "2":
                await self.run_product_launch_demo()
            elif choice == "3":
                await self.run_content_marketing_demo()
            elif choice == "4":
                await self.run_parallel_brainstorm_demo()
            elif choice == "5":
                task = self.orchestrator.create_workflow_from_template("brainstorm_and_analyze",
                                                                     problem="improve team productivity")
                results = await self.orchestrator.execute_task(task)
                self.orchestrator.save_results(task.id)
                self.show_workflow_results(results)
            elif choice == "6":
                # Quality audit with all agents
                workflow = [
                    {"agent": "research_specialist", "description": "Gather quality data", "instruction": "Research current quality standards and benchmarks"},
                    {"agent": "data_analyzer", "description": "Analyze quality metrics", "instruction": "Analyze the quality data and identify patterns"},
                    {"agent": "quality_reviewer", "description": "Comprehensive review", "instruction": "Conduct thorough quality assessment and provide recommendations"}
                ]
                task = TaskConfig(name="Quality Audit", description="Comprehensive quality review", assigned_agents=["research_specialist", "data_analyzer", "quality_reviewer"], workflow=workflow, expected_output="Quality audit report")
                results = await self.orchestrator.execute_task(task)
                self.show_workflow_results(results)
            elif choice == "7":
                await self.run_custom_workflow_demo()
            elif choice == "8":
                self.orchestrator.show_swarm_status()

            if choice not in ["8", "quit"]:
                if not Confirm.ask("\nTry another demo scenario?"):
                    break

        self.console.print("\nThanks for exploring the Agent Swarm system!", style="bold cyan")
        self.console.print("Check the 'outputs' directory for saved results!", style="dim")

def main():
    """Run the agent swarm demo."""
    demo = SwarmDemo()
    asyncio.run(demo.run_demo())

if __name__ == "__main__":
    main()