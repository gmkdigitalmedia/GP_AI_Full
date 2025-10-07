package types

import "time"

// EventType defines types of events that occur in the swarm
type EventType string

const (
	EventTaskReceived  EventType = "task_received"
	EventTaskStarted   EventType = "task_started"
	EventTaskCompleted EventType = "task_completed"
	EventTaskFailed    EventType = "task_failed"
	EventAgentIdle     EventType = "agent_idle"
	EventAgentBusy     EventType = "agent_busy"
	EventMessage       EventType = "message"
	EventBroadcast     EventType = "broadcast"
)

// Event represents something that happened in the swarm
type Event struct {
	Type      EventType   `json:"type"`
	Timestamp time.Time   `json:"timestamp"`
	AgentID   string      `json:"agent_id"`
	TaskID    string      `json:"task_id,omitempty"`
	Message   string      `json:"message"`
	Data      interface{} `json:"data,omitempty"`
}

// EventBus manages event distribution
type EventBus struct {
	subscribers []chan Event
}

// NewEventBus creates a new event bus
func NewEventBus() *EventBus {
	return &EventBus{
		subscribers: make([]chan Event, 0),
	}
}

// Subscribe creates a new event subscription
func (eb *EventBus) Subscribe() chan Event {
	ch := make(chan Event, 100)
	eb.subscribers = append(eb.subscribers, ch)
	return ch
}

// Publish sends an event to all subscribers
func (eb *EventBus) Publish(event Event) {
	for _, ch := range eb.subscribers {
		select {
		case ch <- event:
		default:
			// Drop event if channel is full
		}
	}
}

// Close closes all subscriber channels
func (eb *EventBus) Close() {
	for _, ch := range eb.subscribers {
		close(ch)
	}
}