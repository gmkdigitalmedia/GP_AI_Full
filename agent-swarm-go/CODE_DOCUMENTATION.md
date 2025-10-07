# 📚 Code Documentation - All 13 Active Files Explained

This document provides extensive comments and explanations for all actively running files in the agent-swarm-go system.

---

## 1. `cmd/main.go` ✅ (FULLY COMMENTED)

**Purpose**: Application entry point that bootstraps the entire system

**What it does**:
- Loads `.env` file for API keys
- Creates swarm coordinator
- Initializes 3 AI agents (researcher, analyzer, reporter)
- Starts web dashboard on port 8080
- Launches interactive CLI
- Handles graceful shutdown

**Key Functions**:
```go
loadEnvFile(filename) // Loads KEY=VALUE pairs from .env
main()                // Orchestrates entire startup sequence
```

**Flow**:
```
Start → Load .env → Create Swarm → Create Agents → Start Web Server → Start CLI → Wait → Shutdown
```

---

## 2. `pkg/interactive/interactive.go`

**Purpose**: Interactive CLI menu system for user commands

**What it does**:
- Displays main menu with 8 options
- Gets user input
- Routes to appropriate workflow functions
- Shows formatted output

**Key Struct**:
```go
type Session struct {
    swarm *swarm.Swarm  // Reference to agent coordinator
    cli   *cli.CLI      // CLI helper functions
}
```

**Key Functions**:
```go
NewSession(s *swarm.Swarm) *Session
    // Creates new interactive session

Start()
    // Main loop: Show menu → Get choice → Execute → Repeat

runResearchAnalysis()
    // Option 1: Runs AI research workflow
    // - Prompts for topic
    // - Creates workflow
    // - Executes research → analysis → report
    // - Displays results

runParallelProcessing()
    // Option 2: Distributes N tasks in parallel

runCustomTask()
    // Option 3: User creates custom tasks

showSwarmStatus()
    // Option 4: Shows all agent states

broadcastMessage()
    // Option 5: Sends message to all agents

showAgentDetails()
    // Option 6: Shows specific agent info

runStressTest()
    // Option 7: Tests system with many tasks
```

**User Flow**:
```
User → Menu Display → Choice Input → Function Execution → Results Display → Back to Menu
```

---

## 3. `pkg/cli/cli.go`

**Purpose**: CLI helper functions for formatting and user input

**What it does**:
- Prints formatted banners
- Shows menus
- Gets user input with defaults
- Displays success/error/info messages

**Key Struct**:
```go
type CLI struct {
    // Empty - just namespacing for helper functions
}
```

**Key Functions**:
```go
NewCLI() *CLI
    // Creates new CLI helper

PrintBanner()
    // Displays ASCII art banner at startup
    // Shows "AGENT SWARM - Interactive Multi-Agent System"

ShowMainMenu()
    // Displays formatted menu with all options
    // Uses box-drawing characters for visual appeal

GetChoice(prompt string) string
    // Gets user's menu choice
    // Returns: "1", "2", etc.

GetInputWithDefault(prompt, defaultValue string) string
    // Gets user input with a default value
    // Example: "Enter topic [quantum computing]: "
    // If user presses Enter, returns "quantum computing"

GetInput(prompt string) string
    // Gets raw user input without default

WaitForEnter(message string)
    // Displays message and waits for Enter key
    // Used for "Press Enter to continue..."

PrintSection(title string)
    // Prints section header
    // Example: "=== Research & Analysis Workflow ==="

PrintSuccess(message string)
    // Prints green success message with ✓ icon

PrintError(message string)
    // Prints red error message with ✗ icon

PrintInfo(message string)
    // Prints blue info message with ℹ icon
```

**Example Usage**:
```go
cli := cli.NewCLI()
cli.PrintBanner()
cli.ShowMainMenu()
choice := cli.GetChoice("Select option")
topic := cli.GetInputWithDefault("Enter topic", "AI")
cli.PrintSuccess("Task completed!")
```

---

## 4. `pkg/workflows/research_workflow.go`

**Purpose**: Orchestrates the 3-step AI research workflow

**What it does**:
- Manages sequential execution of research → analysis → report
- Passes context (results) between steps
- Waits for each step to complete
- Displays formatted results

**Key Structs**:
```go
type ResearchWorkflow struct {
    swarm   *swarm.Swarm           // Agent coordinator
    results map[string]types.Result // Stores task results
}

type WorkflowResult struct {
    Topic       string                 // Research topic
    StartTime   time.Time             // When workflow started
    EndTime     time.Time             // When workflow ended
    Duration    time.Duration         // Total execution time
    StepResults map[string]string     // Results from each step
    FinalReport string                // Complete final report
}
```

