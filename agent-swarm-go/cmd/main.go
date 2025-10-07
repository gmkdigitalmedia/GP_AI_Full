/*
Package main is the entry point for the Agent Swarm Go application.

This file orchestrates the entire system by:
  - Loading environment variables from .env file
  - Creating and configuring the agent swarm
  - Initializing AI-powered agents (researcher, analyzer, reporter)
  - Starting the web dashboard for real-time monitoring
  - Launching the interactive CLI for user interaction
  - Handling graceful shutdown on interrupt signals

The application uses a concurrent architecture where:
  - Agents run in separate goroutines
  - Web server runs in background
  - Interactive CLI runs in main flow
  - All components communicate via channels and event bus
*/
package main

import (
	"bufio"
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	"agent-swarm-go/pkg/agents"
	"agent-swarm-go/pkg/interactive"
	"agent-swarm-go/pkg/llm"
	"agent-swarm-go/pkg/swarm"
	"agent-swarm-go/pkg/web"
)

// init runs before main() and loads environment variables from .env file
// This allows API keys and configuration to be stored in .env instead of hardcoded
func init() {
	loadEnvFile(".env")
}

// loadEnvFile reads a .env file and loads KEY=VALUE pairs into environment variables.
// This function:
//   - Opens the specified .env file
//   - Parses each line for KEY=VALUE format
//   - Skips empty lines and comments (lines starting with #)
//   - Only sets variables that aren't already set in the environment
//   - Silently returns if .env file doesn't exist (it's optional)
//
// Example .env file:
//   OPENAI_API_KEY=sk-...
//   ANTHROPIC_API_KEY=sk-ant-...
func loadEnvFile(filename string) {
	// Try to open the .env file
	file, err := os.Open(filename)
	if err != nil {
		return // .env file is optional, so we don't error if it's missing
	}
	defer file.Close()

	// Read file line by line
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())

		// Skip empty lines and comments (lines starting with #)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}

		// Parse KEY=VALUE pairs
		// SplitN with 2 allows values to contain = signs
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])

			// Only set if not already set in environment
			// This allows environment variables to override .env file
			if os.Getenv(key) == "" {
				os.Setenv(key, value)
			}
		}
	}
}

// main is the application entry point that sets up and runs the agent swarm system.
//
// Execution flow:
//   1. Create swarm coordinator
//   2. Check for API keys (OpenAI or Anthropic)
//   3. Create three specialized AI agents:
//      - researcher-1: Gathers comprehensive information on topics
//      - analyzer-1: Analyzes data and identifies patterns
//      - reporter-1: Generates professional reports
//   4. Start all agents in background goroutines
//   5. Launch web dashboard on port 8080
//   6. Start interactive CLI for user commands
//   7. Wait for user to quit or Ctrl+C
//   8. Gracefully shutdown all components
func main() {
	// Create a new swarm coordinator that manages all agents
	// The swarm handles agent registration, task distribution, and event publishing
	s := swarm.NewSwarm()

	// Check for API keys and display connection status
	// The LLM client will try OPENAI_API_KEY first, then ANTHROPIC_API_KEY
	llmClient := llm.NewClient()
	if !llmClient.HasAPIKey() {
		// No API key found - system will run in demo mode with simulated responses
		fmt.Println("\n⚠️  WARNING: No API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
		fmt.Println("   Agents will run in DEMO MODE with simulated responses")
		fmt.Println("   Set an API key in your environment for real AI-powered research\n")
		time.Sleep(2 * time.Second)
	} else {
		// API key found - show which provider we're using
		fmt.Printf("\n✅ Connected to %s for AI-powered agent swarm\n\n", llmClient.GetProvider())
	}

	// Create three specialized AI agents
	// Each agent has a unique ID and receives the swarm's event bus for publishing events

	// ResearchAgent: Specializes in gathering comprehensive information on any topic
	// Uses LLM to break down research questions, gather data, and identify key insights
	researcher := agents.NewResearchAgent("researcher-1", s.GetEventBus())

	// AnalysisAgent: Specializes in analyzing research data
	// Uses LLM to identify patterns, correlations, and generate actionable insights
	analyzer := agents.NewAnalysisAgent("analyzer-1", s.GetEventBus())

	// ReportAgent: Specializes in creating professional reports
	// Uses LLM to synthesize research and analysis into executive-friendly reports
	reporter := agents.NewReportAgent("reporter-1", s.GetEventBus())

	// Add all agents to the swarm
	// The swarm maintains a registry of agents and routes tasks to them
	if err := s.AddAgent(researcher); err != nil {
		log.Fatalf("Failed to add researcher: %v", err)
	}
	if err := s.AddAgent(analyzer); err != nil {
		log.Fatalf("Failed to add analyzer: %v", err)
	}
	if err := s.AddAgent(reporter); err != nil {
		log.Fatalf("Failed to add reporter: %v", err)
	}

	// Create a context for coordinating graceful shutdown
	// When cancel() is called, all goroutines will receive the cancellation signal
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Set up signal handler for graceful shutdown on Ctrl+C or SIGTERM
	// This ensures all agents finish their current tasks before exiting
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM)
	go func() {
		<-sigChan // Block until we receive an interrupt signal
		fmt.Println("\n\nReceived interrupt signal. Shutting down...")
		cancel() // Trigger cancellation to stop all components
	}()

	// Start all agents in background goroutines
	// Each agent runs its own message processing loop
	fmt.Println("Initializing agent swarm...")
	if err := s.Start(ctx); err != nil {
		log.Fatalf("Failed to start swarm: %v", err)
	}

	// Give agents a moment to fully initialize their goroutines
	time.Sleep(500 * time.Millisecond)

	// Start web dashboard server in background goroutine
	// The web server provides real-time monitoring at http://localhost:8080
	// Features:
	//   - Live agent status cards
	//   - Real-time event stream via WebSocket
	//   - Task statistics and completion tracking
	//   - Full task results display
	webServer := web.NewServer(s)
	go func() {
		if err := webServer.Start(8080); err != nil {
			log.Printf("Web server error: %v", err)
		}
	}()

	// Display web dashboard URL to user
	fmt.Println("\n🌐 Web Dashboard: http://localhost:8080")
	fmt.Println("📊 Open the URL above in your browser for real-time monitoring!")
	time.Sleep(1 * time.Second)

	// Create and start the interactive CLI session
	// This provides a menu-driven interface for:
	//   - Running research workflows
	//   - Creating custom tasks
	//   - Viewing agent status
	//   - Broadcasting messages
	session := interactive.NewSession(s)

	// Run interactive session in a goroutine so we can monitor for shutdown
	done := make(chan bool)
	go func() {
		session.Start() // Blocks until user quits
		done <- true
	}()

	// Wait for either:
	//   - User to quit from interactive session (done channel receives)
	//   - Interrupt signal received (ctx.Done() receives)
	select {
	case <-done:
		// User quit normally from interactive menu
		cancel()
	case <-ctx.Done():
		// Interrupt signal received (Ctrl+C)
	}

	// Gracefully stop all agents
	// This allows agents to finish their current tasks before exiting
	fmt.Println("\nStopping all agents...")
	if err := s.Stop(); err != nil {
		log.Printf("Error stopping swarm: %v", err)
	}

	// Display goodbye message
	fmt.Println("\n=== Agent Swarm Demo Complete ===")
	fmt.Println("Thank you for using Agent Swarm!")
}