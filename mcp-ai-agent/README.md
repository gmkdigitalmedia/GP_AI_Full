# MCP AI Agent

A powerful AI agent that demonstrates the Model Context Protocol (MCP) by integrating ChatGPT with multiple specialized tool servers.

## What is MCP?

Model Context Protocol (MCP) is like "USB for AI agents" - it provides a standard way for AI agents to connect to external tools and data sources. Instead of custom integrations for each tool, MCP creates a unified interface.

## Features

This demo includes **3 MCP Servers** with **15 total tools**:

### 1. File System Server
- `read_file` - Read file contents
- `write_file` - Write content to files
- `list_files` - List files with glob patterns
- `search_files` - Search text within files
- `delete_file` - Delete files

### 2. Web Server
- `wikipedia_search` - Search Wikipedia articles
- `wikipedia_summary` - Get detailed Wikipedia summaries
- `fetch_url` - Extract content from web pages
- `get_news_headlines` - Get current events

### 3. Calculator Server
- `calculate` - Basic math expressions
- `solve_equation` - Solve algebraic equations
- `derivative` - Calculate derivatives
- `integrate` - Calculate integrals
- `statistics` - Statistical analysis
- `convert_units` - Unit conversions

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up OpenAI API
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run the Demo
```bash
python demo.py
```

### 4. Or Chat Directly
```bash
python ai_agent.py
```

## Demo Scenarios

The interactive demo includes these scenarios:

1. **Research Assistant** - Search Wikipedia, save notes, analyze content
2. **Math Tutor** - Solve equations, calculate derivatives, statistics
3. **Content Creator** - Generate content, save to files, research topics
4. **Data Analyst** - Calculate statistics, create reports
5. **Study Helper** - Research topics, create summaries, organize notes
6. **Free Chat** - Open conversation with all tools
7. **Tool Explorer** - Browse all available capabilities

## How It Works

### MCP Architecture
```
[ChatGPT API] ↔ [AI Agent] ↔ [MCP Registry] ↔ [Multiple MCP Servers]
                                                    ├── File System
                                                    ├── Web Search
                                                    └── Calculator
```

### Example Interaction
```
User: "Research quantum computing and save a summary to a file"

AI Agent:
1. Uses wikipedia_search to find quantum computing info
2. Uses wikipedia_summary to get detailed content
3. Uses write_file to save the summary
4. Reports back with results
```

## Sample Conversations

### Research Assistant
```
You: Research artificial intelligence and create study notes

AI: I'll help you research AI and create comprehensive study notes.

[Uses wikipedia_search for "artificial intelligence"]
[Uses wikipedia_summary for detailed content]
[Uses write_file to save "ai_study_notes.txt"]

I've researched artificial intelligence and created detailed study notes
covering machine learning, neural networks, and AI applications.
The notes are saved in ai_study_notes.txt (2,847 characters).
```

### Math Tutor
```
You: Solve x^2 + 5x + 6 = 0 and find the derivative of x^3 + 2x

AI: I'll solve that equation and calculate the derivative for you.

[Uses solve_equation for quadratic equation]
[Uses derivative for the polynomial]

Equation: x^2 + 5x + 6 = 0
Solutions: x = -2, x = -3

Derivative of x^3 + 2x:
Result: 3x^2 + 2
```

### Content Creator
```
You: Write a blog post about blockchain and save it

AI: I'll research blockchain technology and create a comprehensive blog post.

[Uses wikipedia_search for "blockchain"]
[Uses wikipedia_summary for detailed info]
[Uses write_file to save blog post]

I've created a detailed blog post about blockchain technology covering
its principles, applications, and impact. The post is saved as
"blockchain_blog_post.txt" and is ready for publication.
```

## Technical Details

### MCP Server Structure
Each MCP server inherits from `MCPServer` base class:

```python
class FileSystemServer(MCPServer):
    def _register_tools(self):
        self.add_tool("read_file", "Read file contents", {...}, self._read_file)
        # ... more tools
```

### Tool Registration
Tools are automatically registered with OpenAI function calling:

```python
{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read contents of a file",
        "parameters": {...}
    }
}
```

### Function Execution
AI decides which tools to use, and MCP Registry routes the calls:

```python
result = self.mcp_registry.execute_tool(function_name, **arguments)
```

## File Structure

```
mcp-ai-agent/
├── ai_agent.py           # Main AI agent with ChatGPT integration
├── demo.py              # Interactive demo with scenarios
├── mcp_base.py          # Base MCP classes and registry
├── filesystem_server.py # File operations MCP server
├── web_server.py        # Web search MCP server
├── calculator_server.py # Math operations MCP server
├── requirements.txt     # Python dependencies
├── .env.example        # Environment template
├── workspace/          # File operations workspace (auto-created)
└── README.md          # This file
```

## Educational Value

This demo teaches:

1. **MCP Protocol Concepts** - Standardized tool interfaces
2. **Function Calling** - OpenAI function calling with real tools
3. **Modular Architecture** - Separate servers for different capabilities
4. **Tool Registry Pattern** - Dynamic tool discovery and routing
5. **Error Handling** - Robust error handling across multiple systems
6. **Real-world Applications** - Practical use cases for AI agents

## Extending the System

Add new MCP servers by:

1. Creating a new server class inheriting from `MCPServer`
2. Implementing `_register_tools()` method
3. Adding tool handlers
4. Registering with `MCPRegistry`

Example:
```python
class DatabaseServer(MCPServer):
    def _register_tools(self):
        self.add_tool("query_db", "Execute SQL query", {...}, self._query_db)
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Missing**
   - Create `.env` file with `OPENAI_API_KEY=your_key`

2. **Import Errors**
   - Run `pip install -r requirements.txt`

3. **File Permission Errors**
   - Check workspace directory permissions

4. **Wikipedia/Web Requests Failing**
   - Check internet connection
   - Some requests may timeout (normal)

## Course Discussion Points

This project demonstrates:

- **MCP Architecture**: How standardized protocols enable tool interoperability
- **AI Function Calling**: Practical implementation of ChatGPT function calling
- **Modular Design**: Separation of concerns across different servers
- **Real-world Applications**: Practical use cases for AI agents
- **Error Handling**: Robust system design across multiple components
- **Extensibility**: How to add new capabilities through additional servers

Perfect for teaching modern AI agent development patterns and the future of AI tool integration!