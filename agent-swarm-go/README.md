# Agent Swarm in Go

A powerful AI-powered agent swarm system in Go featuring real research capabilities, concurrent multi-agent task processing, and a real-time web dashboard.

## ✨ Features

- 🤖 **Real AI-Powered Agents** - Research, Analysis, and Report generation using OpenAI or Anthropic APIs
- 🔬 **Intelligent Research Workflows** - Sequential task execution with context passing between agents
- 🎯 **Interactive CLI Interface** - Choose from pre-built scenarios or create custom workflows
- 🌐 **Real-Time Web Dashboard** - Monitor agent activity with WebSocket updates
- 🔄 **Concurrent Execution** - Agents run in parallel using goroutines
- 💬 **Message Passing** - Thread-safe communication via channels
- 📊 **Live Event Monitoring** - Track task progress and agent states in real-time

## 🚀 Quick Start

### 1. Set up API Key (for real AI research)

```bash
# Using OpenAI
export OPENAI_API_KEY="your-key-here"

# OR using Anthropic Claude
export ANTHROPIC_API_KEY="your-key-here"
```

> **Note**: Without an API key, the system runs in DEMO MODE with simulated responses.

### 2. Run the Agent Swarm

```bash
cd agent-swarm-go
go run cmd/main.go
```

**You'll get:**
- 🌐 **Web Dashboard** at http://localhost:8080 - Real-time visualization of agent activity
- 💬 **Interactive CLI** - Menu-driven task creation and monitoring
- 📊 **Live Updates** - See tasks being processed as they happen via WebSocket

**Open http://localhost:8080 in your browser to see the magic!**

## 🔬 Research Workflow Example

The Research & Analysis workflow demonstrates the power of agent swarms:

```
1. 📚 Research Agent - Gathers comprehensive information on your topic
   ↓ (passes findings to next agent)

2. 📊 Analysis Agent - Identifies patterns, trends, and insights
   ↓ (passes analysis to reporter)

3. 📝 Report Agent - Generates professional executive report
```

### Example Output:

```
Enter research topic: quantum computing

🔬 Starting Research Workflow for: quantum computing
================================================================

📚 Step 1/3: Research Phase
✅ Research completed

📊 Step 2/3: Analysis Phase
✅ Analysis completed

📝 Step 3/3: Report Generation Phase
✅ Report generated

🎉 Workflow completed in 45.2s

📋 WORKFLOW RESULTS
====================================================================
📚 RESEARCH FINDINGS
====================================================================
# Quantum Computing: Comprehensive Research Report

## Executive Summary
Quantum computing represents a paradigm shift in computational
capabilities, leveraging quantum mechanical phenomena...

[Full AI-generated research findings]

====================================================================
📊 ANALYSIS INSIGHTS
====================================================================
# Analysis of Quantum Computing Research

## Key Patterns Identified:
1. Exponential growth in quantum qubit stability
2. Strong correlation between error correction and practical applications
...

[Full AI-generated analysis]

====================================================================
📝 FINAL REPORT
====================================================================
# Executive Report: Quantum Computing

## Overview
This report synthesizes comprehensive research and analytical insights...

[Full professional report]
```

## 📁 Project Structure

```
agent-swarm-go/
├── cmd/
│   └── main.go                    # Application entry point
├── pkg/
│   ├── agents/                    # Specialized agent implementations
│   │   ├── research_agent.go      # AI-powered research agent
│   │   ├── analysis_agent.go      # Data analysis agent
│   │   └── report_agent.go        # Report generation agent
│   ├── agent/
│   │   └── base_agent.go          # Base agent implementation
│   ├── llm/
│   │   └── client.go              # LLM API client (OpenAI/Anthropic)
│   ├── workflows/
│   │   └── research_workflow.go   # Research workflow orchestration
│   ├── swarm/
│   │   └── swarm.go               # Swarm coordinator
│   ├── types/
│   │   ├── types.go               # Core types and interfaces
│   │   └── events.go              # Event system
│   ├── interactive/
│   │   └── interactive.go         # Interactive session manager
│   ├── cli/
│   │   └── cli.go                 # CLI utilities
│   ├── scenarios/
│   │   └── scenarios.go           # Pre-built workflows
│   └── web/
│       └── server.go              # Web dashboard server
├── examples/
│   ├── worker_agent.go            # Example worker agent
│   └── coordinator_agent.go       # Example coordinator agent
└── go.mod
```

