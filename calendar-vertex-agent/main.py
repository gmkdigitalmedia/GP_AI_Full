"""
Main entry point for the Calendar AI Agent.
Provides both CLI and web interface for interacting with the agent.
"""

import os
import sys
import asyncio
import argparse
import json
from datetime import datetime
from typing import Dict, Any

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

from calendar_ai_agent import CalendarAIAgent, AgentResponse
from auth_manager import AuthManager

# Load environment variables
load_dotenv()

console = Console()

class CalendarAgentCLI:
    """Command-line interface for the Calendar AI Agent"""

    def __init__(self):
        self.agent = None
        self.auth_manager = AuthManager()

    async def initialize(self):
        """Initialize the agent"""
        try:
            project_id = os.getenv('PROJECT_ID')
            region = os.getenv('REGION', 'us-central1')

            if not project_id:
                console.print("[red]Error: PROJECT_ID environment variable is required[/red]")
                return False

            self.agent = CalendarAIAgent(project_id=project_id, region=region)
            console.print("[green]✅ Calendar AI Agent initialized successfully[/green]")
            return True

        except Exception as e:
            console.print(f"[red]❌ Failed to initialize agent: {e}[/red]")
            return False

    async def run_interactive(self):
        """Run the interactive CLI"""
        console.print(Panel.fit(
            "[bold blue]🤖 Calendar AI Agent[/bold blue]\n"
            "Your intelligent calendar assistant powered by Vertex AI\n\n"
            "Commands:\n"
            "• Type your request in natural language\n"
            "• 'help' - Show help\n"
            "• 'history' - Show conversation history\n"
            "• 'clear' - Clear conversation history\n"
            "• 'quit' or 'exit' - Exit the application",
            title="Welcome"
        ))

        while True:
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]👋 Goodbye![/yellow]")
                    break

                elif user_input.lower() == 'help':
                    self._show_help()

                elif user_input.lower() == 'history':
                    self._show_history()

                elif user_input.lower() == 'clear':
                    self.agent.clear_conversation_history()
                    console.print("[green]✅ Conversation history cleared[/green]")

                elif user_input:
                    await self._process_request(user_input)

                else:
                    console.print("[yellow]Please enter a command or request[/yellow]")

            except KeyboardInterrupt:
                console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                console.print(f"[red]❌ Error: {e}[/red]")

    async def _process_request(self, user_input: str):
        """Process a user request"""
        console.print(f"\n[dim]Processing your request...[/dim]")

        try:
            response = await self.agent.process_natural_language_request(user_input)
            self._display_response(response)

        except Exception as e:
            console.print(f"[red]❌ Error processing request: {e}[/red]")

    def _display_response(self, response: AgentResponse):
        """Display the agent's response"""
        if response.success:
            console.print(f"\n[bold green]🤖 Agent:[/bold green] {response.message}")

            # Display additional data if available
            if response.data:
                if 'events' in response.data:
                    self._display_events(response.data['events'])

            # Display suggestions if available
            if response.suggestions:
                console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
                for suggestion in response.suggestions:
                    console.print(f"• {suggestion}")

        else:
            console.print(f"\n[bold red]🤖 Agent:[/bold red] {response.message}")

            if response.suggestions:
                console.print("\n[bold yellow]💡 Suggestions:[/bold yellow]")
                for suggestion in response.suggestions:
                    console.print(f"• {suggestion}")

    def _display_events(self, events: list):
        """Display events in a table format"""
        if not events:
            return

        table = Table(title="📅 Calendar Events", show_header=True, header_style="bold blue")
        table.add_column("Title", style="cyan", no_wrap=False)
        table.add_column("Date/Time", style="green")
        table.add_column("Location", style="yellow")
        table.add_column("Status", style="magenta")

        for event in events[:10]:  # Limit to 10 events
            title = event.get('title', 'No Title')
            start_time = event.get('start_time', '')

            # Format datetime
            if 'T' in start_time:
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%m/%d %I:%M %p')
                except:
                    formatted_time = start_time
            else:
                formatted_time = start_time

            location = event.get('location', '')
            status = event.get('status', 'confirmed')

            table.add_row(title, formatted_time, location, status)

        console.print("\n")
        console.print(table)

    def _show_help(self):
        """Show help information"""
        help_text = """
[bold blue]📚 Calendar AI Agent Help[/bold blue]

[bold]Natural Language Examples:[/bold]
• "Schedule a meeting with John tomorrow at 2 PM"
• "What's on my calendar this week?"
• "Find my dentist appointment"
• "Cancel my 3 PM meeting today"
• "When am I free on Friday afternoon?"
• "Create a team standup every Monday at 9 AM"
• "Move my lunch meeting to next Tuesday"

[bold]Supported Actions:[/bold]
• Create events with smart scheduling
• List and search existing events
• Update event details
• Delete events
• Find available time slots
• Get calendar summaries

[bold]Commands:[/bold]
• help - Show this help
• history - Show conversation history
• clear - Clear conversation history
• quit/exit - Exit the application
"""
        console.print(Panel(help_text, title="Help"))

    def _show_history(self):
        """Show conversation history"""
        history = self.agent.get_conversation_history()

        if not history:
            console.print("[yellow]No conversation history yet[/yellow]")
            return

        console.print("\n[bold blue]📜 Conversation History:[/bold blue]\n")

        for i, entry in enumerate(history[-10:], 1):  # Show last 10 entries
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%m/%d %I:%M %p')
            console.print(f"[dim]{i}. [{timestamp}][/dim]")
            console.print(f"[bold cyan]You:[/bold cyan] {entry['user_input']}")

            analysis = entry.get('analysis', {})
            action = analysis.get('action', 'unknown')
            confidence = analysis.get('confidence', 0)

            console.print(f"[dim]   → Action: {action} (confidence: {confidence:.2f})[/dim]\n")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Calendar AI Agent")
    parser.add_argument('--mode', choices=['cli', 'web'], default='cli',
                       help='Run mode (cli or web)')
    parser.add_argument('--request', type=str,
                       help='Single request to process (non-interactive)')

    args = parser.parse_args()

    # Initialize CLI
    cli = CalendarAgentCLI()

    if not await cli.initialize():
        return 1

    # Handle single request mode
    if args.request:
        await cli._process_request(args.request)
        return 0

    # Run interactive mode
    if args.mode == 'cli':
        await cli.run_interactive()
    elif args.mode == 'web':
        console.print("[yellow]Web mode not implemented yet. Running CLI mode.[/yellow]")
        await cli.run_interactive()

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]💥 Fatal error: {e}[/red]")
        sys.exit(1)