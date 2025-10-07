# AI Agents - Specialized Agent Implementations

This directory contains the three specialized AI-powered agents that form the core of the research workflow.

## 📂 Files

### 1. **research_agent.go** (12 KB - Extensively Commented)
- **ResearchAgent**: Conducts comprehensive research on any topic
- **Specialty**: Information gathering, synthesis, and insight identification
- **Output**: Detailed research reports with findings and evidence
- **Comments**: ✅ Fully documented with 300+ lines of inline documentation

### 2. **analysis_agent.go** (3.5 KB)
- **AnalysisAgent**: Analyzes research data for patterns and insights
- **Specialty**: Data analysis, pattern recognition, correlation identification
- **Output**: Analysis reports with insights and recommendations
- **Comments**: ⚠️ Basic comments (can be enhanced like research_agent.go)

### 3. **report_agent.go** (3.6 KB)
- **ReportAgent**: Synthesizes research and analysis into professional reports
- **Specialty**: Executive report writing, synthesis, recommendations
- **Output**: Professional executive-ready reports
- **Comments**: ⚠️ Basic comments (can be enhanced like research_agent.go)

### 4. **AGENTS_DIAGRAM.md** (15 KB - Visual Documentation)
- Comprehensive Mermaid diagrams showing:
  - System architecture
  - Sequence diagrams for each agent
  - State machines
  - Event flows
  - Data context passing
  - Comparison matrices
  - Integration examples

### 5. **README.md** (This File)
- Quick reference guide to the agents directory

---

## 🎯 Quick Start

### Creating Agents

```go
import "agent-swarm-go/pkg/agents"

// Create event bus for publishing events
eventBus := types.NewEventBus()

// Create the three specialized agents
researcher := agents.NewResearchAgent("researcher-1", eventBus)
analyzer := agents.NewAnalysisAgent("analyzer-1", eventBus)
reporter := agents.NewReportAgent("reporter-1", eventBus)

// Add to swarm
swarm.AddAgent(researcher)
swarm.AddAgent(analyzer)
swarm.AddAgent(reporter)

// Start all agents
swarm.Start(ctx)
```

### Agent Specialties

```go
researcher.GetSpecialty() // Returns: "research"
analyzer.GetSpecialty()   // Returns: "analysis"
reporter.GetSpecialty()   // Returns: "reporting"
```

---

## 🔄 How Agents Work Together

```
User Input: "quantum computing"
    ↓
┌─────────────────────────────────────────┐
│ Step 1: Research Agent                  │
│ • Receives: Topic                       │
│ • Context: {} (empty)                   │
│ • LLM Call: Research specialist         │
│ • Output: Comprehensive research report │
└─────────────────────────────────────────┘
    ↓ (Context passed)
┌─────────────────────────────────────────┐
│ Step 2: Analysis Agent                  │
│ • Receives: Analysis request            │
│ • Context: {research_findings: ...}     │
│ • LLM Call: Data analyst                │
│ • Output: Pattern analysis & insights   │
└─────────────────────────────────────────┘
    ↓ (All context passed)
┌─────────────────────────────────────────┐
│ Step 3: Report Agent                    │
│ • Receives: Report request              │
│ • Context: {research: ..., analysis: ..}│
│ • LLM Call: Report writer               │
│ • Output: Executive report              │
└─────────────────────────────────────────┘
    ↓
Complete Results Displayed
```

---

## 📊 Agent Architecture

Each agent follows the same pattern:

### Structure
```go
type XxxAgent struct {
    *agent.BaseAgent      // Message handling, state management
    llmClient *llm.Client // API calls to OpenAI/Anthropic
    eventBus  *types.EventBus // Event publishing
    history   []llm.Message   // Conversation context (last 6)
}
```

### Lifecycle
```
Created → Registered → Started → Idle → Task Received → Processing → Task Complete → Idle → ...
```

### Event Publishing
Each agent publishes 3 events per task:
1. **EventTaskReceived** (📥) - Task arrived
2. **EventTaskStarted** (⚙️) - Processing began
3. **EventTaskCompleted** (✅) - Task finished (with results)

### LLM Integration
All agents use the same pattern:
1. Define system prompt (agent role and behavior)
2. Build user prompt (task + context)
3. Call `llmClient.Complete(system, user, history)`
4. Process AI response
5. Update conversation history
6. Return result

---

## 🎨 Customization

### To Add a New Agent Type:

1. **Create new file**: `pkg/agents/your_agent.go`

2. **Define struct**:
```go
type YourAgent struct {
    *agent.BaseAgent
    llmClient *llm.Client
    eventBus  *types.EventBus
    history   []llm.Message
}
```

3. **Implement constructor**:
```go
func NewYourAgent(id string, eventBus *types.EventBus) *YourAgent {
    ya := &YourAgent{
        BaseAgent: agent.NewBaseAgent(id),
        llmClient: llm.NewClient(),
        eventBus:  eventBus,
        history:   []llm.Message{},
    }
    ya.RegisterHandler(types.MessageTypeTask, ya.handleTask)
    return ya
}
```

4. **Implement handleTask** (see research_agent.go for template)

5. **Implement ProcessTask** with your custom prompts:
```go
func (ya *YourAgent) ProcessTask(task types.Task) types.Result {
    systemPrompt := "You are a [your specialty]..."
    userPrompt := fmt.Sprintf("Your task: %s", task.Description)
    response, err := ya.llmClient.Complete(systemPrompt, userPrompt, ya.history)
    // ... handle response
}
```

6. **Add to main.go**:
```go
yourAgent := agents.NewYourAgent("your-agent-1", s.GetEventBus())
s.AddAgent(yourAgent)
```

---

## 📈 Performance Characteristics

| Agent | Avg Response Time | Token Usage | Complexity |
|-------|------------------|-------------|------------|
| Research | 15-30 seconds | 1000-3000 | High |
| Analysis | 15-30 seconds | 800-2500 | Medium |
| Report | 15-30 seconds | 1000-3000 | Medium |

**Total Workflow Time**: ~45-90 seconds (sequential execution)

---

## 🔍 Troubleshooting

### Agent Not Responding
- Check if agent is started: `swarm.Start(ctx)`
- Verify agent registered: `swarm.AddAgent(agent)`
- Check API key is set: `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`

### Empty Results
- Check task routing: Task payload should have `agent_type` field
- Verify LLM client initialized: Check API key in environment
- Look for errors in console output

### Slow Performance
- Normal: LLM calls take 10-30 seconds each
- Check internet connection
- Verify API quotas not exceeded

---

## 📚 Additional Resources

- **AGENTS_DIAGRAM.md** - Visual architecture diagrams
- **CODE_DOCUMENTATION.md** (root) - Complete system documentation
- **research_agent.go** - Fully commented reference implementation
- **pkg/llm/client.go** - LLM API integration details
- **pkg/workflows/research_workflow.go** - Workflow orchestration

---

## 🎓 Learning Path

For understanding the agents:

1. **Start with**: `research_agent.go` - Extensively commented
2. **Then read**: `AGENTS_DIAGRAM.md` - Visual overview
3. **Understand**: How events flow through the system
4. **See in action**: Run `go run cmd/main.go` and select option 1
5. **Monitor**: Watch web dashboard at http://localhost:8080

---

*Part of Agent Swarm Go - AI-Powered Multi-Agent Research System*