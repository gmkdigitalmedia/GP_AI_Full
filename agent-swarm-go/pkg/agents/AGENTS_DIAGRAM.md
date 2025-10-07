# Agent Swarm - AI Agents Architecture

## System Overview Diagram

```mermaid
graph TB
    subgraph "User Interface"
        CLI[Interactive CLI]
        WEB[Web Dashboard<br/>localhost:8080]
    end

    subgraph "Orchestration Layer"
        SWARM[Swarm Coordinator<br/>Task Router & Event Publisher]
        WORKFLOW[Research Workflow<br/>Sequential Orchestrator]
    end

    subgraph "AI Agents"
        RESEARCHER[Research Agent<br/>researcher-1<br/>📚 Comprehensive Research]
        ANALYZER[Analysis Agent<br/>analyzer-1<br/>📊 Pattern Analysis]
        REPORTER[Report Agent<br/>reporter-1<br/>📝 Report Generation]
    end

    subgraph "LLM Integration"
        LLM[LLM Client<br/>OpenAI GPT-4 or<br/>Anthropic Claude]
        OPENAI[OpenAI API<br/>api.openai.com]
        ANTHROPIC[Anthropic API<br/>api.anthropic.com]
    end

    subgraph "Event System"
        EVENTBUS[Event Bus<br/>Pub/Sub System]
    end

    %% User interaction flows
    CLI -->|1. Select Research Option| WORKFLOW
    WEB -.->|Real-time Updates| EVENTBUS

    %% Workflow orchestration
    WORKFLOW -->|2. Create Research Task| SWARM
    WORKFLOW -->|4. Create Analysis Task<br/>+ Research Context| SWARM
    WORKFLOW -->|6. Create Report Task<br/>+ All Context| SWARM

    %% Task routing
    SWARM -->|3. Route by agent_type| RESEARCHER
    SWARM -->|5. Route by agent_type| ANALYZER
    SWARM -->|7. Route by agent_type| REPORTER

    %% AI processing
    RESEARCHER -->|Call LLM| LLM
    ANALYZER -->|Call LLM| LLM
    REPORTER -->|Call LLM| LLM

    %% LLM API selection
    LLM -->|If OPENAI_API_KEY| OPENAI
    LLM -->|If ANTHROPIC_API_KEY| ANTHROPIC

    %% Event publishing
    RESEARCHER -->|Publish Events| EVENTBUS
    ANALYZER -->|Publish Events| EVENTBUS
    REPORTER -->|Publish Events| EVENTBUS
    SWARM -->|Publish Events| EVENTBUS

    %% Results flow
    OPENAI -.->|AI Response| LLM
    ANTHROPIC -.->|AI Response| LLM
    LLM -.->|Research Findings| RESEARCHER
    LLM -.->|Analysis Insights| ANALYZER
    LLM -.->|Final Report| REPORTER

    %% Results back to user
    RESEARCHER -.->|Result via Events| WORKFLOW
    ANALYZER -.->|Result via Events| WORKFLOW
    REPORTER -.->|Result via Events| WORKFLOW
    WORKFLOW -.->|Display Results| CLI
    EVENTBUS -.->|Stream to Browser| WEB

    style RESEARCHER fill:#4CAF50,stroke:#2E7D32,stroke-width:3px,color:#fff
    style ANALYZER fill:#2196F3,stroke:#1565C0,stroke-width:3px,color:#fff
    style REPORTER fill:#FF9800,stroke:#E65100,stroke-width:3px,color:#fff
    style LLM fill:#9C27B0,stroke:#6A1B9A,stroke-width:3px,color:#fff
    style EVENTBUS fill:#F44336,stroke:#C62828,stroke-width:2px,color:#fff
    style WORKFLOW fill:#00BCD4,stroke:#00838F,stroke-width:2px,color:#fff
```

---

## Research Agent Detail

