"""
Base MCP Server class that all tools inherit from.
This demonstrates the MCP protocol structure.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import json

class MCPServer(ABC):
    """Base class for MCP servers"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools = {}  
        self._register_tools()

    @abstractmethod
    def _register_tools(self):
        """Register available tools for this server"""
        pass

    def add_tool(self, name: str, description: str, parameters: Dict[str, Any], handler):
        """Add a tool to this MCP server"""
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler
        }

    def get_manifest(self) -> Dict[str, Any]:  
        """Return the server manifest (available tools)"""
        tools_schema = []
        for tool_name, tool_info in self.tools.items():
            tools_schema.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_info["description"],
                    "parameters": tool_info["parameters"]
                }
            })

        return {
            "server_name": self.name,
            "server_description": self.description,
            "tools": tools_schema
        }

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool with given parameters"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found in server '{self.name}'"
            }

        try:
            result = self.tools[tool_name]["handler"](**kwargs)
            return {
                "success": True,
                "result": result,
                "tool": tool_name,
                "server": self.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error executing {tool_name}: {str(e)}",
                "tool": tool_name,
                "server": self.name
            }

class MCPRegistry:
    """Registry to manage multiple MCP servers"""

    def __init__(self):
        self.servers = {}

    def register_server(self, server: MCPServer):
        """Register an MCP server"""
        self.servers[server.name] = server

    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools from all servers"""
        all_tools = []
        for server in self.servers.values():
            manifest = server.get_manifest()
            all_tools.extend(manifest["tools"])
        return all_tools

    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute a tool across all servers"""
        for server in self.servers.values():
            if tool_name in server.tools:
                return server.execute_tool(tool_name, **kwargs)

        return {
            "success": False,
            "error": f"Tool '{tool_name}' not found in any registered server"
        }

    def list_servers(self) -> Dict[str, str]:
        """List all registered servers"""
        return {name: server.description for name, server in self.servers.items()}