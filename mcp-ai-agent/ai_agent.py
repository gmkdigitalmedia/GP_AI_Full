"""
Main AI Agent with MCP Tool Integration
Uses OpenAI ChatGPT API with function calling to route to MCP servers
"""

import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from mcp_base import MCPRegistry
from filesystem_server import FileSystemServer
from web_server import WebServer
from calculator_server import CalculatorServer

class MCPAIAgent:
    """
    Main AI Agent class that orchestrates MCP (Model Context Protocol) servers
    and integrates them with OpenAI's ChatGPT API using function calling.

    This agent acts as a bridge between natural language user input and
    structured tool execution across multiple specialized servers.
    """

    def __init__(self):
        """
        Initialize the AI Agent with OpenAI client, MCP servers, and conversation history.

        Sets up:
        - OpenAI API client for ChatGPT integration
        - Rich console for formatted output
        - MCP registry to manage all tool servers
        - Conversation history with system prompt defining agent capabilities

        The system prompt tells the AI what tools are available and how to use them.
        """
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.console = Console()

        # Initialize MCP registry and servers
        self.mcp_registry = MCPRegistry()
        self._initialize_servers()

        # Conversation history
        self.conversation_history = [
            {
                "role": "system",
                "content": """You are an intelligent AI assistant with access to multiple tools through MCP (Model Context Protocol) servers.

Available tool servers:
1. Filesystem Server: read_file, write_file, list_files, search_files, delete_file
2. Web Server: wikipedia_search, wikipedia_summary, fetch_url, get_news_headlines
3. Calculator Server: calculate, solve_equation, derivative, integrate, statistics, convert_units

When users request tasks, analyze what they need and use the appropriate tools. Always explain what you're doing and show the results clearly.

Be helpful, thorough, and use tools proactively to provide comprehensive answers."""
            }
        ]

    def _initialize_servers(self):
        """
        Initialize and register all MCP servers with the registry.

        Creates instances of:
        - FileSystemServer: Handles file operations (read, write, list, search, delete)
        - WebServer: Handles web search and content retrieval (Wikipedia, URL fetching)
        - CalculatorServer: Handles mathematical operations (calculations, equations, calculus)

        Each server is registered with the MCP registry so tools can be discovered
        and executed through a unified interface.
        """
        filesystem_server = FileSystemServer()
        web_server = WebServer()
        calculator_server = CalculatorServer()

        self.mcp_registry.register_server(filesystem_server)
        self.mcp_registry.register_server(web_server)
        self.mcp_registry.register_server(calculator_server)

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Retrieve all available tools from registered MCP servers for OpenAI function calling.

        Returns:
            List of tool definitions in OpenAI function calling format.
            Each tool includes name, description, and parameter schema.

        The tools are automatically formatted for OpenAI's function calling API,
        which allows the AI to understand what tools are available and how to use them.
        """
        return self.mcp_registry.get_all_tools()

    def _execute_function_call(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool function call through the MCP registry.

        Args:
            function_name: Name of the tool to execute (e.g., 'read_file', 'wikipedia_search')
            arguments: Dictionary of arguments to pass to the tool

        Returns:
            String result from the tool execution, or error message if execution fails

        This method routes the function call to the appropriate MCP server and
        handles success/error responses uniformly.
        """
        result = self.mcp_registry.execute_tool(function_name, **arguments)

        if result["success"]:
            return result["result"]
        else:
            return f"Error: {result['error']}"

    def chat(self, user_message: str) -> str:
        """
        Process a user message and return an AI response, handling tool calls if needed.

        This is the core method that:
        1. Adds user message to conversation history.  Appended to conversation_history
        2. Calls OpenAI API with available tools
        3. If AI wants to use tools, executes them via MCP servers
        4. Gets final response after tool execution
        5. Maintains conversation context throughout

        Args:
            user_message: User's input message

        Returns:
            AI's response string (may include results from tool execution)

        The method implements the full OpenAI function calling flow:
        - Initial API call with tool definitions
        - Tool execution if requested by AI
        - Follow-up API call to generate final response with tool results
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_message})

        try:
            # Call OpenAI with available tools
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.conversation_history,
                tools=self._get_available_tools(),
                tool_choice="auto",
                temperature=0.7
            )

            assistant_message = response.choices[0].message

            # Check if AI wants to use tools
            if assistant_message.tool_calls:
                # Add assistant message with tool calls to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        }
                        for tool_call in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the function
                    function_result = self._execute_function_call(function_name, function_args)

                    # Add tool result to conversation
                    self.conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": function_result
                    })

                # Get final response after tool execution
                final_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=self.conversation_history,
                    temperature=0.7
                )

                final_message = final_response.choices[0].message.content
                self.conversation_history.append({"role": "assistant", "content": final_message})

                return final_message

            else:
                # No tools needed, just return the response
                self.conversation_history.append({"role": "assistant", "content": assistant_message.content})
                return assistant_message.content

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.conversation_history.append({"role": "assistant", "content": error_msg})
            return error_msg

    def show_available_tools(self):
        """
        Display all available tools from registered MCP servers in a formatted way.

        This method creates a nice visual display showing:
        - All registered MCP servers
        - Each server's description
        - All tools available in each server with descriptions

        Used for the 'help' command in interactive mode and tool exploration.
        Helps users understand what capabilities the agent has.
        """
        servers = self.mcp_registry.list_servers()

        self.console.print(Panel.fit("Available MCP Servers & Tools", style="bold blue"))

        for server_name, description in servers.items():
            server = self.mcp_registry.servers[server_name]
            manifest = server.get_manifest()

            self.console.print(f"\n[bold green]{server_name.upper()} SERVER[/bold green]")
            self.console.print(f"[italic]{description}[/italic]")

            for tool in manifest["tools"]:
                tool_info = tool["function"]
                self.console.print(f"  • [bold]{tool_info['name']}[/bold]: {tool_info['description']}")

    def interactive_chat(self):
        """
        Start an interactive chat session with the AI agent.

        This method provides a command-line interface where users can:
        - Type messages to chat with the AI
        - Use special commands:
          - 'help' or 'h': Show available tools
          - 'clear': Clear the terminal screen
          - 'quit', 'exit', 'q': Exit the program

        The session continues until the user chooses to quit or presses Ctrl+C.
        All conversations maintain context through the conversation history.
        """
        self.console.print(Panel.fit(
            "MCP AI Agent - Interactive Chat\nType 'quit', 'exit', or 'help' for commands",
            style="bold cyan"
        ))

        while True:
            try:
                user_input = input("\n> ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    self.console.print("Goodbye!", style="bold blue")
                    break

                elif user_input.lower() in ['help', 'h']:
                    self.show_available_tools()
                    continue

                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue

                elif not user_input:
                    continue

                # Process the message
                self.console.print(f"\n[bold blue]AI:[/bold blue]")
                response = self.chat(user_input)
                self.console.print(response)

            except KeyboardInterrupt:
                self.console.print("\nGoodbye!", style="bold blue")
                break
            except Exception as e:
                self.console.print(f"Error: {e}", style="bold red")

def main():
    """
    Main entry point for the AI agent application.

    This function:
    1. Checks for required OpenAI API key in environment
    2. Creates an instance of the MCPAIAgent
    3. Starts the interactive chat session

    If the API key is missing, displays helpful error message and exits.
    """

    # Check for OpenAI API key
    load_dotenv()
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in .env file")
        print("Please create a .env file with your OpenAI API key")
        return

    # Create and run the agent
    agent = MCPAIAgent()
    agent.interactive_chat()

if __name__ == "__main__":
    main()