package examples

import (
	"fmt"
	"math/rand"
	"time"

	"agent-swarm-go/pkg/agent"
	"agent-swarm-go/pkg/types"
)

// WorkerAgent is a specialized agent that processes work tasks
type WorkerAgent struct {
	*agent.BaseAgent
	specialty string
	eventBus  *types.EventBus
}

// NewWorkerAgent creates a new worker agent with a specialty
func NewWorkerAgent(id, specialty string, eventBus *types.EventBus) *WorkerAgent {
	wa := &WorkerAgent{
		BaseAgent: agent.NewBaseAgent(id),
		specialty: specialty,
		eventBus:  eventBus,
	}

	// Register custom task handler
	wa.RegisterHandler(types.MessageTypeTask, wa.handleTask)

	return wa
}

// SetEventBus sets the event bus for the worker (for backward compatibility)
func (wa *WorkerAgent) SetEventBus(eventBus *types.EventBus) {
	wa.eventBus = eventBus
}

// handleTask processes incoming tasks
func (wa *WorkerAgent) handleTask(msg types.Message) error {
	task, ok := msg.Content.(types.Task)
	if !ok {
		return fmt.Errorf("invalid task format")
	}

	// Publish task received event
	if wa.eventBus != nil {
		wa.eventBus.Publish(types.Event{
			Type:      types.EventTaskReceived,
			Timestamp: time.Now(),
			AgentID:   wa.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("Received task: %s", task.Description),
			Data:      map[string]interface{}{"specialty": wa.specialty},
		})
	}

	fmt.Printf("[%s] 📥 Worker %s (%s) received task: %s\n",
		time.Now().Format("15:04:05"),
		wa.GetID(),
		wa.specialty,
		task.Description)

	// Publish task started event
	if wa.eventBus != nil {
		wa.eventBus.Publish(types.Event{
			Type:      types.EventTaskStarted,
			Timestamp: time.Now(),
			AgentID:   wa.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("Processing task: %s", task.Description),
		})
	}

	result := wa.ProcessTask(task)

	// Publish task completed event
	if wa.eventBus != nil {
		eventType := types.EventTaskCompleted
		if !result.Success {
			eventType = types.EventTaskFailed
		}
		wa.eventBus.Publish(types.Event{
			Type:      eventType,
			Timestamp: time.Now(),
			AgentID:   wa.GetID(),
			TaskID:    task.ID,
			Message:   fmt.Sprintf("Completed task: %s", task.ID),
			Data:      result,
		})
	}

	statusIcon := "✅"
	if !result.Success {
		statusIcon = "❌"
	}
	fmt.Printf("[%s] %s Worker %s (%s) completed task: %s\n",
		time.Now().Format("15:04:05"),
		statusIcon,
		wa.GetID(),
		wa.specialty,
		task.ID)

	return nil
}

// ProcessTask overrides the base implementation with specialty-specific logic
func (wa *WorkerAgent) ProcessTask(task types.Task) types.Result {
	// Simulate processing time
	processingTime := time.Duration(rand.Intn(1000)+500) * time.Millisecond
	time.Sleep(processingTime)

	return types.Result{
		TaskID:  task.ID,
		Success: true,
		Data: fmt.Sprintf("Task %s processed by %s specialist in %v",
			task.ID,
			wa.specialty,
			processingTime),
	}
}