**Key Functions**:
```go
NewResearchWorkflow(s *swarm.Swarm) *ResearchWorkflow
    // Creates new workflow handler

Execute(topic string) (*WorkflowResult, error)
    // Main workflow execution
    // Steps:
    // 1. Create research task → Distribute to researcher
    // 2. Wait for completion → Store results
    // 3. Create analysis task with research context → Distribute
    // 4. Wait for completion → Store results
    // 5. Create report task with all context → Distribute
    // 6. Wait for completion → Return final result

waitForTaskCompletion(taskID string, timeout time.Duration) types.Result
    // Subscribes to event bus
    // Waits for EventTaskCompleted or EventTaskFailed
    // Returns result or times out after duration

Display()
    // Formats and prints the complete workflow results
    // Shows: Research findings → Analysis insights → Final report

printWrapped(text string, width int)
    // Word-wraps long text for terminal display
```

**Workflow Sequence**:
```
1. Research Task Created
   ├─ ID: research-<timestamp>
   ├─ Description: "Research the topic: [topic]..."
   ├─ Payload: {type: "research", topic: topic}
   └─ Context: {} (empty)

2. Distribute to Swarm
   └─ Swarm routes to researcher-1

3. Wait for Completion (up to 60 seconds)
   └─ Monitor event bus for task_completed

4. Analysis Task Created
   ├─ ID: analyze-<timestamp>
   ├─ Description: "Analyze the research findings..."
   ├─ Payload: {type: "analysis", topic: topic}
   └─ Context: {research_findings: <result from step 1>}

5. Distribute & Wait

6. Report Task Created
   ├─ ID: report-<timestamp>
   ├─ Description: "Generate comprehensive report..."
   ├─ Payload: {type: "report", topic: topic}
   └─ Context: {research_findings: <step 1>, analysis_insights: <step 2>}

7. Distribute & Wait

8. Display Complete Results
```

---

## 5. `pkg/agents/research_agent.go`

**Purpose**: AI agent that researches topics using LLM

**What it does**:
- Receives research tasks
- Calls LLM API with research-specific prompts
- Maintains conversation history for context
- Publishes events for monitoring

**Key Struct**:
```go
type ResearchAgent struct {
    *agent.BaseAgent          // Inherits: ID, state, message handling
    llmClient *llm.Client      // LLM API client
    eventBus  *types.EventBus  // Event publisher
    history   []llm.Message    // Conversation history (last 6 messages)
}
```

**Key Functions**:
```go
NewResearchAgent(id string, eventBus *types.EventBus) *ResearchAgent
    // Creates new research agent
    // Registers handleTask as the task message handler

handleTask(msg types.Message) error
    // Called when agent receives a task
    // 1. Publishes EventTaskReceived
    // 2. Publishes EventTaskStarted
    // 3. Calls ProcessTask
    // 4. Publishes EventTaskCompleted or EventTaskFailed

ProcessTask(task types.Task) types.Result
    // Main research logic
    // Creates system prompt for research specialist
    // Creates user prompt with task description and context
    // Calls llmClient.Complete()
    // Returns AI-generated research findings

GetSpecialty() string
    // Returns "research"
```

**System Prompt** (sent to LLM):
```
You are a research specialist agent. Your role is to:
1. Break down the research topic into key questions
2. Gather and synthesize relevant information
3. Identify patterns and insights
4. Present findings clearly with evidence

Provide comprehensive, well-structured research output.
```

**User Prompt Template**:
```
Research Task: [task description]

Please provide a thorough research report including:
- Executive summary
- Key findings (3-5 main points)
- Supporting details and evidence
- Trends and patterns identified
- Recommendations for next steps

Context from previous tasks: [context data]
```

---

## 6. `pkg/agents/analysis_agent.go`

**Purpose**: AI agent that analyzes research data using LLM

**What it does**:
- Receives analysis tasks (with research context)
- Analyzes data for patterns and insights
- Calls LLM API with analysis-specific prompts
- Returns structured analysis results

**Key Struct**:
```go
type AnalysisAgent struct {
    *agent.BaseAgent
    llmClient *llm.Client
    eventBus  *types.EventBus
    history   []llm.Message
}
```

**Key Functions**: Same structure as ResearchAgent

