package agents

import (
	"fmt"
	"time"

	"agent-swarm-go/pkg/agent"
	"agent-swarm-go/pkg/llm"
	"agent-swarm-go/pkg/types"
)

// AnalysisAgent specializes in analyzing data and findings
type AnalysisAgent struct {
	*agent.BaseAgent
	llmClient *llm.Client
	eventBus  *types.EventBus
	history   []llm.Message
}

// NewAnalysisAgent creates a new analysis agent
func NewAnalysisAgent(id string, eventBus *types.EventBus) *AnalysisAgent {
	aa := &AnalysisAgent{
		BaseAgent: agent.NewBaseAgent(id),
		llmClient: llm.NewClient(),
		eventBus:  eventBus,
		history:   []llm.Message{},
	}

	aa.RegisterHandler(types.MessageTypeTask, aa.handleTask)
	return aa
}

func (aa *AnalysisAgent) handleTask(msg types.Message) error {
	task, ok := msg.Content.(types.Task)
	if !ok {
		return fmt.Errorf("invalid task format")
	}

	if aa.eventBus != nil {
		aa.eventBus.Publish(types.Event{
			Type:      types.EventTaskReceived,
			Timestamp: time.Now(),
			AgentID:   aa.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("📥 Received analysis task: %s", task.Description),
		})
	}

	fmt.Printf("[%s] 📥 Analyzer %s received task: %s\n",
		time.Now().Format("15:04:05"), aa.GetID(), task.Description)

	if aa.eventBus != nil {
		aa.eventBus.Publish(types.Event{
			Type:      types.EventTaskStarted,
			Timestamp: time.Now(),
			AgentID:   aa.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("⚙️  Analyzing: %s", task.Description),
		})
	}

	result := aa.ProcessTask(task)

	eventType := types.EventTaskCompleted
	if !result.Success {
		eventType = types.EventTaskFailed
	}
	if aa.eventBus != nil {
		aa.eventBus.Publish(types.Event{
			Type:      eventType,
			Timestamp: time.Now(),
			AgentID:   aa.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("✅ Analysis complete: %s", task.ID),
			Data:      result,
		})
	}

	statusIcon := "✅"
	if !result.Success {
		statusIcon = "❌"
	}
	fmt.Printf("[%s] %s Analyzer %s completed: %s\n",
		time.Now().Format("15:04:05"), statusIcon, aa.GetID(), task.ID)

	return nil
}

// ProcessTask performs analysis using LLM
func (aa *AnalysisAgent) ProcessTask(task types.Task) types.Result {
	systemPrompt := `You are a data analysis specialist agent. Your role is to:
1. Assess data quality and completeness
2. Identify patterns, trends, and anomalies
3. Apply analytical techniques
4. Generate actionable insights

Provide thorough, evidence-based analysis.`

	contextStr := ""
	if task.Context != nil {
		contextStr = fmt.Sprintf("%v", task.Context)
	}

	userPrompt := fmt.Sprintf(`Analysis Task: %s

Data/Research to analyze:
%s

Please provide a comprehensive analysis including:
- Data quality assessment
- Key patterns and trends identified
- Statistical insights
- Correlations and relationships
- Actionable recommendations
- Confidence levels in findings`, task.Description, contextStr)

	response, err := aa.llmClient.Complete(systemPrompt, userPrompt, aa.history)
	if err != nil {
		return types.Result{
			TaskID:  task.ID,
			Success: false,
			Data:    fmt.Sprintf("Analysis failed: %v", err),
		}
	}

	aa.history = append(aa.history,
		llm.Message{Role: "user", Content: userPrompt},
		llm.Message{Role: "assistant", Content: response},
	)

	if len(aa.history) > 6 {
		aa.history = aa.history[len(aa.history)-6:]
	}

	return types.Result{
		TaskID:  task.ID,
		Success: true,
		Data:    response,
	}
}

// GetSpecialty returns the agent's specialty
func (aa *AnalysisAgent) GetSpecialty() string {
	return "analysis"
}