```mermaid
sequenceDiagram
    participant Workflow as Research Workflow
    participant Swarm as Swarm Coordinator
    participant Agent as Research Agent<br/>(researcher-1)
    participant LLM as LLM Client
    participant API as OpenAI/Anthropic API
    participant Events as Event Bus
    participant Web as Web Dashboard

    Note over Workflow: Step 1: Research Phase
    Workflow->>Swarm: Task{id: "research-001", type: "research"}
    Swarm->>Agent: Route task to researcher-1

    Agent->>Events: Publish: EventTaskReceived 📥
    Events-->>Web: Update event stream

    Agent->>Events: Publish: EventTaskStarted ⚙️
    Events-->>Web: Set agent status: processing

    Note over Agent: Build system prompt:<br/>"You are a research specialist..."
    Note over Agent: Build user prompt:<br/>"Research Task: quantum computing..."

    Agent->>LLM: Complete(system, user, history)
    LLM->>API: POST /v1/chat/completions

    Note over API: GPT-4 generates<br/>comprehensive research<br/>(10-30 seconds)

    API-->>LLM: Research findings (markdown)
    LLM-->>Agent: Research report text

    Note over Agent: Update conversation history<br/>(keep last 6 messages)

    Agent->>Events: Publish: EventTaskCompleted ✅<br/>Data: Full research report
    Events-->>Web: Display results panel
    Events-->>Workflow: Task complete signal

    Note over Workflow: Context = {research_findings: ...}
```

---

## Analysis Agent Detail

```mermaid
sequenceDiagram
    participant Workflow as Research Workflow
    participant Swarm as Swarm Coordinator
    participant Agent as Analysis Agent<br/>(analyzer-1)
    participant LLM as LLM Client
    participant API as OpenAI/Anthropic API
    participant Events as Event Bus

    Note over Workflow: Step 2: Analysis Phase<br/>Context includes research findings
    Workflow->>Swarm: Task{id: "analyze-001", type: "analysis",<br/>context: {research_findings: "..."}}
    Swarm->>Agent: Route task to analyzer-1

    Agent->>Events: Publish: EventTaskReceived 📥
    Agent->>Events: Publish: EventTaskStarted ⚙️

    Note over Agent: System prompt:<br/>"You are a data analysis specialist..."
    Note over Agent: User prompt includes:<br/>- Task description<br/>- Research findings from context

    Agent->>LLM: Complete(system, user, history)
    LLM->>API: POST /v1/chat/completions

    Note over API: AI analyzes research data<br/>Identifies patterns & insights<br/>(10-30 seconds)

    API-->>LLM: Analysis insights (markdown)
    LLM-->>Agent: Analysis report text

    Agent->>Events: Publish: EventTaskCompleted ✅<br/>Data: Full analysis report
    Events-->>Workflow: Task complete signal

    Note over Workflow: Context = {<br/>  research_findings: ...,<br/>  analysis_insights: ...<br/>}
```

---

## Report Agent Detail

```mermaid
sequenceDiagram
    participant Workflow as Research Workflow
    participant Swarm as Swarm Coordinator
    participant Agent as Report Agent<br/>(reporter-1)
    participant LLM as LLM Client
    participant API as OpenAI/Anthropic API
    participant Events as Event Bus
    participant User as User (CLI)

    Note over Workflow: Step 3: Report Phase<br/>Context includes ALL previous results
    Workflow->>Swarm: Task{id: "report-001", type: "report",<br/>context: {research_findings: ...,<br/>analysis_insights: ...}}
    Swarm->>Agent: Route task to reporter-1

    Agent->>Events: Publish: EventTaskReceived 📥
    Agent->>Events: Publish: EventTaskStarted ⚙️

    Note over Agent: System prompt:<br/>"You are a professional report writer..."
    Note over Agent: User prompt includes:<br/>- Task description<br/>- Research findings<br/>- Analysis insights

    Agent->>LLM: Complete(system, user, history)
    LLM->>API: POST /v1/chat/completions

    Note over API: AI synthesizes all data into<br/>executive-ready report<br/>(10-30 seconds)

    API-->>LLM: Professional report (markdown)
    LLM-->>Agent: Complete report text

    Agent->>Events: Publish: EventTaskCompleted ✅<br/>Data: Full executive report
    Events-->>Workflow: Task complete signal

    Workflow->>User: Display complete workflow results:<br/>- Research findings<br/>- Analysis insights<br/>- Final report
```