**System Prompt** (sent to LLM):
```
You are a data analysis specialist agent. Your role is to:
1. Assess data quality and completeness
2. Identify patterns, trends, and anomalies
3. Apply analytical techniques
4. Generate actionable insights

Provide thorough, evidence-based analysis.
```

**User Prompt Template**:
```
Analysis Task: [task description]

Data/Research to analyze:
[research findings from previous step]

Please provide a comprehensive analysis including:
- Data quality assessment
- Key patterns and trends identified
- Statistical insights
- Correlations and relationships
- Actionable recommendations
- Confidence levels in findings
```

---

## 7. `pkg/agents/report_agent.go`

**Purpose**: AI agent that generates professional reports using LLM

**What it does**:
- Receives report generation tasks (with all prior context)
- Synthesizes research and analysis into reports
- Formats output professionally
- Returns executive-ready documents

**Key Struct**:
```go
type ReportAgent struct {
    *agent.BaseAgent
    llmClient *llm.Client
    eventBus  *types.EventBus
    history   []llm.Message
}
```

**System Prompt** (sent to LLM):
```
You are a professional report writer agent. Your role is to:
1. Synthesize information from research and analysis
2. Create clear, well-structured reports
3. Present findings in an executive-friendly format
4. Provide actionable recommendations

Create comprehensive, professional reports.
```

**User Prompt Template**:
```
Report Generation Task: [task description]

Research and Analysis Results:
[all previous context]

Please create a comprehensive report including:
- Executive Summary (2-3 paragraphs)
- Key Findings (clearly numbered/bulleted)
- Detailed Analysis
- Recommendations (actionable next steps)
- Conclusion

Format the report professionally with clear sections and markdown formatting.
```

---

## 8. `pkg/llm/client.go`

**Purpose**: LLM API client supporting multiple providers

**What it does**:
- Detects and configures OpenAI or Anthropic API
- Makes HTTP requests to LLM APIs
- Handles different API formats
- Provides mock responses when no API key

**Key Struct**:
```go
type Client struct {
    apiKey   string  // API key from environment
    model    string  // Model name (gpt-4 or claude-3-5-sonnet)
    provider string  // "openai", "anthropic", or "mock"
}

type Message struct {
    Role    string // "system", "user", or "assistant"
    Content string // Message text
}
```

**Key Functions**:
```go
NewClient() *Client
    // Auto-detects API keys from environment
    // Priority: OPENAI_API_KEY → ANTHROPIC_API_KEY → none (mock)
    // Returns configured client

Complete(systemPrompt, userPrompt string, history []Message) (string, error)
    // Main function to get LLM response
    // Builds message array: [system, ...history, user]
    // Routes to callOpenAI() or callAnthropic() or mockResponse()

callOpenAI(messages []Message) (string, error)
    // Makes POST request to https://api.openai.com/v1/chat/completions
    // Headers: Content-Type, Authorization: Bearer <key>
    // Body: {model: "gpt-4", messages: [...]}
    // Returns: Assistant's text response

callAnthropic(messages []Message) (string, error)
    // Makes POST request to https://api.anthropic.com/v1/messages
    // Headers: Content-Type, x-api-key, anthropic-version
    // Body: {model: "claude-3-5-sonnet", messages: [...], system: "..."}
    // Note: Anthropic handles system prompt separately
    // Returns: Assistant's text response

mockResponse(prompt string) string
    // Called when no API key is configured
    // Provides intelligent simulated responses based on keywords
    // "research" → Mock research findings
    // "analyze" → Mock analysis results
    // "report" → Mock executive report

HasAPIKey() bool
    // Returns true if API key is configured

GetProvider() string
    // Returns "openai", "anthropic", or "mock"
```

**API Request Examples**:

**OpenAI Request**:
```json
POST https://api.openai.com/v1/chat/completions
Headers:
  Content-Type: application/json
  Authorization: Bearer sk-...

Body:
{
  "model": "gpt-4",
  "messages": [
    {"role": "system", "content": "You are a research agent..."},
    {"role": "user", "content": "Research quantum computing..."}
  ]
}
```

**Anthropic Request**:
```json
POST https://api.anthropic.com/v1/messages
Headers:
  Content-Type: application/json
  x-api-key: sk-ant-...
  anthropic-version: 2023-06-01

Body:
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "system": "You are a research agent...",
  "messages": [
    {"role": "user", "content": "Research quantum computing..."}
  ]
}
```

---

## 9. `pkg/swarm/swarm.go`

**Purpose**: Agent coordinator and task router

