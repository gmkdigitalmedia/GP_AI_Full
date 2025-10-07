/*
Package agent provides the base agent implementation that all specialized agents inherit from.

BaseAgent is the foundation for all agents in the swarm system. It provides:
  - Message queue and processing loop
  - Thread-safe state management
  - Customizable message handlers
  - Lifecycle management (start/stop)
  - Context-based cancellation

All specialized agents (ResearchAgent, AnalysisAgent, ReportAgent) embed BaseAgent
to inherit this core functionality, then add their own specialized behavior.

Architecture Pattern:
  BaseAgent provides the "how" (message handling, concurrency)
  Specialized agents provide the "what" (research, analysis, reporting)

This separation of concerns allows:
  - Reusable infrastructure code
  - Consistent behavior across all agents
  - Easy creation of new agent types
  - Reliable concurrency management
*/
package agent

import (
	"context"
	"fmt"
	"sync"

	"agent-swarm-go/pkg/types"
)

// BaseAgent provides the foundational implementation for all agents in the system.
//
// It handles the low-level details of being an agent:
//   - Message queuing and delivery
//   - Concurrent execution in a goroutine
//   - Thread-safe state tracking
//   - Graceful startup and shutdown
//   - Customizable message type handlers
//
// Design Pattern: Embedded Struct Inheritance
//   Specialized agents embed BaseAgent to inherit all this functionality:
//     type ResearchAgent struct {
//         *agent.BaseAgent  // Inherits all BaseAgent methods
//         // Add specialized fields...
//     }
//
// Concurrency Model:
//   - Each agent runs in its own goroutine (via run() loop)
//   - Messages are sent to a buffered channel (inbox)
//   - The agent's goroutine processes messages sequentially
//   - Thread-safety is ensured with sync.RWMutex
//
// Message Flow:
//   External → SendMessage() → inbox channel → run() loop → handleMessage() → registered handler
//
// Example Usage:
//   // Create a basic agent
//   agent := agent.NewBaseAgent("worker-1")
//
//   // Register custom handler
//   agent.RegisterHandler(types.MessageTypeTask, func(msg types.Message) error {
//       // Custom task handling logic
//       return nil
//   })
//
//   // Start the agent
//   agent.Start(ctx)
//
//   // Send messages (handled automatically)
//   agent.SendMessage(types.Message{Type: types.MessageTypeTask, ...})
type BaseAgent struct {
	id       string                               // Unique identifier (e.g., "researcher-1", "worker-2")
	state    types.AgentState                     // Current state: idle, processing, or stopped
	inbox    chan types.Message                   // Message queue (buffered to 100 messages)
	mu       sync.RWMutex                         // Mutex for thread-safe access to state and handlers
	ctx      context.Context                      // Context for cancellation and lifecycle
	cancel   context.CancelFunc                   // Function to cancel the context and stop the agent
	wg       sync.WaitGroup                       // WaitGroup to ensure graceful shutdown
	handlers map[types.MessageType]MessageHandler // Custom handlers for different message types
}

// MessageHandler is a function signature for handling specific message types.
//
// When you register a handler for a message type (e.g., MessageTypeTask),
// this function will be called whenever a message of that type arrives.
//
// Parameters:
//   - msg: The message to process (contains Type, From, To, Content)
//
// Returns:
//   - error: If processing failed, nil if successful
//
// Example Handler:
//   func handleTask(msg types.Message) error {
//       task := msg.Content.(types.Task)
//       // Process task...
//       return nil
//   }
//
// Thread Safety:
//   Handlers are called from the agent's goroutine, so they execute sequentially.
//   You don't need locks within the handler for the same agent.
type MessageHandler func(msg types.Message) error

