package workflows

import (
	"fmt"
	"time"

	"agent-swarm-go/pkg/swarm"
	"agent-swarm-go/pkg/types"
)

// ResearchWorkflow handles sequential research → analysis → report workflow
type ResearchWorkflow struct {
	swarm   *swarm.Swarm
	results map[string]types.Result
}

// NewResearchWorkflow creates a new research workflow handler
func NewResearchWorkflow(s *swarm.Swarm) *ResearchWorkflow {
	return &ResearchWorkflow{
		swarm:   s,
		results: make(map[string]types.Result),
	}
}

// Execute runs a complete research workflow with proper context passing
func (rw *ResearchWorkflow) Execute(topic string) (*WorkflowResult, error) {
	fmt.Printf("\n🔬 Starting Research Workflow for: %s\n", topic)
	fmt.Println("=" + string(make([]byte, 60)) + "=")

	workflowResult := &WorkflowResult{
		Topic:      topic,
		StartTime:  time.Now(),
		StepResults: make(map[string]string),
	}

	// Step 1: Research
	fmt.Println("\n📚 Step 1/3: Research Phase")
	researchTask := types.Task{
		ID:          fmt.Sprintf("research-%d", time.Now().Unix()),
		Description: fmt.Sprintf("Research the topic: %s. Provide comprehensive findings with key insights, trends, and supporting evidence.", topic),
		Payload:     map[string]interface{}{"type": "research", "topic": topic},
		Priority:    1,
		Context:     make(map[string]interface{}),
	}

	if err := rw.swarm.DistributeTask(researchTask); err != nil {
		return nil, fmt.Errorf("failed to distribute research task: %w", err)
	}

	// Wait for research to complete
	researchResult := rw.waitForTaskCompletion(researchTask.ID, 60*time.Second)
	if !researchResult.Success {
		return nil, fmt.Errorf("research failed: %v", researchResult.Data)
	}

	workflowResult.StepResults["research"] = fmt.Sprintf("%v", researchResult.Data)
	fmt.Println("✅ Research completed")

	// Step 2: Analysis
	fmt.Println("\n📊 Step 2/3: Analysis Phase")
	analysisTask := types.Task{
		ID:          fmt.Sprintf("analyze-%d", time.Now().Unix()),
		Description: fmt.Sprintf("Analyze the research findings on %s. Identify patterns, correlations, and generate actionable insights.", topic),
		Payload:     map[string]interface{}{"type": "analysis", "topic": topic},
		Priority:    2,
		Context: map[string]interface{}{
			"research_findings": researchResult.Data,
		},
		Dependencies: []string{researchTask.ID},
	}

	if err := rw.swarm.DistributeTask(analysisTask); err != nil {
		return nil, fmt.Errorf("failed to distribute analysis task: %w", err)
	}

	analysisResult := rw.waitForTaskCompletion(analysisTask.ID, 60*time.Second)
	if !analysisResult.Success {
		return nil, fmt.Errorf("analysis failed: %v", analysisResult.Data)
	}

	workflowResult.StepResults["analysis"] = fmt.Sprintf("%v", analysisResult.Data)
	fmt.Println("✅ Analysis completed")

	// Step 3: Report Generation
	fmt.Println("\n📝 Step 3/3: Report Generation Phase")
	reportTask := types.Task{
		ID:          fmt.Sprintf("report-%d", time.Now().Unix()),
		Description: fmt.Sprintf("Generate a comprehensive executive report on %s based on research and analysis.", topic),
		Payload:     map[string]interface{}{"type": "report", "topic": topic},
		Priority:    3,
		Context: map[string]interface{}{
			"research_findings": researchResult.Data,
			"analysis_insights": analysisResult.Data,
		},
		Dependencies: []string{researchTask.ID, analysisTask.ID},
	}

	if err := rw.swarm.DistributeTask(reportTask); err != nil {
		return nil, fmt.Errorf("failed to distribute report task: %w", err)
	}

	reportResult := rw.waitForTaskCompletion(reportTask.ID, 60*time.Second)
	if !reportResult.Success {
		return nil, fmt.Errorf("report generation failed: %v", reportResult.Data)
	}

	workflowResult.StepResults["report"] = fmt.Sprintf("%v", reportResult.Data)
	workflowResult.FinalReport = fmt.Sprintf("%v", reportResult.Data)
	workflowResult.EndTime = time.Now()
	workflowResult.Duration = workflowResult.EndTime.Sub(workflowResult.StartTime)

	fmt.Println("✅ Report generated")
	fmt.Printf("\n🎉 Workflow completed in %v\n", workflowResult.Duration)

	return workflowResult, nil
}

// waitForTaskCompletion waits for a task to complete and returns its result
func (rw *ResearchWorkflow) waitForTaskCompletion(taskID string, timeout time.Duration) types.Result {
	// Subscribe to events to monitor task completion
	eventChan := rw.swarm.GetEventBus().Subscribe()

	deadline := time.Now().Add(timeout)

	for {
		if time.Now().After(deadline) {
			return types.Result{
				TaskID:  taskID,
				Success: false,
				Data:    "Task timeout",
			}
		}

		select {
		case event := <-eventChan:
			if event.TaskID == taskID {
				if event.Type == types.EventTaskCompleted {
					if result, ok := event.Data.(types.Result); ok {
						return result
					}
				} else if event.Type == types.EventTaskFailed {
					return types.Result{
						TaskID:  taskID,
						Success: false,
						Data:    event.Message,
					}
				}
			}
		case <-time.After(100 * time.Millisecond):
			// Continue checking
		}
	}
}

// WorkflowResult contains the complete results of a research workflow
type WorkflowResult struct {
	Topic       string
	StartTime   time.Time
	EndTime     time.Time
	Duration    time.Duration
	StepResults map[string]string
	FinalReport string
}

// Display prints the workflow results in a readable format
func (wr *WorkflowResult) Display() {
	fmt.Println("\n" + string(make([]byte, 70)))
	fmt.Println("📋 WORKFLOW RESULTS")
	fmt.Println(string(make([]byte, 70)))
	fmt.Printf("\n📌 Topic: %s\n", wr.Topic)
	fmt.Printf("⏱️  Duration: %v\n\n", wr.Duration)

	fmt.Println("=" + string(make([]byte, 68)) + "=")
	fmt.Println("📚 RESEARCH FINDINGS")
	fmt.Println("=" + string(make([]byte, 68)) + "=")
	wr.printWrapped(wr.StepResults["research"], 70)

	fmt.Println("\n" + "=" + string(make([]byte, 68)) + "=")
	fmt.Println("📊 ANALYSIS INSIGHTS")
	fmt.Println("=" + string(make([]byte, 68)) + "=")
	wr.printWrapped(wr.StepResults["analysis"], 70)

	fmt.Println("\n" + "=" + string(make([]byte, 68)) + "=")
	fmt.Println("📝 FINAL REPORT")
	fmt.Println("=" + string(make([]byte, 68)) + "=")
	wr.printWrapped(wr.FinalReport, 70)

	fmt.Println("\n" + string(make([]byte, 70)))
}

func (wr *WorkflowResult) printWrapped(text string, width int) {
	// Simple word wrap for better readability
	words := []rune(text)
	if len(words) == 0 {
		return
	}

	printed := 0
	for i, char := range words {
		fmt.Print(string(char))
		printed++
		if char == '\n' {
			printed = 0
		} else if printed >= width && (char == ' ' || i == len(words)-1) {
			fmt.Println()
			printed = 0
		}
	}
	fmt.Println()
}