**What it does**:
- Registers and manages agents
- Routes tasks to appropriate agents
- Publishes events to event bus
- Tracks agent states

**Key Struct**:
```go
type Swarm struct {
    agents   map[string]types.Agent  // Agent registry (ID → Agent)
    eventBus *types.EventBus         // Event publisher
    mu       sync.RWMutex            // Thread-safe access
}
```

**Key Functions**:
```go
NewSwarm() *Swarm
    // Creates new swarm with event bus

AddAgent(agent types.Agent) error
    // Registers an agent in the swarm
    // Checks for duplicate IDs

Start(ctx context.Context) error
    // Starts all registered agents
    // Each agent runs in its own goroutine

Stop() error
    // Stops all agents gracefully

DistributeTask(task types.Task) error
    // Routes task to appropriate agent based on:
    //   - task.Payload["agent_type"] (researcher/analyzer/reporter)
    //   - Or round-robin if not specified
    // Creates message and sends to agent

GetEventBus() *types.EventBus
    // Returns event bus for publishing events

GetSwarmStatus() map[string]types.AgentState
    // Returns map of agent ID → current state
    // States: "idle", "processing", "stopped"

GetAgent(id string) (types.Agent, error)
    // Retrieves agent by ID
```

**Task Routing Logic**:
```go
// If task specifies agent type in payload
if agentType := task.Payload["agent_type"]; agentType != nil {
    // Find agent with matching specialty
    if agent found {
        send task to that agent
    }
}
// Otherwise use round-robin
else {
    send to next agent in rotation
}
```

---

## 10. `pkg/agent/base_agent.go`

**Purpose**: Base agent class with common functionality

**What it does**:
- Provides message handling infrastructure
- Manages agent state (idle/processing/stopped)
- Runs message processing loop in goroutine
- Allows custom handlers to be registered

**Key Struct**:
```go
type BaseAgent struct {
    id       string                               // Unique agent ID
    state    types.AgentState                     // Current state
    inbox    chan types.Message                   // Incoming message queue
    handlers map[types.MessageType]MessageHandler // Message type → handler function
    ctx      context.Context                      // For cancellation
    cancel   context.CancelFunc                   // Stop function
    mu       sync.RWMutex                        // Thread-safe access
}

type MessageHandler func(types.Message) error
```

**Key Functions**:
```go
NewBaseAgent(id string) *BaseAgent
    // Creates new base agent with:
    //   - Buffered inbox channel (100 messages)
    //   - Empty handler map
    //   - State = idle

Start(ctx context.Context) error
    // Starts message processing loop in goroutine
    // Loop: Wait for message → Find handler → Execute → Repeat

Stop() error
    // Cancels context → Stops message loop

SendMessage(msg types.Message) error
    // Sends message to agent's inbox
    // Non-blocking: Returns error if inbox full

ReceiveMessage() (*types.Message, bool)
    // Non-blocking receive from inbox
    // Returns (message, true) or (nil, false)

RegisterHandler(msgType types.MessageType, handler MessageHandler)
    // Registers a handler function for a message type
    // Example: agent.RegisterHandler(MessageTypeTask, handleTask)

ProcessTask(task types.Task) types.Result
    // Default task processing (override in subclasses)
    // Just returns success

GetID() string
GetState() types.AgentState
SetState(state types.AgentState)
```

**Message Processing Loop**:
```go
for {
    select {
    case msg := <-agent.inbox:
        // Find handler for this message type
        if handler, exists := handlers[msg.Type] {
            // Execute handler
            handler(msg)
        }
    case <-ctx.Done():
        // Context cancelled, exit loop
        return
    }
}
```

---

## 11. `pkg/types/types.go`

**Purpose**: Core data structures and interfaces

