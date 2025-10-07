package agents

import (
	"fmt"
	"time"

	"agent-swarm-go/pkg/agent"
	"agent-swarm-go/pkg/llm"
	"agent-swarm-go/pkg/types"
)

// ReportAgent specializes in creating comprehensive reports
type ReportAgent struct {
	*agent.BaseAgent
	llmClient *llm.Client
	eventBus  *types.EventBus
	history   []llm.Message
}

// NewReportAgent creates a new report generation agent
func NewReportAgent(id string, eventBus *types.EventBus) *ReportAgent {
	ra := &ReportAgent{
		BaseAgent: agent.NewBaseAgent(id),
		llmClient: llm.NewClient(),
		eventBus:  eventBus,
		history:   []llm.Message{},
	}

	ra.RegisterHandler(types.MessageTypeTask, ra.handleTask)
	return ra
}

func (ra *ReportAgent) handleTask(msg types.Message) error {
	task, ok := msg.Content.(types.Task)
	if !ok {
		return fmt.Errorf("invalid task format")
	}

	if ra.eventBus != nil {
		ra.eventBus.Publish(types.Event{
			Type:      types.EventTaskReceived,
			Timestamp: time.Now(),
			AgentID:   ra.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("📥 Received report task: %s", task.Description),
		})
	}

	fmt.Printf("[%s] 📥 Reporter %s received task: %s\n",
		time.Now().Format("15:04:05"), ra.GetID(), task.Description)

	if ra.eventBus != nil {
		ra.eventBus.Publish(types.Event{
			Type:      types.EventTaskStarted,
			Timestamp: time.Now(),
			AgentID:   ra.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("⚙️  Generating report: %s", task.Description),
		})
	}

	result := ra.ProcessTask(task)

	eventType := types.EventTaskCompleted
	if !result.Success {
		eventType = types.EventTaskFailed
	}
	if ra.eventBus != nil {
		ra.eventBus.Publish(types.Event{
			Type:      eventType,
			Timestamp: time.Now(),
			AgentID:   ra.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("✅ Report complete: %s", task.ID),
			Data:      result,
		})
	}

	statusIcon := "✅"
	if !result.Success {
		statusIcon = "❌"
	}
	fmt.Printf("[%s] %s Reporter %s completed: %s\n",
		time.Now().Format("15:04:05"), statusIcon, ra.GetID(), task.ID)

	return nil
}

// ProcessTask generates a report using LLM
func (ra *ReportAgent) ProcessTask(task types.Task) types.Result {
	systemPrompt := `You are a professional report writer agent. Your role is to:
1. Synthesize information from research and analysis
2. Create clear, well-structured reports
3. Present findings in an executive-friendly format
4. Provide actionable recommendations

Create comprehensive, professional reports.`

	contextStr := ""
	if task.Context != nil {
		contextStr = fmt.Sprintf("%v", task.Context)
	}

	userPrompt := fmt.Sprintf(`Report Generation Task: %s

Research and Analysis Results:
%s

Please create a comprehensive report including:
- Executive Summary (2-3 paragraphs)
- Key Findings (clearly numbered/bulleted)
- Detailed Analysis
- Recommendations (actionable next steps)
- Conclusion

Format the report professionally with clear sections and markdown formatting.`, task.Description, contextStr)

	response, err := ra.llmClient.Complete(systemPrompt, userPrompt, ra.history)
	if err != nil {
		return types.Result{
			TaskID:  task.ID,
			Success: false,
			Data:    fmt.Sprintf("Report generation failed: %v", err),
		}
	}

	ra.history = append(ra.history,
		llm.Message{Role: "user", Content: userPrompt},
		llm.Message{Role: "assistant", Content: response},
	)

	if len(ra.history) > 6 {
		ra.history = ra.history[len(ra.history)-6:]
	}

	return types.Result{
		TaskID:  task.ID,
		Success: true,
		Data:    response,
	}
}

// GetSpecialty returns the agent's specialty
func (ra *ReportAgent) GetSpecialty() string {
	return "reporting"
}