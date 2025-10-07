package scenarios

import (
	"fmt"
	"time"

	"agent-swarm-go/pkg/swarm"
	"agent-swarm-go/pkg/types"
)

// Scenario represents a pre-configured workflow scenario
type Scenario struct {
	Name        string
	Description string
	Tasks       []types.Task
}

// ResearchAnalysisScenario creates a research and analysis workflow
func ResearchAnalysisScenario(topic string) *Scenario {
	return &Scenario{
		Name:        "Research & Analysis Workflow",
		Description: fmt.Sprintf("Complete research and analysis pipeline for: %s", topic),
		Tasks: []types.Task{
			{
				ID:          "research-001",
				Description: fmt.Sprintf("Research the topic: %s. Provide comprehensive findings with key insights, trends, and supporting evidence.", topic),
				Priority:    1,
				Payload:     map[string]interface{}{"type": "research", "topic": topic, "agent_type": "researcher"},
			},
			{
				ID:          "analyze-001",
				Description: fmt.Sprintf("Analyze the research findings on %s. Identify patterns, correlations, and generate actionable insights.", topic),
				Priority:    2,
				Payload:     map[string]interface{}{"type": "analysis", "topic": topic, "agent_type": "analyzer"},
				Dependencies: []string{"research-001"},
			},
			{
				ID:          "report-001",
				Description: fmt.Sprintf("Generate a comprehensive executive report on %s based on research and analysis.", topic),
				Priority:    3,
				Payload:     map[string]interface{}{"type": "report", "topic": topic, "agent_type": "reporter"},
				Dependencies: []string{"research-001", "analyze-001"},
			},
		},
	}
}

// ParallelProcessingScenario creates multiple tasks for parallel processing
func ParallelProcessingScenario(count int) *Scenario {
	tasks := make([]types.Task, count)
	for i := 0; i < count; i++ {
		tasks[i] = types.Task{
			ID:          fmt.Sprintf("parallel-%03d", i+1),
			Description: fmt.Sprintf("Parallel task #%d: Process data batch", i+1),
			Priority:    1,
			Payload:     map[string]interface{}{"batch": i + 1, "timestamp": time.Now()},
		}
	}

	return &Scenario{
		Name:        "Parallel Task Processing",
		Description: fmt.Sprintf("Process %d tasks in parallel across available workers", count),
		Tasks:       tasks,
	}
}

// StressTestScenario creates a large number of tasks for stress testing
func StressTestScenario(taskCount int) *Scenario {
	tasks := make([]types.Task, taskCount)
	for i := 0; i < taskCount; i++ {
		priority := (i % 3) + 1
		tasks[i] = types.Task{
			ID:          fmt.Sprintf("stress-%04d", i+1),
			Description: fmt.Sprintf("Stress test task #%d", i+1),
			Priority:    priority,
			Payload:     map[string]interface{}{"index": i, "priority": priority},
		}
	}

	return &Scenario{
		Name:        "Stress Test",
		Description: fmt.Sprintf("Process %d tasks to test swarm capacity", taskCount),
		Tasks:       tasks,
	}
}

// CustomScenario creates a custom scenario from user input
func CustomScenario(name, description string, tasks []types.Task) *Scenario {
	return &Scenario{
		Name:        name,
		Description: description,
		Tasks:       tasks,
	}
}

// ExecuteScenario runs a scenario through the swarm
func ExecuteScenario(s *swarm.Swarm, scenario *Scenario, progressCallback func(int, int)) error {
	fmt.Printf("\n🚀 Executing Scenario: %s\n", scenario.Name)
	fmt.Printf("   %s\n", scenario.Description)
	fmt.Printf("   Total tasks: %d\n\n", len(scenario.Tasks))

	completed := 0
	total := len(scenario.Tasks)

	for i, task := range scenario.Tasks {
		fmt.Printf("[%s] Distributing task: %s\n",
			time.Now().Format("15:04:05"),
			task.Description)

		if err := s.DistributeTask(task); err != nil {
			return fmt.Errorf("failed to distribute task %s: %w", task.ID, err)
		}

		completed++
		if progressCallback != nil {
			progressCallback(completed, total)
		}

		// Small delay between task distributions
		time.Sleep(200 * time.Millisecond)

		// Show progress every 5 tasks
		if (i+1)%5 == 0 {
			fmt.Printf("\n--- Progress: %d/%d tasks distributed ---\n\n", i+1, total)
		}
	}

	fmt.Printf("\n✓ All %d tasks distributed successfully!\n", total)
	return nil
}

// GetScenarioTemplate returns a pre-defined scenario by name
func GetScenarioTemplate(name string, params map[string]interface{}) *Scenario {
	switch name {
	case "research":
		topic := "artificial intelligence"
		if t, ok := params["topic"].(string); ok {
			topic = t
		}
		return ResearchAnalysisScenario(topic)

	case "parallel":
		count := 10
		if c, ok := params["count"].(int); ok {
			count = c
		}
		return ParallelProcessingScenario(count)

	case "stress":
		count := 50
		if c, ok := params["count"].(int); ok {
			count = c
		}
		return StressTestScenario(count)

	default:
		return &Scenario{
			Name:        "Default Scenario",
			Description: "Simple task processing",
			Tasks: []types.Task{
				{ID: "default-001", Description: "Default task", Priority: 1},
			},
		}
	}
}