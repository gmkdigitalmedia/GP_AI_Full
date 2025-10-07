/*
Package agents provides specialized AI agent implementations.

ResearchAgent is an AI-powered agent that specializes in comprehensive research.
It uses Large Language Models (LLM) to:
  - Break down complex research topics into key questions
  - Gather and synthesize relevant information
  - Identify patterns, trends, and insights
  - Present findings in a structured, evidence-based format

The agent maintains conversation history to provide contextual continuity
across multiple research tasks.
*/
package agents

import (
	"fmt"
	"time"

	"agent-swarm-go/pkg/agent"
	"agent-swarm-go/pkg/llm"
	"agent-swarm-go/pkg/types"
)

// ResearchAgent is an AI-powered specialist that conducts comprehensive research on any topic.
//
// Architecture:
//   - Inherits base agent functionality (message handling, state management)
//   - Uses LLM client to interact with OpenAI or Anthropic APIs
//   - Publishes events to event bus for real-time monitoring
//   - Maintains conversation history for contextual awareness
//
// Workflow:
//   1. Receives research task via message
//   2. Publishes "task received" event
//   3. Publishes "task started" event
//   4. Calls LLM with research-specific prompts
//   5. Processes and stores the AI response
//   6. Publishes "task completed" event with results
//
// Example Usage:
//   researcher := agents.NewResearchAgent("researcher-1", eventBus)
//   swarm.AddAgent(researcher)
//   // Agent will receive and process research tasks automatically
type ResearchAgent struct {
	*agent.BaseAgent            // Embedded base agent provides core functionality
	llmClient *llm.Client        // Client for calling OpenAI/Anthropic APIs
	eventBus  *types.EventBus    // Event publisher for real-time monitoring
	history   []llm.Message      // Conversation history (last 6 messages max)
}

// NewResearchAgent creates and initializes a new research agent.
//
// The agent is configured with:
//   - Unique identifier for tracking and routing
//   - Event bus connection for publishing status updates
//   - LLM client (auto-configured for OpenAI or Anthropic)
//   - Empty conversation history (will build up over time)
//   - Registered handler for task messages
//
// Parameters:
//   - id: Unique identifier (e.g., "researcher-1", "research-agent-main")
//   - eventBus: Event bus for publishing real-time updates
//
// Returns:
//   - Fully configured ResearchAgent ready to process tasks
//
// Example:
//   eventBus := types.NewEventBus()
//   researcher := NewResearchAgent("researcher-1", eventBus)
func NewResearchAgent(id string, eventBus *types.EventBus) *ResearchAgent {
	// Create agent with embedded base agent
	ra := &ResearchAgent{
		BaseAgent: agent.NewBaseAgent(id), // Provides message queue and state management
		llmClient: llm.NewClient(),         // Auto-detects OPENAI_API_KEY or ANTHROPIC_API_KEY
		eventBus:  eventBus,                // For publishing events to web dashboard and monitors
		history:   []llm.Message{},         // Empty history, will populate during conversations
	}

	// Register this agent's task handler to process incoming task messages
	// When a message of type "task" arrives, handleTask() will be called
	ra.RegisterHandler(types.MessageTypeTask, ra.handleTask)

	return ra
}

// handleTask is the message handler that processes incoming research tasks.
//
// This function is called automatically when the agent receives a task message.
// It orchestrates the complete research workflow:
//
// Workflow Steps:
//   1. Validates the message contains a valid Task
//   2. Publishes EventTaskReceived (shows in web dashboard)
//   3. Logs task receipt to console
//   4. Publishes EventTaskStarted (updates agent status to "processing")
//   5. Calls ProcessTask() to perform the actual research
//   6. Publishes EventTaskCompleted or EventTaskFailed with results
//   7. Logs completion to console
//
// Event Publishing:
//   - EventTaskReceived: "📥 Received research task: [description]"
//   - EventTaskStarted: "⚙️  Researching: [description]"
//   - EventTaskCompleted: "✅ Research complete: [task-id]" (with full results)
//   - EventTaskFailed: "❌ Research failed: [task-id]" (with error)
//
// Parameters:
//   - msg: Message containing the task (msg.Content must be types.Task)
//
// Returns:
//   - error if message format is invalid, nil otherwise
//
// Note: This function doesn't return the task result directly.
// Results are published via events and can be retrieved by monitoring the event bus.
func (ra *ResearchAgent) handleTask(msg types.Message) error {
	// Extract the task from the message content
	// Type assertion ensures we have a valid Task structure
	task, ok := msg.Content.(types.Task)
	if !ok {
		return fmt.Errorf("invalid task format")
	}

	// STEP 1: Publish "task received" event
	// This appears in the web dashboard event stream and updates statistics
	if ra.eventBus != nil {
		ra.eventBus.Publish(types.Event{
			Type:      types.EventTaskReceived,
			Timestamp: time.Now(),
			AgentID:   ra.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("📥 Received research task: %s", task.Description),
		})
	}

	// STEP 2: Log to console for CLI visibility
	// Format: [15:04:05] 📥 Researcher researcher-1 received task: Research quantum computing...
	fmt.Printf("[%s] 📥 Researcher %s received task: %s\n",
		time.Now().Format("15:04:05"), ra.GetID(), task.Description)

	// STEP 3: Publish "task started" event
	// This changes the agent's status to "processing" in the web dashboard
	if ra.eventBus != nil {
		ra.eventBus.Publish(types.Event{
			Type:      types.EventTaskStarted,
			Timestamp: time.Now(),
			AgentID:   ra.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("⚙️  Researching: %s", task.Description),
		})
	}

	// STEP 4: Perform the actual research
	// This calls the LLM API and can take 10-30 seconds
	result := ra.ProcessTask(task)

	// STEP 5: Determine event type based on success/failure
	eventType := types.EventTaskCompleted
	if !result.Success {
		eventType = types.EventTaskFailed
	}

	// STEP 6: Publish completion/failure event with full results
	// The result.Data contains the complete AI-generated research report
	// This is picked up by the web dashboard and displayed in the results panel
	if ra.eventBus != nil {
		ra.eventBus.Publish(types.Event{
			Type:      eventType,
			Timestamp: time.Now(),
			AgentID:   ra.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("✅ Research complete: %s", task.ID),
			Data:      result, // Contains full research report
		})
	}

	// STEP 7: Log completion to console
	statusIcon := "✅"
	if !result.Success {
		statusIcon = "❌"
	}
	fmt.Printf("[%s] %s Researcher %s completed: %s\n",
		time.Now().Format("15:04:05"), statusIcon, ra.GetID(), task.ID)

	return nil
}

