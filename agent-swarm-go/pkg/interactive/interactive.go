package interactive

import (
	"fmt"
	"strconv"
	"time"

	"agent-swarm-go/pkg/cli"
	"agent-swarm-go/pkg/scenarios"
	"agent-swarm-go/pkg/swarm"
	"agent-swarm-go/pkg/types"
	"agent-swarm-go/pkg/workflows"
)

// Session manages an interactive swarm session
type Session struct {
	swarm *swarm.Swarm
	cli   *cli.CLI
}

// NewSession creates a new interactive session
func NewSession(s *swarm.Swarm) *Session {
	return &Session{
		swarm: s,
		cli:   cli.NewCLI(),
	}
}

// Start begins the interactive session
func (s *Session) Start() {
	s.cli.PrintBanner()
	s.cli.WaitForEnter("Press Enter to start")

	for {
		s.cli.ShowMainMenu()
		choice := s.cli.GetChoice("Select an option (0-7)")

		switch choice {
		case "1":
			s.runResearchAnalysis()
		case "2":
			s.runParallelProcessing()
		case "3":
			s.runCustomTask()
		case "4":
			s.showSwarmStatus()
		case "5":
			s.broadcastMessage()
		case "6":
			s.showAgentDetails()
		case "7":
			s.runStressTest()
		case "0":
			s.cli.PrintInfo("Shutting down swarm...")
			return
		default:
			s.cli.PrintError("Invalid choice. Please select 0-7")
		}

		if choice != "0" && choice != "4" {
			s.cli.WaitForEnter("\nPress Enter to return to main menu")
		}
	}
}

// runResearchAnalysis executes the research and analysis workflow
func (s *Session) runResearchAnalysis() {
	s.cli.PrintSection("Research & Analysis Workflow")

	fmt.Println("This workflow will:")
	fmt.Println("  1. Research your topic with comprehensive findings")
	fmt.Println("  2. Analyze the research data for insights and patterns")
	fmt.Println("  3. Generate a professional executive report")
	fmt.Println()

	topic := s.cli.GetInputWithDefault("Enter research topic", "quantum computing")

	// Use the research workflow for proper sequential execution with context passing
	workflow := workflows.NewResearchWorkflow(s.swarm)

	result, err := workflow.Execute(topic)
	if err != nil {
		s.cli.PrintError(fmt.Sprintf("Workflow failed: %v", err))
		return
	}

	// Display the complete results
	result.Display()
}

// runParallelProcessing executes parallel task processing
func (s *Session) runParallelProcessing() {
	s.cli.PrintSection("Parallel Task Processing")

	countStr := s.cli.GetInputWithDefault("How many parallel tasks?", "10")
	count, err := strconv.Atoi(countStr)
	if err != nil || count < 1 {
		s.cli.PrintError("Invalid number. Using default: 10")
		count = 10
	}

	if count > 100 {
		if !s.cli.Confirm(fmt.Sprintf("You want to create %d tasks. This may take a while. Continue?", count)) {
			return
		}
	}

	scenario := scenarios.ParallelProcessingScenario(count)

	// Execute with progress callback
	if err := scenarios.ExecuteScenario(s.swarm, scenario, func(current, total int) {
		s.cli.PrintProgress(current, total, "Distributing")
	}); err != nil {
		s.cli.PrintError(fmt.Sprintf("Scenario execution failed: %v", err))
		return
	}

	// Give workers time to process
	waitTime := time.Duration(count/2+2) * time.Second
	s.cli.PrintInfo(fmt.Sprintf("Processing tasks (waiting %v)...", waitTime))
	time.Sleep(waitTime)

	s.cli.PrintSuccess(fmt.Sprintf("Successfully processed %d parallel tasks!", count))
}

// runCustomTask creates and executes custom tasks
func (s *Session) runCustomTask() {
	s.cli.PrintSection("Custom Task Creation")

	taskID := s.cli.GetInputWithDefault("Task ID", fmt.Sprintf("custom-%d", time.Now().Unix()))
	description := s.cli.GetInput("Task description")
	priorityStr := s.cli.GetInputWithDefault("Priority (1-5)", "1")

	priority, err := strconv.Atoi(priorityStr)
	if err != nil || priority < 1 || priority > 5 {
		s.cli.PrintError("Invalid priority. Using 1")
		priority = 1
	}

	task := types.Task{
		ID:          taskID,
		Description: description,
		Priority:    priority,
		Payload:     map[string]string{"custom": "true", "created": time.Now().Format(time.RFC3339)},
	}

	s.cli.PrintInfo(fmt.Sprintf("Creating task: [%s] %s (Priority: %d)", task.ID, task.Description, task.Priority))

	if err := s.swarm.DistributeTask(task); err != nil {
		s.cli.PrintError(fmt.Sprintf("Failed to distribute task: %v", err))
		return
	}

	s.cli.PrintSuccess("Task distributed successfully!")

	if s.cli.Confirm("Create another task?") {
		s.runCustomTask()
	}
}