## 🎮 Interactive Menu Options

When you run the application, you'll see:

1. **Research & Analysis Workflow** - AI-powered research pipeline with real results
2. **Parallel Task Processing** - Distribute multiple tasks across agents
3. **Custom Task Creation** - Build your own workflows interactively
4. **Swarm Status** - View all agents and their current states
5. **Broadcast Message** - Send messages to all agents
6. **View Agent Details** - Inspect specific agent information
7. **Run Stress Test** - Test swarm capacity with many tasks

## 🤖 Available Agents

### ResearchAgent
- Gathers comprehensive information
- Identifies key insights and trends
- Provides evidence-based findings
- Maintains conversation context

### AnalysisAgent
- Processes research data
- Identifies patterns and correlations
- Generates actionable insights
- Assesses data quality

### ReportAgent
- Synthesizes research and analysis
- Creates professional reports
- Formats content with markdown
- Provides executive summaries

## 🌐 Web Dashboard Features

The real-time web dashboard provides:

- **Live Agent Status** - See which agents are idle or processing
- **Event Stream** - Monitor all task events as they happen
- **Statistics** - Track total agents, active agents, tasks completed
- **Visual Feedback** - Color-coded agent states and event types
- **WebSocket Updates** - Zero-latency real-time updates

## 🔧 Configuration

### API Providers

The system automatically detects and uses available API keys:

1. Checks for `OPENAI_API_KEY` first (uses GPT-4)
2. Falls back to `ANTHROPIC_API_KEY` (uses Claude 3.5 Sonnet)
3. Runs in demo mode if no keys are found

### Customization

Create custom agents by implementing the `Agent` interface:

```go
type CustomAgent struct {
    *agent.BaseAgent
    // your fields
}

func NewCustomAgent(id string, eventBus *types.EventBus) *CustomAgent {
    ca := &CustomAgent{
        BaseAgent: agent.NewBaseAgent(id),
    }
    ca.RegisterHandler(types.MessageTypeTask, ca.handleTask)
    return ca
}
```

## 💡 Use Cases

- **Research & Development** - Automated literature review and analysis
- **Business Intelligence** - Market research and competitive analysis
- **Content Creation** - Topic research, analysis, and report generation
- **Data Analysis** - Pattern identification and insight generation
- **Strategic Planning** - Multi-perspective analysis and recommendations

## 🆚 Comparison with Python Version

| Feature | Python agent-swarm | Go agent-swarm-go |
|---------|-------------------|-------------------|
| Real AI Integration | ✅ OpenAI | ✅ OpenAI + Anthropic |
| Concurrent Processing | ✅ asyncio | ✅ goroutines |
| Web Dashboard | ❌ | ✅ Real-time WebSocket |
| Interactive CLI | ✅ | ✅ Enhanced |
| Context Passing | ✅ | ✅ |
| Performance | Good | Excellent |
| Deployment | Python runtime | Single binary |

## 🛠️ Building from Source

```bash
# Build binary
go build -o bin/agent-swarm cmd/main.go

# Run binary
./bin/agent-swarm
```

## 📝 Environment Variables

```bash
# Optional: OpenAI API key for real AI research
export OPENAI_API_KEY="sk-..."

# Optional: Anthropic API key (alternative to OpenAI)
export ANTHROPIC_API_KEY="sk-ant-..."
```

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:

- Additional specialized agent types
- More workflow templates
- Enhanced web dashboard features
- Integration with more LLM providers
- Performance optimizations

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Inspired by the Python agent-swarm project, reimplemented in Go with enhanced features and real AI integration.

---

**Ready to unleash the power of agent swarms? Run `go run cmd/main.go` and start researching!** 🚀