---

## Agent State Machine

```mermaid
stateDiagram-v2
    [*] --> Idle: Agent Created

    Idle --> Processing: Receive Task Message

    Processing --> PublishReceived: Publish EventTaskReceived
    PublishReceived --> PublishStarted: Publish EventTaskStarted
    PublishStarted --> CallLLM: Execute ProcessTask()

    CallLLM --> WaitingAPI: HTTP Request to LLM API

    WaitingAPI --> Success: API Returns Response
    WaitingAPI --> Failed: API Error

    Success --> UpdateHistory: Add to conversation history
    UpdateHistory --> PublishCompleted: Publish EventTaskCompleted

    Failed --> PublishFailed: Publish EventTaskFailed

    PublishCompleted --> Idle: Ready for next task
    PublishFailed --> Idle: Ready for next task

    Idle --> [*]: Agent.Stop() called

    note right of Processing
        Agent sets state to "processing"
        Shows in web dashboard as orange
    end note

    note right of Idle
        Agent sets state to "idle"
        Shows in web dashboard as green
    end note

    note right of CallLLM
        Typical time: 10-30 seconds
        - Research: Comprehensive findings
        - Analysis: Pattern identification
        - Report: Professional synthesis
    end note
```

---

## Event Flow Diagram

```mermaid
graph LR
    subgraph "Agent Events"
        E1[📥 EventTaskReceived<br/>Agent got task]
        E2[⚙️ EventTaskStarted<br/>Agent processing]
        E3[✅ EventTaskCompleted<br/>Task succeeded]
        E4[❌ EventTaskFailed<br/>Task failed]
    end

    subgraph "Event Bus"
        BUS[Event Publisher/Subscriber]
    end

    subgraph "Subscribers"
        WEB[Web Dashboard<br/>WebSocket Stream]
        WORKFLOW[Research Workflow<br/>Task Completion Monitor]
        LOG[Console Logger<br/>Terminal Output]
    end

    E1 --> BUS
    E2 --> BUS
    E3 --> BUS
    E4 --> BUS

    BUS --> WEB
    BUS --> WORKFLOW
    BUS --> LOG

    WEB -.->|Update| UI1[Event Stream Panel]
    WEB -.->|Update| UI2[Agent Status Cards]
    WEB -.->|Update| UI3[Task Results Panel]
    WEB -.->|Update| UI4[Statistics Counters]

    style E1 fill:#2196F3,color:#fff
    style E2 fill:#FF9800,color:#fff
    style E3 fill:#4CAF50,color:#fff
    style E4 fill:#F44336,color:#fff
```

---

## Data Flow: Context Passing Between Agents

```mermaid
flowchart TD
    START([User enters topic:<br/>"quantum computing"])

    TASK1[Task 1: Research<br/>context: empty {}]
    AGENT1[Research Agent<br/>LLM Call #1]
    RESULT1[Result 1:<br/># Research Findings<br/>- Key points...<br/>- Evidence...]

    TASK2[Task 2: Analysis<br/>context: {research_findings}]
    AGENT2[Analysis Agent<br/>LLM Call #2]
    RESULT2[Result 2:<br/># Analysis Insights<br/>- Patterns...<br/>- Correlations...]

    TASK3[Task 3: Report<br/>context: {research, analysis}]
    AGENT3[Report Agent<br/>LLM Call #3]
    RESULT3[Result 3:<br/># Executive Report<br/>- Summary...<br/>- Recommendations...]

    END([Display to User])

    START --> TASK1
    TASK1 --> AGENT1
    AGENT1 --> RESULT1

    RESULT1 -->|Add to context| TASK2
    TASK2 --> AGENT2
    AGENT2 --> RESULT2

    RESULT2 -->|Add to context| TASK3
    TASK3 --> AGENT3
    AGENT3 --> RESULT3

    RESULT3 --> END

    style AGENT1 fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style AGENT2 fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    style AGENT3 fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
```

---

## Agent Comparison Matrix