**Key Types**:
```go
// Message: Communication between agents
type Message struct {
    From    string      // Sender agent ID
    To      string      // Recipient agent ID
    Content interface{} // Message payload (usually a Task)
    Type    MessageType // Message type (task/result/query/broadcast)
}

// MessageType: Types of messages
const (
    MessageTypeTask      MessageType = "task"
    MessageTypeResult    MessageType = "result"
    MessageTypeQuery     MessageType = "query"
    MessageTypeBroadcast MessageType = "broadcast"
)

// Task: Work to be done by an agent
type Task struct {
    ID           string                 // Unique task ID
    Description  string                 // Human-readable description
    Payload      interface{}            // Task-specific data
    Priority     int                    // Priority (1-5, 1=highest)
    Context      map[string]interface{} // Results from previous tasks
    Dependencies []string               // Task IDs that must complete first
}

// Result: Output from agent's work
type Result struct {
    TaskID  string      // Which task this is a result for
    Success bool        // Did it succeed?
    Data    interface{} // Result data (usually string)
    Error   error       // Error if failed
}

// AgentState: Current state of agent
type AgentState string
const (
    StateIdle       AgentState = "idle"       // Not processing anything
    StateProcessing AgentState = "processing" // Currently working on task
    StateStopped    AgentState = "stopped"    // Shut down
)

// Agent: Interface that all agents must implement
type Agent interface {
    GetID() string
    Start(ctx context.Context) error
    Stop() error
    SendMessage(msg Message) error
    ReceiveMessage() (*Message, bool)
    ProcessTask(task Task) Result
    GetState() AgentState
}
```

**Example Task**:
```go
task := Task{
    ID: "research-1234567890",
    Description: "Research quantum computing",
    Payload: map[string]interface{}{
        "type": "research",
        "topic": "quantum computing",
        "agent_type": "researcher",
    },
    Priority: 1,
    Context: map[string]interface{}{
        // Empty for first task, will contain results for later tasks
    },
    Dependencies: []string{}, // No dependencies
}
```

---

## 12. `pkg/types/events.go`

**Purpose**: Event system for monitoring and web dashboard

**Key Types**:
```go
// EventType: Types of events that occur
type EventType string
const (
    EventTaskReceived  EventType = "task_received"  // Agent got a task
    EventTaskStarted   EventType = "task_started"   // Agent started working
    EventTaskCompleted EventType = "task_completed" // Task finished successfully
    EventTaskFailed    EventType = "task_failed"    // Task failed
    EventAgentIdle     EventType = "agent_idle"     // Agent is idle
    EventAgentBusy     EventType = "agent_busy"     // Agent is busy
    EventMessage       EventType = "message"        // Generic message
    EventBroadcast     EventType = "broadcast"      // Broadcast message
)

// Event: Something that happened in the swarm
type Event struct {
    Type      EventType   // What happened
    Timestamp time.Time   // When it happened
    AgentID   string      // Which agent was involved
    TaskID    string      // Which task (if applicable)
    Message   string      // Human-readable message
    Data      interface{} // Event-specific data
}

// EventBus: Pub/sub system for events
type EventBus struct {
    subscribers []chan Event // List of subscriber channels
}
```

**Key Functions**:
```go
NewEventBus() *EventBus
    // Creates new event bus

Subscribe() chan Event
    // Creates new subscriber channel (buffered to 100 events)
    // Adds to subscriber list
    // Returns channel to receive events

Publish(event Event)
    // Sends event to all subscribers
    // Non-blocking: Drops event if subscriber's channel is full

Close()
    // Closes all subscriber channels
```

**Usage Example**:
```go
// Agent publishes event
eventBus.Publish(Event{
    Type:      EventTaskStarted,
    Timestamp: time.Now(),
    AgentID:   "researcher-1",
    TaskID:    "research-123",
    Message:   "Starting research on quantum computing",
})

// Web server subscribes to events
events := eventBus.Subscribe()
for event := range events {
    // Send event to WebSocket clients
    sendToWebClients(event)
}
```

---

## 13. `pkg/web/server.go`

**Purpose**: Web dashboard with real-time monitoring

**What it does**:
- Serves HTML/CSS/JavaScript dashboard
- Provides WebSocket for real-time updates
- Streams events from event bus to browser
- Displays agent status and task results

**Key Struct**:
```go
type Server struct {
    swarm       *swarm.Swarm        // Reference to swarm
    clients     map[*websocket.Conn]bool // Connected WebSocket clients
    clientsMu   sync.RWMutex        // Thread-safe access
    eventStream chan types.Event    // Events from event bus
}
```

**Key Functions**:
```go
NewServer(s *swarm.Swarm) *Server
    // Creates new web server
    // Subscribes to swarm's event bus
    // Starts broadcastEvents() in background

Start(port int) error
    // Registers HTTP handlers:
    //   GET  /          → HTML dashboard
    //   GET  /ws        → WebSocket connection
    //   GET  /api/status → JSON swarm status
    //   GET  /api/agents → JSON agent list
    // Starts HTTP server on specified port

handleIndex(w, r)
    // Serves main HTML dashboard
    // Includes embedded CSS and JavaScript
    // Features:
    //   - Agent status cards
    //   - Live event stream
    //   - Task results panel
    //   - Statistics counters
    //   - WebSocket auto-reconnect

handleWebSocket(w, r)
    // Upgrades HTTP to WebSocket
    // Adds client to subscribers
    // Sends initial status
    // Keeps connection alive

handleStatus(w, r)
    // Returns JSON: {agent_id: state, ...}

handleAgents(w, r)
    // Returns JSON: [{id: "...", state: "..."}, ...]

broadcastEvents()
    // Background goroutine
    // Reads from eventStream channel
    // Sends each event to all WebSocket clients
    // Removes disconnected clients
```