// NewBaseAgent creates and initializes a new base agent.
//
// The agent is created in the "idle" state with:
//   - Empty message queue (buffered channel, capacity 100)
//   - No registered handlers (empty map)
//   - Ready to be started
//
// Buffer Size (100):
//   The inbox can hold up to 100 messages before SendMessage() blocks.
//   This prevents overwhelming the agent with too many tasks at once.
//   If the buffer fills up, senders will get an error.
//
// Parameters:
//   - id: Unique identifier for this agent (should be unique in the swarm)
//
// Returns:
//   - *BaseAgent: Fully initialized agent ready to be started
//
// Example:
//   agent := NewBaseAgent("worker-1")
//   // agent.state == StateIdle
//   // agent.inbox is ready to receive messages
//   // agent.handlers is empty (default behavior)
func NewBaseAgent(id string) *BaseAgent {
	return &BaseAgent{
		id:       id,                                           // Store unique identifier
		state:    types.StateIdle,                              // Start in idle state
		inbox:    make(chan types.Message, 100),                // Buffered channel for messages
		handlers: make(map[types.MessageType]MessageHandler),   // Empty handler map
	}
}

// GetID returns the unique identifier of this agent.
//
// The ID is used for:
//   - Routing messages to the correct agent
//   - Logging and debugging
//   - Event publishing (tracking which agent did what)
//   - Swarm registry (looking up agents by ID)
//
// Returns:
//   - string: The agent's unique identifier
//
// Thread Safety: Safe to call from any goroutine (id is immutable after creation)
func (a *BaseAgent) GetID() string {
	return a.id
}

// Start begins the agent's execution loop in a background goroutine.
//
// What happens when you call Start():
//   1. Validates agent is not already running
//   2. Creates a cancellable context (for shutdown)
//   3. Sets state to "processing"
//   4. Launches run() in a new goroutine
//   5. Returns immediately (non-blocking)
//
// The run() goroutine will:
//   - Wait for messages on the inbox channel
//   - Process each message with registered handlers
//   - Continue until context is cancelled or inbox closes
//
// Context Hierarchy:
//   - Parent context (ctx parameter) is often the application context
//   - Child context (a.ctx) is created with WithCancel
//   - Calling a.cancel() stops this agent but not others
//   - Cancelling parent context stops all agents
//
// Parameters:
//   - ctx: Parent context for lifecycle management
//
// Returns:
//   - error: If agent is already running, nil on success
//
// Example:
//   // Application context
//   appCtx, appCancel := context.WithCancel(context.Background())
//
//   // Start agent with app context
//   if err := agent.Start(appCtx); err != nil {
//       log.Fatal(err)
//   }
//
//   // Agent now running in background
//   // To stop: appCancel() or agent.Stop()
//
// Thread Safety: Uses mutex to protect state checks
func (a *BaseAgent) Start(ctx context.Context) error {
	a.mu.Lock() // Acquire write lock

	// Check if already running
	if a.state != types.StateIdle {
		a.mu.Unlock()
		return fmt.Errorf("agent %s is already running", a.id)
	}

	// Create cancellable child context
	// When this context is cancelled, the agent's goroutine will exit
	a.ctx, a.cancel = context.WithCancel(ctx)

	// Update state to processing
	// Note: Agents start in "processing" state (ready to process messages)
	// even if they're currently idle waiting for messages
	a.state = types.StateProcessing

	a.mu.Unlock() // Release write lock

	// Add to WaitGroup for graceful shutdown tracking
	a.wg.Add(1)

	// Launch the message processing loop in a new goroutine
	go a.run()

	return nil
}

