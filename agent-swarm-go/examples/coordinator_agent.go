package examples

import (
	"fmt"
	"time"

	"agent-swarm-go/pkg/agent"
	"agent-swarm-go/pkg/types"
)

// CoordinatorAgent manages and delegates tasks to other agents
type CoordinatorAgent struct {
	*agent.BaseAgent
	taskQueue   []types.Task
	workerIDs   []string
	nextWorker  int
}

// NewCoordinatorAgent creates a new coordinator agent
func NewCoordinatorAgent(id string, workerIDs []string) *CoordinatorAgent {
	ca := &CoordinatorAgent{
		BaseAgent:  agent.NewBaseAgent(id),
		taskQueue:  make([]types.Task, 0),
		workerIDs:  workerIDs,
		nextWorker: 0,
	}

	// Register handlers
	ca.RegisterHandler(types.MessageTypeTask, ca.handleTask)
	ca.RegisterHandler(types.MessageTypeResult, ca.handleResult)

	return ca
}

// handleTask receives tasks and delegates them to workers
func (ca *CoordinatorAgent) handleTask(msg types.Message) error {
	task, ok := msg.Content.(types.Task)
	if !ok {
		return fmt.Errorf("invalid task format")
	}

	fmt.Printf("[%s] Coordinator %s received task: %s (priority: %d)\n",
		time.Now().Format("15:04:05"),
		ca.GetID(),
		task.Description,
		task.Priority)

	ca.taskQueue = append(ca.taskQueue, task)
	return ca.delegateNextTask()
}

// handleResult receives results from workers
func (ca *CoordinatorAgent) handleResult(msg types.Message) error {
	result, ok := msg.Content.(types.Result)
	if !ok {
		return fmt.Errorf("invalid result format")
	}

	fmt.Printf("[%s] Coordinator %s received result from %s: task %s, success: %v\n",
		time.Now().Format("15:04:05"),
		ca.GetID(),
		msg.From,
		result.TaskID,
		result.Success)

	return nil
}

// delegateNextTask assigns the next task to a worker using round-robin
func (ca *CoordinatorAgent) delegateNextTask() error {
	if len(ca.taskQueue) == 0 || len(ca.workerIDs) == 0 {
		return nil
	}

	task := ca.taskQueue[0]
	ca.taskQueue = ca.taskQueue[1:]

	workerID := ca.workerIDs[ca.nextWorker]
	ca.nextWorker = (ca.nextWorker + 1) % len(ca.workerIDs)

	fmt.Printf("[%s] Coordinator %s delegating task %s to worker %s\n",
		time.Now().Format("15:04:05"),
		ca.GetID(),
		task.ID,
		workerID)

	return nil
}