// showSwarmStatus displays the current status of all agents
func (s *Session) showSwarmStatus() {
	s.cli.PrintSection("Swarm Status")

	status := s.swarm.GetSwarmStatus()
	agents := s.swarm.ListAgents()

	if len(agents) == 0 {
		s.cli.PrintError("No agents in swarm")
		return
	}

	headers := []string{"Agent ID", "Status", "Specialty"}
	rows := make([][]string, 0, len(agents))

	for _, agentID := range agents {
		state := status[agentID]
		specialty := "worker"
		if len(agentID) > 0 {
			// Extract specialty from agent ID if possible
			if agentID[:3] == "wor" {
				// Parse specialty from worker agent
				specialty = "general"
			} else if agentID[:3] == "coo" {
				specialty = "coordinator"
			}
		}

		rows = append(rows, []string{agentID, string(state), specialty})
	}

	s.cli.PrintTable(headers, rows)

	s.cli.PrintInfo(fmt.Sprintf("Total agents: %d", len(agents)))
}

// broadcastMessage sends a broadcast message to all agents
func (s *Session) broadcastMessage() {
	s.cli.PrintSection("Broadcast Message")

	message := s.cli.GetInput("Enter message to broadcast")
	if message == "" {
		s.cli.PrintError("Message cannot be empty")
		return
	}

	msg := types.Message{
		From:    "user",
		Content: message,
		Type:    types.MessageTypeBroadcast,
	}

	if err := s.swarm.Broadcast(msg); err != nil {
		s.cli.PrintError(fmt.Sprintf("Broadcast failed: %v", err))
		return
	}

	s.cli.PrintSuccess(fmt.Sprintf("Message broadcast to %d agents", len(s.swarm.ListAgents())))
}

// showAgentDetails displays detailed information about a specific agent
func (s *Session) showAgentDetails() {
	s.cli.PrintSection("Agent Details")

	agents := s.swarm.ListAgents()
	if len(agents) == 0 {
		s.cli.PrintError("No agents available")
		return
	}

	fmt.Println("\nAvailable agents:")
	for i, agentID := range agents {
		fmt.Printf("  %d. %s\n", i+1, agentID)
	}

	choice := s.cli.GetInput("\nEnter agent number or ID")

	var selectedAgent string
	if num, err := strconv.Atoi(choice); err == nil && num > 0 && num <= len(agents) {
		selectedAgent = agents[num-1]
	} else {
		selectedAgent = choice
	}

	agent, err := s.swarm.GetAgent(selectedAgent)
	if err != nil {
		s.cli.PrintError(fmt.Sprintf("Agent not found: %v", err))
		return
	}

	fmt.Printf("\n╔═══════════════════════════════════════════════════════╗\n")
	fmt.Printf("║  Agent: %-44s ║\n", agent.GetID())
	fmt.Printf("╠═══════════════════════════════════════════════════════╣\n")
	fmt.Printf("║  Status: %-43s ║\n", agent.GetState())
	fmt.Printf("║  Type: %-45s ║\n", "Worker Agent")
	fmt.Printf("╚═══════════════════════════════════════════════════════╝\n")
}

// runStressTest executes a stress test scenario
func (s *Session) runStressTest() {
	s.cli.PrintSection("Stress Test")

	s.cli.PrintInfo("This will create a large number of tasks to test swarm capacity")

	countStr := s.cli.GetInputWithDefault("Number of tasks (default: 50, max: 1000)", "50")
	count, err := strconv.Atoi(countStr)
	if err != nil || count < 1 {
		count = 50
	}
	if count > 1000 {
		s.cli.PrintError("Maximum 1000 tasks allowed. Setting to 1000.")
		count = 1000
	}

	if !s.cli.Confirm(fmt.Sprintf("Create and process %d tasks?", count)) {
		return
	}

	scenario := scenarios.StressTestScenario(count)

	startTime := time.Now()

	if err := scenarios.ExecuteScenario(s.swarm, scenario, nil); err != nil {
		s.cli.PrintError(fmt.Sprintf("Stress test failed: %v", err))
		return
	}

	// Wait for processing
	waitTime := time.Duration(count/10+5) * time.Second
	s.cli.PrintInfo(fmt.Sprintf("Processing %d tasks (waiting %v)...", count, waitTime))
	time.Sleep(waitTime)

	elapsed := time.Since(startTime)

	s.cli.PrintSuccess(fmt.Sprintf("Stress test completed!"))
	fmt.Printf("  Tasks: %d\n", count)
	fmt.Printf("  Time: %v\n", elapsed)
	fmt.Printf("  Rate: %.2f tasks/sec\n", float64(count)/elapsed.Seconds())
}