// Stop gracefully shuts down the agent.
//
// Shutdown sequence:
//   1. Checks if agent is already stopped (idempotent)
//   2. Cancels the agent's context (signals run() to exit)
//   3. Waits for run() goroutine to finish (wg.Wait)
//   4. Sets state to "stopped"
//   5. Closes the inbox channel (no more messages accepted)
//
// Graceful Shutdown:
//   - Agent finishes processing current message before exiting
//   - WaitGroup ensures we don't return until goroutine exits
//   - Closing inbox prevents new messages from being sent
//
// Idempotent:
//   Safe to call multiple times - will return nil if already stopped
//
// Returns:
//   - error: Currently always returns nil (reserved for future use)
//
// Example:
//   // Start agent
//   agent.Start(ctx)
//
//   // ... agent processes messages ...
//
//   // Stop agent gracefully
//   if err := agent.Stop(); err != nil {
//       log.Printf("Error stopping agent: %v", err)
//   }
//
//   // Agent's goroutine has now exited
//   // Inbox is closed, no more messages accepted
//
// Thread Safety: Uses mutex to protect state and ensures thread-safe shutdown
func (a *BaseAgent) Stop() error {
	a.mu.Lock()
	defer a.mu.Unlock()

	// Already stopped? Return early (idempotent)
	if a.state == types.StateStopped {
		return nil
	}

	// Cancel the context to signal run() to exit
	if a.cancel != nil {
		a.cancel()
	}

	// Wait for run() goroutine to finish
	// This ensures we don't close the inbox while run() is still using it
	a.wg.Wait()

	// Update state to stopped
	a.state = types.StateStopped

	// Close inbox channel
	// This will cause any pending SendMessage() calls to fail
	close(a.inbox)

	return nil
}

// SendMessage sends a message to this agent's inbox.
//
// Message Delivery:
//   - Non-blocking: Returns immediately with error if inbox is full
//   - Buffered: Can queue up to 100 messages
//   - Thread-safe: Safe to call from multiple goroutines
//
// Error Conditions:
//   - Agent is stopped: Returns error
//   - Inbox is full (100 messages waiting): Returns error
//
// Message Processing:
//   Messages are processed in FIFO order by the agent's run() loop.
//   Each message is handled sequentially (one at a time).
//
// Parameters:
//   - msg: Message to send (contains Type, From, To, Content)
//
// Returns:
//   - error: If agent is stopped or inbox is full, nil on success
//
// Example:
//   // Create a task message
//   msg := types.Message{
//       From:    "coordinator",
//       To:      "researcher-1",
//       Type:    types.MessageTypeTask,
//       Content: types.Task{
//           ID:          "task-001",
//           Description: "Research quantum computing",
//       },
//   }
//
//   // Send to agent
//   if err := agent.SendMessage(msg); err != nil {
//       log.Printf("Failed to send message: %v", err)
//   }
//
// Thread Safety: Uses read lock to check state, select ensures channel safety
func (a *BaseAgent) SendMessage(msg types.Message) error {
	a.mu.RLock()
	defer a.mu.RUnlock()

	// Check if agent is stopped
	if a.state == types.StateStopped {
		return fmt.Errorf("agent %s is stopped", a.id)
	}

	// Try to send message to inbox
	select {
	case a.inbox <- msg:
		// Successfully queued message
		return nil
	default:
		// Inbox is full (100 messages already waiting)
		return fmt.Errorf("agent %s inbox is full", a.id)
	}
}

// ReceiveMessage attempts to receive a message from the inbox (non-blocking).
//
// This is a non-blocking receive operation:
//   - Returns immediately with (message, true) if message available
//   - Returns immediately with (nil, false) if no message available
//   - Does not wait for messages to arrive
//
// Use Cases:
//   - Polling for messages in a loop
//   - Checking if messages are available
//   - Custom message processing loops
//
// Note: Most agents don't use this directly.
//   The run() loop handles message processing automatically.
//   This is primarily for testing or custom agent implementations.
//
// Returns:
//   - *types.Message: The message if available, nil otherwise
//   - bool: true if message was received, false if not available or channel closed
//
// Example:
//   if msg, ok := agent.ReceiveMessage(); ok {
//       // Process message
//       fmt.Printf("Received: %+v\n", msg)
//   } else {
//       // No message available
//       fmt.Println("No messages")
//   }
//
// Thread Safety: Channel operations are thread-safe
func (a *BaseAgent) ReceiveMessage() (*types.Message, bool) {
	select {
	case msg, ok := <-a.inbox:
		if !ok {
			// Channel closed
			return nil, false
		}
		return &msg, true
	default:
		// No message available
		return nil, false
	}
}

