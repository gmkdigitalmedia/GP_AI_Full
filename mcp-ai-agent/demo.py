#!/usr/bin/env python3
"""
Interactive Demo for MCP AI Agent
Showcases real-world use cases of the AI agent with multiple MCP servers
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from ai_agent import MCPAIAgent

class MCPDemo:
    def __init__(self):
        self.console = Console()
        self.agent = None

    def check_setup(self):
        """Check if everything is properly set up"""
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
        """Show the demo banner"""
        banner = """
[bold cyan]GP's MCP AI AGENT DEMO[/bold cyan]
[dim]Model Context Protocol + ChatGPT Integration[/dim]

This demo showcases an AI agent that can:
• Manage files and documents
• Search Wikipedia and web content
• Perform complex mathematical calculations
• Solve equations and do statistics
• All through natural conversation!
        """
        self.console.print(Panel(banner, expand=False))

    def show_demo_menu(self):
        """Show available demo scenarios"""
        table = Table(title="Demo Scenarios", show_header=True, header_style="bold magenta")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Scenario", style="green")
        table.add_column("Description", style="dim")

        scenarios = [
            ("1", "Research Assistant", "Search Wikipedia, save notes, analyze content"),
            ("2", "Math Tutor", "Solve equations, calculate derivatives, statistics"),
            ("3", "Content Creator", "Generate content, save to files, research topics"),
            ("4", "Data Analyst", "Calculate statistics, create reports, save results"),
            ("5", "Study Helper", "Research topics, create summaries, organize notes"),
            ("6", "Free Chat", "Open conversation with all tools available"),
            ("7", "Tool Explorer", "See all available tools and their capabilities")
        ]

        for option, scenario, description in scenarios:
            table.add_row(option, scenario, description)

        self.console.print(table)

    def run_research_assistant_demo(self):
        """Demo: Research Assistant scenario"""
        self.console.print(Panel("Research Assistant Demo", style="bold blue"))

        scenarios = [
            "Research quantum computing and save a summary to a file",
            "Look up information about AI agents and make notes",
            "Search for recent developments in AI and agents",
            "Find information about AI and the future and organize findings"
        ]

        self.console.print("Suggested research tasks:")
        for i, scenario in enumerate(scenarios, 1):
            self.console.print(f"  {i}. {scenario}")

        choice = Prompt.ask("\nChoose a task (1-4) or type your own research request")

        if choice.isdigit() and 1 <= int(choice) <= 4:
            request = scenarios[int(choice) - 1]
        else:
            request = choice

        self.console.print(f"\n[bold green]You:[/bold green] {request}")
        response = self.agent.chat(request)
        self.console.print(f"\n[bold blue]AI:[/bold blue] {response}")

    def run_math_tutor_demo(self):
        """Demo: Math Tutor scenario"""
        self.console.print(Panel("Math Tutor Demo", style="bold blue"))

        problems = [
            "Solve the equation x^2 + 5x + 6 = 0",
            "Calculate the derivative of x^3 + 2x^2 + x + 1",
            "Find the integral of sin(x) from 0 to pi",
            "Calculate statistics for these test scores: 85, 92, 78, 96, 88, 75, 91"
        ]

        self.console.print("Suggested math problems:")
        for i, problem in enumerate(problems, 1):
            self.console.print(f"  {i}. {problem}")

        choice = Prompt.ask("\nChoose a problem (1-4) or type your own math question")

        if choice.isdigit() and 1 <= int(choice) <= 4:
            request = problems[int(choice) - 1]
        else:
            request = choice

        self.console.print(f"\n[bold green]You:[/bold green] {request}")
        response = self.agent.chat(request)
        self.console.print(f"\n[bold blue]AI:[/bold blue] {response}")

    def run_content_creator_demo(self):
        """Demo: Content Creator scenario"""
        self.console.print(Panel("Content Creator Demo", style="bold blue"))

        tasks = [
            "Write a blog post about AI agents and save it to a file",
            "Research the history of the Artificial Intelligence and create an article",
            "Generate a technical explanation of MCP agents and servers and save it",
            "Create a guide about MLOps Orchestration and organize it in files"
        ]

        self.console.print("Suggested content creation tasks:")
        for i, task in enumerate(tasks, 1):
            self.console.print(f"  {i}. {task}")

        choice = Prompt.ask("\nChoose a task (1-4) or describe your content creation need")

        if choice.isdigit() and 1 <= int(choice) <= 4:
            request = tasks[int(choice) - 1]
        else:
            request = choice

        self.console.print(f"\n[bold green]You:[/bold green] {request}")
        response = self.agent.chat(request)
        self.console.print(f"\n[bold blue]AI:[/bold blue] {response}")

    def run_data_analyst_demo(self):
        """Demo: Data Analyst scenario"""
        self.console.print(Panel("Data Analyst Demo", style="bold blue"))

        tasks = [
            "Analyze these sales numbers and create a report: 150, 200, 175, 300, 250, 180, 220",
            "Calculate conversion rates and save analysis: 1000 visitors, 50 signups, 10 purchases",
            "Convert units and analyze: Convert 100 kg to pounds and calculate shipping costs",
            "Statistical analysis of exam scores: 78, 85, 92, 67, 88, 95, 72, 84, 91, 76"
        ]

        self.console.print("Suggested analysis tasks:")
        for i, task in enumerate(tasks, 1):
            self.console.print(f"  {i}. {task}")

        choice = Prompt.ask("\nChoose a task (1-4) or describe your analysis need")

        if choice.isdigit() and 1 <= int(choice) <= 4:
            request = tasks[int(choice) - 1]
        else:
            request = choice

        self.console.print(f"\n[bold green]You:[/bold green] {request}")
        response = self.agent.chat(request)
        self.console.print(f"\n[bold blue]AI:[/bold blue] {response}")

    def run_study_helper_demo(self):
        """Demo: Study Helper scenario"""
        self.console.print(Panel("Study Helper Demo", style="bold blue"))

        tasks = [
            "Help me study photosynthesis - research and create study notes",
            "Explain calculus derivatives with examples and save to a study guide",
            "Research World War 2 and create organized notes with key facts",
            "Study programming algorithms and create a reference file"
        ]

        self.console.print("Suggested study tasks:")
        for i, task in enumerate(tasks, 1):
            self.console.print(f"  {i}. {task}")

        choice = Prompt.ask("\nChoose a task (1-4) or describe what you want to study")

        if choice.isdigit() and 1 <= int(choice) <= 4:
            request = tasks[int(choice) - 1]
        else:
            request = choice

        self.console.print(f"\n[bold green]You:[/bold green] {request}")
        response = self.agent.chat(request)
        self.console.print(f"\n[bold blue]AI:[/bold blue] {response}")

    def run_free_chat_demo(self):
        """Demo: Free chat with all tools"""
        self.console.print(Panel("Free Chat Mode - All Tools Available", style="bold blue"))
        self.console.print("You can ask anything! The AI has access to:")
        self.console.print("• File operations (read, write, search)")
        self.console.print("• Web research (Wikipedia, content fetching)")
        self.console.print("• Math calculations (equations, calculus, statistics)")
        self.console.print("• Unit conversions")
        self.console.print("\nType 'back' to return to demo menu\n")

        while True:
            user_input = Prompt.ask("[bold green]You[/bold green]")

            if user_input.lower() in ['back', 'menu', 'return']:
                break

            response = self.agent.chat(user_input)
            self.console.print(f"\n[bold blue]AI:[/bold blue] {response}\n")

    def show_tool_explorer(self):
        """Show all available tools"""
        self.console.print(Panel("Tool Explorer - All Available Capabilities", style="bold blue"))
        self.agent.show_available_tools()

    def run_demo(self):
        """Main demo runner"""
        if not self.check_setup():
            return

        self.show_banner()

        # Initialize the agent
        try:
            self.console.print("Initializing AI Agent with MCP servers...", style="dim")
            self.agent = MCPAIAgent()
            self.console.print("Ready!", style="bold green")
        except Exception as e:
            self.console.print(f"Error initializing agent: {e}", style="bold red")
            return

        while True:
            self.console.print("\n" + "="*60)
            self.show_demo_menu()

            choice = Prompt.ask("\nSelect a demo scenario", choices=["1", "2", "3", "4", "5", "6", "7", "quit"])

            if choice == "quit":
                break
            elif choice == "1":
                self.run_research_assistant_demo()
            elif choice == "2":
                self.run_math_tutor_demo()
            elif choice == "3":
                self.run_content_creator_demo()
            elif choice == "4":
                self.run_data_analyst_demo()
            elif choice == "5":
                self.run_study_helper_demo()
            elif choice == "6":
                self.run_free_chat_demo()
            elif choice == "7":
                self.show_tool_explorer()

            if choice != "6":  # Free chat has its own loop
                if not Confirm.ask("\nTry another demo?"):
                    break

        self.console.print("\nThanks for trying the MCP AI Agent demo!", style="bold cyan")

def main():
    """Run the demo"""
    demo = MCPDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()