**WebSocket Message Format**:
```json
{
  "type": "task_completed",
  "timestamp": "2025-09-30T20:15:30Z",
  "agent_id": "researcher-1",
  "task_id": "research-1234567890",
  "message": "Research completed",
  "data": {
    "TaskID": "research-1234567890",
    "Success": true,
    "Data": "# Research Findings\n\n..."
  }
}
```

**Dashboard Features**:
- **Agent Cards**: Show each agent with color-coded status (green=idle, orange=processing)
- **Event Stream**: Scrolling log of all events with timestamps
- **Task Results**: Full AI-generated outputs displayed in readable format
- **Statistics**: Real-time counters for total agents, active agents, tasks completed
- **Auto-reconnect**: WebSocket automatically reconnects if connection drops

---

## Summary: How Everything Works Together

```
User runs: go run cmd/main.go
    ↓
1. main.go loads .env and creates:
   - Swarm (coordinator)
   - 3 AI Agents (researcher, analyzer, reporter)
   - Web Server (background)
   - Interactive CLI

2. User selects "1. Research & Analysis"
    ↓
3. interactive.go calls runResearchAnalysis()
   - Uses cli.go to get topic input
   - Creates ResearchWorkflow

4. research_workflow.go executes 3-step workflow:

   Step 1: Research
   ├─ Creates Task with topic
   ├─ swarm.go routes to researcher-1
   ├─ research_agent.go receives task
   ├─ Publishes events via events.go
   ├─ Calls llm/client.go
   ├─ client.go calls OpenAI API
   ├─ Returns research findings
   └─ workflow waits for completion

   Step 2: Analysis (with research context)
   ├─ Creates Task with research results in context
   ├─ Routes to analyzer-1
   ├─ analysis_agent.go processes
   ├─ Calls LLM with research data
   └─ Returns analysis insights

   Step 3: Report (with all context)
   ├─ Creates Task with research + analysis
   ├─ Routes to reporter-1
   ├─ report_agent.go processes
   ├─ Calls LLM with all data
   └─ Returns final report

5. Meanwhile, web/server.go:
   ├─ Receives all events from event bus
   ├─ Broadcasts to WebSocket clients
   └─ Updates dashboard in real-time

6. Results displayed:
   ├─ Terminal: Formatted output via cli.go
   └─ Browser: Real-time updates via web/server.go
```

---

## File Dependencies

```
cmd/main.go
  ├── pkg/swarm/swarm.go
  ├── pkg/agents/*.go
  ├── pkg/interactive/interactive.go
  ├── pkg/llm/client.go
  └── pkg/web/server.go

pkg/interactive/interactive.go
  ├── pkg/cli/cli.go
  ├── pkg/workflows/research_workflow.go
  └── pkg/scenarios/scenarios.go

pkg/workflows/research_workflow.go
  ├── pkg/swarm/swarm.go
  └── pkg/types/*.go

pkg/agents/*.go
  ├── pkg/agent/base_agent.go
  ├── pkg/llm/client.go
  ├── pkg/types/*.go

pkg/swarm/swarm.go
  ├── pkg/types/*.go
  └── pkg/agent/base_agent.go

pkg/web/server.go
  ├── pkg/swarm/swarm.go
  └── pkg/types/events.go
```

---

## Extending the System

**To add a new agent type**:
1. Create file in `pkg/agents/`
2. Inherit from `agent.BaseAgent`
3. Implement custom `ProcessTask()`
4. Register in `cmd/main.go`

**To add a new workflow**:
1. Create file in `pkg/workflows/`
2. Define workflow steps
3. Use `swarm.DistributeTask()` for each step
4. Wait for completion via event bus

**To add a new menu option**:
1. Edit `pkg/cli/cli.go` to add menu item
2. Add function in `pkg/interactive/interactive.go`
3. Update switch statement in `Start()`

---

This documentation covers all 13 active files in detail. Each file has a specific purpose and works together to create the AI-powered agent swarm system.