// ProcessTask processes a task and returns a result.
//
// DEFAULT IMPLEMENTATION - Should be overridden by specialized agents.
//
// This is a placeholder that:
//   - Returns success for any task
//   - Doesn't actually do any processing
//   - Just logs that the task was received
//
// Specialized agents override this with real logic:
//   - ResearchAgent: Calls LLM API to research topics
//   - AnalysisAgent: Calls LLM API to analyze data
//   - ReportAgent: Calls LLM API to generate reports
//
// Override Pattern:
//   type ResearchAgent struct {
//       *agent.BaseAgent
//       // ... specialized fields
//   }
//
//   func (ra *ResearchAgent) ProcessTask(task types.Task) types.Result {
//       // Real implementation here
//       return types.Result{...}
//   }
//
// Parameters:
//   - task: Task to process (contains ID, Description, Context, etc.)
//
// Returns:
//   - types.Result: Result with Success=true and a default message
//
// Example Override:
//   func (ra *ResearchAgent) ProcessTask(task types.Task) types.Result {
//       // Call LLM API
//       response, err := ra.llmClient.Complete(...)
//       if err != nil {
//           return types.Result{TaskID: task.ID, Success: false}
//       }
//       return types.Result{TaskID: task.ID, Success: true, Data: response}
//   }
func (a *BaseAgent) ProcessTask(task types.Task) types.Result {
	// Default implementation - should be overridden by subclasses
	return types.Result{
		TaskID:  task.ID,
		Success: true,
		Data:    fmt.Sprintf("Agent %s processed task %s", a.id, task.ID),
	}
}

// GetState returns the current state of the agent.
//
// Possible States:
//   - StateIdle:       Agent created but not started
//   - StateProcessing: Agent running and ready to process messages
//   - StateStopped:    Agent has been shut down
//
// Use Cases:
//   - Checking if agent is ready before sending messages
//   - Monitoring agent health
//   - Displaying agent status in dashboards
//   - Debugging agent lifecycle issues
//
// Returns:
//   - types.AgentState: Current state ("idle", "processing", or "stopped")
//
// Example:
//   state := agent.GetState()
//   switch state {
//   case types.StateIdle:
//       fmt.Println("Agent not started yet")
//   case types.StateProcessing:
//       fmt.Println("Agent is running")
//   case types.StateStopped:
//       fmt.Println("Agent has been stopped")
//   }
//
// Thread Safety: Uses read lock to ensure safe concurrent access
func (a *BaseAgent) GetState() types.AgentState {
	a.mu.RLock()
	defer a.mu.RUnlock()
	return a.state
}

// RegisterHandler registers a custom handler function for a specific message type.
//
// Message Type Routing:
//   When a message arrives, the agent checks its Type field:
//   - If a handler is registered for that type, the handler is called
//   - If no handler exists, default handling is used
//
// Handler Registration:
//   - Can register multiple handlers for different message types
//   - Later registrations override earlier ones for the same type
//   - Handlers are called sequentially (one message at a time)
//
// Common Pattern (in specialized agents):
//   func NewResearchAgent(id string) *ResearchAgent {
//       ra := &ResearchAgent{BaseAgent: NewBaseAgent(id)}
//
//       // Register task handler
//       ra.RegisterHandler(types.MessageTypeTask, ra.handleTask)
//
//       return ra
//   }
//
// Parameters:
//   - msgType: The message type to handle (e.g., MessageTypeTask, MessageTypeResult)
//   - handler: Function to call when messages of this type arrive
//
// Example:
//   // Register a custom task handler
//   agent.RegisterHandler(types.MessageTypeTask, func(msg types.Message) error {
//       task := msg.Content.(types.Task)
//       fmt.Printf("Processing task: %s\n", task.Description)
//       result := agent.ProcessTask(task)
//       // Publish result, update state, etc.
//       return nil
//   })
//
// Thread Safety: Uses write lock to safely update handler map
func (a *BaseAgent) RegisterHandler(msgType types.MessageType, handler MessageHandler) {
	a.mu.Lock()
	defer a.mu.Unlock()

	// Store handler in map, indexed by message type
	a.handlers[msgType] = handler
}