// ProcessTask performs the actual research using the LLM API.
//
// This is the core research logic that:
//   1. Constructs a research-specific system prompt (defines agent behavior)
//   2. Creates a detailed user prompt with task requirements
//   3. Calls the LLM API (OpenAI GPT-4 or Anthropic Claude)
//   4. Processes the AI response
//   5. Updates conversation history for context in future tasks
//
// System Prompt:
//   Instructs the LLM to act as a research specialist with specific methodology:
//   - Break down topics into key questions
//   - Gather and synthesize information
//   - Identify patterns and insights
//   - Present findings with evidence
//
// User Prompt Template:
//   Research Task: [task.Description]
//
//   Please provide a thorough research report including:
//   - Executive summary
//   - Key findings (3-5 main points)
//   - Supporting details and evidence
//   - Trends and patterns identified
//   - Recommendations for next steps
//
//   Context from previous tasks: [task.Context]
//
// Context Handling:
//   - First task in workflow: task.Context is empty
//   - Subsequent tasks: task.Context contains results from previous agents
//   - This allows the researcher to build on prior work
//
// Conversation History:
//   - Maintains last 6 messages (3 exchanges) for context
//   - Helps LLM understand the conversation flow
//   - Prevents token limit issues by capping history size
//
// Parameters:
//   - task: Task containing description, context, and metadata
//
// Returns:
//   - Result with Success=true and Data=research report (string), or
//   - Result with Success=false and Data=error message
//
// Example Result.Data:
//   # Research Findings: Quantum Computing
//
//   ## Executive Summary
//   Quantum computing represents a paradigm shift...
//
//   ## Key Findings
//   1. Quantum supremacy achieved in 2019...
//   2. Error correction remains primary challenge...
//   ...
func (ra *ResearchAgent) ProcessTask(task types.Task) types.Result {
	// Define the system prompt that shapes the LLM's behavior
	// This tells the AI to act as a research specialist with specific methodology
	systemPrompt := `You are a research specialist agent. Your role is to:
1. Break down the research topic into key questions
2. Gather and synthesize relevant information
3. Identify patterns and insights
4. Present findings clearly with evidence

Provide comprehensive, well-structured research output.`

	// Create the user prompt with task details and any context from previous tasks
	// The context might include results from earlier workflow steps
	userPrompt := fmt.Sprintf(`Research Task: %s

Please provide a thorough research report including:
- Executive summary
- Key findings (3-5 main points)
- Supporting details and evidence
- Trends and patterns identified
- Recommendations for next steps

Context from previous tasks: %v`, task.Description, task.Context)

	// Call the LLM API with the prompts and conversation history
	// This makes an HTTP request to OpenAI or Anthropic
	// Typical response time: 10-30 seconds for comprehensive research
	response, err := ra.llmClient.Complete(systemPrompt, userPrompt, ra.history)
	if err != nil {
		// LLM API call failed (network error, API error, etc.)
		return types.Result{
			TaskID:  task.ID,
			Success: false,
			Data:    fmt.Sprintf("Research failed: %v", err),
		}
	}

	// Add this exchange to conversation history for future context
	// This allows the LLM to reference previous discussions
	ra.history = append(ra.history,
		llm.Message{Role: "user", Content: userPrompt},
		llm.Message{Role: "assistant", Content: response},
	)

	// Keep history manageable to avoid token limits
	// We keep last 6 messages (3 exchanges of user + assistant)
	// This provides enough context without hitting API limits
	if len(ra.history) > 6 {
		ra.history = ra.history[len(ra.history)-6:]
	}

	// Return successful result with the AI-generated research report
	return types.Result{
		TaskID:  task.ID,
		Success: true,
		Data:    response, // Full research report from LLM
	}
}

// GetSpecialty returns the agent's area of expertise.
//
// This is used by the swarm coordinator to route tasks to the appropriate agent.
// Tasks with Payload["agent_type"] == "research" will be routed to this agent.
//
// Returns:
//   - "research" indicating this agent specializes in research tasks
func (ra *ResearchAgent) GetSpecialty() string {
	return "research"
}