| Feature | Research Agent | Analysis Agent | Report Agent |
|---------|---------------|----------------|--------------|
| **Primary Function** | Gather information | Identify patterns | Synthesize findings |
| **System Prompt** | "Research specialist" | "Data analyst specialist" | "Professional report writer" |
| **Input** | Topic description | Research findings | Research + Analysis |
| **Output** | Research report | Analysis insights | Executive report |
| **Output Sections** | • Executive summary<br/>• Key findings<br/>• Evidence<br/>• Trends | • Data quality<br/>• Patterns<br/>• Insights<br/>• Recommendations | • Executive summary<br/>• Findings<br/>• Analysis<br/>• Recommendations |
| **Context Required** | None (first step) | Research findings | All previous results |
| **LLM Behavior** | Comprehensive research | Pattern identification | Professional synthesis |
| **Typical Response Time** | 15-30 seconds | 15-30 seconds | 15-30 seconds |
| **History Tracking** | Last 6 messages | Last 6 messages | Last 6 messages |
| **Event Publishing** | 3 events per task | 3 events per task | 3 events per task |

---

## Agent Lifecycle

```mermaid
timeline
    title Agent Lifecycle from Creation to Task Completion

    section Initialization
        Agent Created : NewResearchAgent(id, eventBus)
                      : Creates BaseAgent
                      : Creates LLM client
                      : Empty history
        Handler Registered : RegisterHandler(MessageTypeTask)
                          : Ready to receive tasks
        Added to Swarm : swarm.AddAgent(agent)
                       : Registered in agent registry
        Started : swarm.Start(ctx)
                : Goroutine begins message loop

    section Task Execution
        Task Received : Message arrives in inbox
                     : handleTask() called
        Events Published : EventTaskReceived
                        : EventTaskStarted
        LLM Processing : Build system prompt
                       : Build user prompt
                       : Call API (10-30s)
        Result Generated : AI response received
                        : Added to history
                        : Result created
        Completion : EventTaskCompleted published
                   : State returns to "idle"

    section Ready for Next
        Waiting : Agent idle in message loop
                : Ready for next task
```

---

## File Structure

```
pkg/agents/
├── research_agent.go     📚 Research specialist (this file)
├── analysis_agent.go     📊 Analysis specialist (similar structure)
├── report_agent.go       📝 Report generator (similar structure)
└── AGENTS_DIAGRAM.md     📖 This documentation file
```

---

## Quick Reference: Key Functions

### ResearchAgent
```go
// Creation
researcher := agents.NewResearchAgent("researcher-1", eventBus)

// Automatic handling (registered handler)
// handleTask(msg) - Called when task arrives
// ProcessTask(task) - Performs LLM research

// Specialty
researcher.GetSpecialty() // Returns "research"
```

### AnalysisAgent
```go
// Creation
analyzer := agents.NewAnalysisAgent("analyzer-1", eventBus)

// Specialty
analyzer.GetSpecialty() // Returns "analysis"
```

### ReportAgent
```go
// Creation
reporter := agents.NewReportAgent("reporter-1", eventBus)

// Specialty
reporter.GetSpecialty() // Returns "reporting"
```

---

## Integration Example

```go
// In cmd/main.go
func main() {
    // Create swarm
    s := swarm.NewSwarm()

    // Create all three agents
    researcher := agents.NewResearchAgent("researcher-1", s.GetEventBus())
    analyzer := agents.NewAnalysisAgent("analyzer-1", s.GetEventBus())
    reporter := agents.NewReportAgent("reporter-1", s.GetEventBus())

    // Add to swarm
    s.AddAgent(researcher)
    s.AddAgent(analyzer)
    s.AddAgent(reporter)

    // Start all agents
    s.Start(ctx)

    // Agents now ready to receive and process tasks
}
```

---

## See Also

- **CODE_DOCUMENTATION.md** - Complete system documentation
- **README.md** - User guide and features
- **QUICK_START.md** - Getting started guide
- **pkg/workflows/research_workflow.go** - Workflow orchestration
- **pkg/llm/client.go** - LLM API integration

---

*Generated for Agent Swarm Go - AI-Powered Multi-Agent System*