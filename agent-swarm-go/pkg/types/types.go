package types

import "context"

// Message represents communication between agents
type Message struct {
	From    string
	To      string
	Content interface{}
	Type    MessageType
}

// MessageType defines the type of message
type MessageType string

const (
	MessageTypeTask     MessageType = "task"
	MessageTypeResult   MessageType = "result"
	MessageTypeQuery    MessageType = "query"
	MessageTypeBroadcast MessageType = "broadcast"
)

// Task represents work to be done by an agent
type Task struct {
	ID           string
	Description  string
	Payload      interface{}
	Priority     int
	Context      map[string]interface{} // Results from previous tasks
	Dependencies []string               // IDs of tasks that must complete first
}

// Result represents the output of an agent's work
type Result struct {
	TaskID  string
	Success bool
	Data    interface{}
	Error   error
}

// AgentState represents the current state of an agent
type AgentState string

const (
	StateIdle       AgentState = "idle"
	StateProcessing AgentState = "processing"
	StateStopped    AgentState = "stopped"
)

// Agent defines the interface that all agents must implement
type Agent interface {
	// GetID returns the unique identifier for this agent
	GetID() string

	// Start begins the agent's execution loop
	Start(ctx context.Context) error

	// Stop gracefully shuts down the agent
	Stop() error

	// SendMessage sends a message to another agent
	SendMessage(msg Message) error

	// ReceiveMessage receives a message (non-blocking)
	ReceiveMessage() (*Message, bool)

	// ProcessTask processes a task and returns a result
	ProcessTask(task Task) Result

	// GetState returns the current state of the agent
	GetState() AgentState
}