// run is the main execution loop for the agent.
//
// This function runs in a separate goroutine (started by Start()).
//
// Loop Behavior:
//   1. Wait for one of two events:
//      a) Context cancelled (shutdown signal)
//      b) Message arrives in inbox
//   2. If context cancelled: Exit loop and return
//   3. If message arrives: Call handleMessage() to process it
//   4. Repeat (back to step 1)
//
// Message Processing:
//   - Messages are processed sequentially (one at a time)
//   - No concurrent message processing within the same agent
//   - This ensures thread-safety for agent state
//
// Lifecycle:
//   - Runs until ctx.Done() signals (via cancel() or parent cancellation)
//   - Decrements WaitGroup on exit (allows Stop() to wait for completion)
//   - Exits gracefully after processing current message
//
// Goroutine Management:
//   - defer a.wg.Done() ensures WaitGroup is decremented even if panic occurs
//   - This allows Stop() to complete even in error conditions
//
// Thread Safety:
//   This function runs in its own goroutine, separate from other agents.
//   Multiple agents can run concurrently, each in their own goroutine.
func (a *BaseAgent) run() {
	// Ensure WaitGroup is decremented when this function exits
	// This allows Stop() to wait for goroutine completion
	defer a.wg.Done()

	// Main message processing loop
	for {
		select {
		case <-a.ctx.Done():
			// Context was cancelled (Stop() was called or parent context cancelled)
			// Exit the loop and return, ending the goroutine
			return

		case msg, ok := <-a.inbox:
			if !ok {
				// Channel was closed (shouldn't happen before ctx.Done, but handled defensively)
				return
			}

			// Process the message using registered handlers or default handling
			a.handleMessage(msg)
		}
	}
}

// handleMessage processes an incoming message by routing it to the appropriate handler.
//
// Message Routing Logic:
//   1. Look up if a handler is registered for msg.Type
//   2. If handler exists: Call it
//   3. If no handler: Use default handling based on message type
//
// Registered Handler Path:
//   - Handler function is called with the message
//   - If handler returns error, it's logged but doesn't crash the agent
//   - Agent continues processing next message
//
// Default Handling (no registered handler):
//   - MessageTypeTask: Extract task, call ProcessTask(), log result
//   - Other types: Just log that message was received
//
// Error Handling:
//   - Errors from handlers are logged but don't stop the agent
//   - This ensures one bad message doesn't crash the entire agent
//   - Agent remains available to process subsequent messages
//
// Parameters:
//   - msg: The message to process
//
// Thread Safety:
//   - Uses read lock to access handler map
//   - Called from run() goroutine (sequential processing)
//   - No concurrent calls within the same agent
func (a *BaseAgent) handleMessage(msg types.Message) {
	// Look up handler for this message type (with read lock)
	a.mu.RLock()
	handler, exists := a.handlers[msg.Type]
	a.mu.RUnlock()

	if exists {
		// Registered handler found - call it
		if err := handler(msg); err != nil {
			// Handler returned an error - log it but continue processing
			// This ensures one bad message doesn't crash the agent
			fmt.Printf("Agent %s: error handling message: %v\n", a.id, err)
		}
	} else {
		// No registered handler - use default handling
		switch msg.Type {
		case types.MessageTypeTask:
			// Default task handling
			if task, ok := msg.Content.(types.Task); ok {
				// Call ProcessTask (may be overridden by specialized agents)
				result := a.ProcessTask(task)
				fmt.Printf("Agent %s: processed task %s, result: %+v\n", a.id, task.ID, result)
			}
		default:
			// Unknown message type - just log it
			fmt.Printf("Agent %s: received message type %s from %s\n", a.id, msg.Type, msg.From)
		}
	}
}
