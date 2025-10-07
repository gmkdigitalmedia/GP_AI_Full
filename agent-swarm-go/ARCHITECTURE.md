# Agent Swarm Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                           │
├─────────────────────────────────┬───────────────────────────────┤
│     CLI (Terminal)              │   Web Dashboard (Browser)     │
│  - Interactive Menu             │  - Real-time Event Stream     │
│  - Task Creation                │  - Agent Status Cards         │
│  - Status Display               │  - Live Statistics            │
└────────────┬────────────────────┴──────────────┬────────────────┘
             │                                    │
             │                                    │ WebSocket
             v                                    v
┌────────────────────────────────────────────────────────────────┐
│                         SWARM LAYER                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                     Event Bus                            │ │
│  │  • Publishes all agent/task events                       │ │
│  │  • Subscribers: Web Server, CLI Monitors                 │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                  Swarm Coordinator                       │ │
│  │  • Agent Registration                                    │ │
│  │  • Task Distribution (Round-Robin)                       │ │
│  │  • Broadcasting                                          │ │
│  │  • Status Monitoring                                     │ │
│  └──────────────────────────────────────────────────────────┘ │
└───────────┬────────────────────────────────────────────────────┘
            │
            │ Distributes Tasks
            v
┌────────────────────────────────────────────────────────────────┐
│                        AGENT LAYER                              │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │  Worker 1   │  │  Worker 2   │  │  Worker 3   │            │
│  │             │  │             │  │             │            │
│  │ Specialty:  │  │ Specialty:  │  │ Specialty:  │            │
│  │   Data      │  │  Analytics  │  │  Reporting  │            │
│  │ Processing  │  │             │  │             │            │
│  │             │  │             │  │             │            │
│  │ [Inbox:100] │  │ [Inbox:100] │  │ [Inbox:100] │            │
│  │ Goroutine   │  │ Goroutine   │  │ Goroutine   │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────────────────────────────────────┐               │
│  │         Coordinator Agent                   │               │
│  │  • Receives high-level tasks                │               │
│  │  • Delegates to workers                     │               │
│  │  • Tracks completion                        │               │
│  │  [Inbox: 100]  Goroutine                    │               │
│  └─────────────────────────────────────────────┘               │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Task Processing Flow:

```
1. User Creates Task (CLI or Web)
         │
         v
2. Swarm.DistributeTask()
         │
         v
3. Find Available Agent (Round-Robin)
         │
         v
4. Agent.SendMessage(task) ──────────┐
         │                            │
         v                            v
5. Task → Agent's Inbox Channel   EventBus.Publish(task_received)
         │                            │
         v                            v
6. Agent Goroutine Reads Task     WebSocket → Browser
         │                         Console → CLI
         v
7. EventBus.Publish(task_started) ───┐
         │                            │
         v                            v
8. Agent.ProcessTask()            Updates Dashboard
         │
         v
9. Simulate Work (0.5-1.5s)
         │
         v
10. EventBus.Publish(task_completed) ─┐
         │                             │
         v                             v
11. Return Result                  Browser Shows ✅
                                   CLI Shows Completion
```

## Component Details

### 1. Event Bus (`pkg/types/events.go`)
- **Purpose**: Pub/sub system for all swarm events
- **Events**:
  - `task_received` - Agent got a task
  - `task_started` - Agent began processing
  - `task_completed` - Task finished successfully
  - `task_failed` - Task encountered error
- **Subscribers**: Web server, CLI monitors
- **Non-blocking**: Drops events if channel full

### 2. Swarm (`pkg/swarm/swarm.go`)
- **Agent Registry**: Map of agent ID → Agent interface
- **Event Bus**: Central event distribution
- **Methods**:
  - `AddAgent()` - Register new agent
  - `DistributeTask()` - Send task to available agent
  - `Broadcast()` - Message all agents
  - `GetSwarmStatus()` - Current state of all agents

