package swarm

import (
	"context"
	"fmt"
	"sync"

	"agent-swarm-go/pkg/types"
)

// Swarm manages a collection of agents
type Swarm struct {
	agents   map[string]types.Agent
	mu       sync.RWMutex
	ctx      context.Context
	cancel   context.CancelFunc
	eventBus *types.EventBus
}

// NewSwarm creates a new agent swarm
func NewSwarm() *Swarm {
	return &Swarm{
		agents:   make(map[string]types.Agent),
		eventBus: types.NewEventBus(),
	}
}

// GetEventBus returns the event bus for subscribing to swarm events
func (s *Swarm) GetEventBus() *types.EventBus {
	return s.eventBus
}

// AddAgent adds an agent to the swarm
func (s *Swarm) AddAgent(agent types.Agent) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	id := agent.GetID()
	if _, exists := s.agents[id]; exists {
		return fmt.Errorf("agent with ID %s already exists", id)
	}

	s.agents[id] = agent
	return nil
}

// RemoveAgent removes an agent from the swarm
func (s *Swarm) RemoveAgent(id string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	agent, exists := s.agents[id]
	if !exists {
		return fmt.Errorf("agent with ID %s not found", id)
	}

	if err := agent.Stop(); err != nil {
		return fmt.Errorf("error stopping agent %s: %w", id, err)
	}

	delete(s.agents, id)
	return nil
}

// GetAgent retrieves an agent by ID
func (s *Swarm) GetAgent(id string) (types.Agent, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	agent, exists := s.agents[id]
	if !exists {
		return nil, fmt.Errorf("agent with ID %s not found", id)
	}

	return agent, nil
}

// ListAgents returns all agent IDs
func (s *Swarm) ListAgents() []string {
	s.mu.RLock()
	defer s.mu.RUnlock()

	ids := make([]string, 0, len(s.agents))
	for id := range s.agents {
		ids = append(ids, id)
	}
	return ids
}

// Start starts all agents in the swarm
func (s *Swarm) Start(ctx context.Context) error {
	s.mu.Lock()
	s.ctx, s.cancel = context.WithCancel(ctx)
	s.mu.Unlock()

	s.mu.RLock()
	defer s.mu.RUnlock()

	for id, agent := range s.agents {
		if err := agent.Start(s.ctx); err != nil {
			return fmt.Errorf("error starting agent %s: %w", id, err)
		}
	}

	return nil
}

// Stop stops all agents in the swarm
func (s *Swarm) Stop() error {
	s.mu.Lock()
	if s.cancel != nil {
		s.cancel()
	}
	s.mu.Unlock()

	s.mu.RLock()
	defer s.mu.RUnlock()

	var errs []error
	for id, agent := range s.agents {
		if err := agent.Stop(); err != nil {
			errs = append(errs, fmt.Errorf("error stopping agent %s: %w", id, err))
		}
	}

	if len(errs) > 0 {
		return fmt.Errorf("errors stopping agents: %v", errs)
	}

	return nil
}

// Broadcast sends a message to all agents
func (s *Swarm) Broadcast(msg types.Message) error {
	s.mu.RLock()
	defer s.mu.RUnlock()

	msg.Type = types.MessageTypeBroadcast

	var errs []error
	for id, agent := range s.agents {
		if err := agent.SendMessage(msg); err != nil {
			errs = append(errs, fmt.Errorf("error sending to agent %s: %w", id, err))
		}
	}

	if len(errs) > 0 {
		return fmt.Errorf("errors broadcasting: %v", errs)
	}

	return nil
}

// SendMessage sends a message from one agent to another
func (s *Swarm) SendMessage(from, to string, content interface{}, msgType types.MessageType) error {
	s.mu.RLock()
	defer s.mu.RUnlock()

	targetAgent, exists := s.agents[to]
	if !exists {
		return fmt.Errorf("target agent %s not found", to)
	}

	msg := types.Message{
		From:    from,
		To:      to,
		Content: content,
		Type:    msgType,
	}

	return targetAgent.SendMessage(msg)
}

// DistributeTask distributes a task to an available agent
func (s *Swarm) DistributeTask(task types.Task) error {
	s.mu.RLock()
	defer s.mu.RUnlock()

	// Find an idle agent
	for _, agent := range s.agents {
		if agent.GetState() == types.StateIdle || agent.GetState() == types.StateProcessing {
			msg := types.Message{
				From:    "swarm",
				To:      agent.GetID(),
				Content: task,
				Type:    types.MessageTypeTask,
			}
			return agent.SendMessage(msg)
		}
	}

	return fmt.Errorf("no available agents to handle task")
}

// GetSwarmStatus returns the status of all agents
func (s *Swarm) GetSwarmStatus() map[string]types.AgentState {
	s.mu.RLock()
	defer s.mu.RUnlock()

	status := make(map[string]types.AgentState)
	for id, agent := range s.agents {
		status[id] = agent.GetState()
	}
	return status
}