### 3. Base Agent (`pkg/agent/base_agent.go`)
- **Inbox**: Buffered channel (capacity: 100)
- **State Machine**: idle → processing → idle
- **Goroutine**: Runs in background, reads from inbox
- **Handlers**: Map of message type → handler function
- **Thread-safe**: Mutex-protected state

### 4. Worker Agent (`examples/worker_agent.go`)
- **Extends**: BaseAgent
- **Specialty**: Different processing focus
- **Publishes Events**: At task receive, start, complete
- **Simulated Work**: Random delay 500ms-1500ms

### 5. Web Server (`pkg/web/server.go`)
- **HTTP Server**: Port 8080
- **WebSocket**: Real-time event streaming
- **Endpoints**:
  - `/` - Dashboard HTML
  - `/ws` - WebSocket connection
  - `/api/status` - JSON status
  - `/api/agents` - JSON agent list
- **Gorilla WebSocket**: For bidirectional communication

### 6. Interactive CLI (`pkg/interactive/interactive.go`)
- **Session Manager**: Handles user interaction
- **Event Monitoring**: Subscribes to event bus
- **Scenarios**: Pre-built workflows
- **Real-time Feedback**: Shows task progress

## Concurrency Model

```
Main Goroutine
├─ Agent 1 Goroutine (message loop)
├─ Agent 2 Goroutine (message loop)
├─ Agent 3 Goroutine (message loop)
├─ Coordinator Goroutine (message loop)
├─ Web Server Goroutine
│  ├─ HTTP Handler Goroutines (one per request)
│  ├─ WebSocket Client Goroutines (one per client)
│  └─ Event Broadcaster Goroutine
└─ CLI Session Goroutine
   └─ Event Monitor Goroutines (per scenario)

Communication: Go Channels
Synchronization: Mutexes (for shared state)
Context: For graceful shutdown
```

## Thread Safety

### Protected Resources:
1. **Swarm.agents** - RWMutex
2. **Agent.state** - RWMutex
3. **Agent.inbox** - Channel (inherently thread-safe)
4. **WebServer.clients** - RWMutex

### Lock-Free:
- Event bus publishing (channel-based)
- Agent message passing (channels)
- Goroutine spawning (Go runtime handles)

## Performance Characteristics

### Scalability:
- **Agents**: Limited by goroutine overhead (~2KB stack each)
- **Tasks**: Limited by channel buffer (100 per agent)
- **Web Clients**: Limited by WebSocket connections
- **Typical**: 10-100 agents, 1000s of tasks, 10-50 web clients

### Latency:
- **Task Distribution**: <1ms (channel send)
- **Event Publishing**: <1ms (channel broadcast)
- **WebSocket Update**: <10ms (network + serialization)
- **Task Processing**: 500ms-1500ms (simulated work)

### Bottlenecks:
1. Event bus subscribers (if channel full, drops events)
2. Agent inbox capacity (blocks if full)
3. WebSocket serialization (JSON encoding)
4. Simulated work time (intentional delay)

## Extension Points

### Adding New Agent Types:
```go
type CustomAgent struct {
    *agent.BaseAgent
    customField string
}

func NewCustomAgent(id string, eventBus *types.EventBus) *CustomAgent {
    ca := &CustomAgent{
        BaseAgent: agent.NewBaseAgent(id),
    }
    ca.RegisterHandler(types.MessageTypeTask, ca.customHandler)
    return ca
}
```

### Adding New Event Types:
```go
const EventCustom EventType = "custom_event"

eventBus.Publish(types.Event{
    Type: EventCustom,
    Timestamp: time.Now(),
    AgentID: "agent-1",
    Message: "Custom event occurred",
})
```

### Adding New Scenarios:
```go
func CustomScenario() *Scenario {
    return &Scenario{
        Name: "Custom Workflow",
        Tasks: []types.Task{
            {ID: "c-1", Description: "Step 1"},
            {ID: "c-2", Description: "Step 2"},
        },
    }
}
```