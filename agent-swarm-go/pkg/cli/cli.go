package cli

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

// CLI provides interactive command-line interface functionality
type CLI struct {
	reader *bufio.Reader
}

// NewCLI creates a new CLI instance
func NewCLI() *CLI {
	return &CLI{
		reader: bufio.NewReader(os.Stdin),
	}
}

// PrintBanner displays the application banner
func (c *CLI) PrintBanner() {
	banner := `
╔═══════════════════════════════════════════════════════════╗
║         AGENT SWARM - Interactive Multi-Agent System      ║
║                       Go Implementation                    ║
╚═══════════════════════════════════════════════════════════╝

A concurrent agent swarm system featuring:
• Multiple specialized worker agents
• Coordinator-based task delegation
• Real-time task processing and monitoring
• Interactive scenario-based workflows
• Parallel and sequential task execution
`
	fmt.Println(banner)
}

// ShowMainMenu displays the main menu options
func (c *CLI) ShowMainMenu() {
	fmt.Println("\n" + strings.Repeat("═", 70))
	fmt.Println("MAIN MENU - Select a Scenario")
	fmt.Println(strings.Repeat("═", 70))
	fmt.Println("1. Research & Analysis Workflow")
	fmt.Println("   → Data processing + Analytics + Report generation")
	fmt.Println()
	fmt.Println("2. Parallel Task Processing")
	fmt.Println("   → Distribute multiple tasks across all workers")
	fmt.Println()
	fmt.Println("3. Custom Task Creation")
	fmt.Println("   → Create your own tasks interactively")
	fmt.Println()
	fmt.Println("4. Swarm Status")
	fmt.Println("   → View current status of all agents")
	fmt.Println()
	fmt.Println("5. Broadcast Message")
	fmt.Println("   → Send a message to all agents")
	fmt.Println()
	fmt.Println("6. View Agent Details")
	fmt.Println("   → Inspect specific agent information")
	fmt.Println()
	fmt.Println("7. Run Stress Test")
	fmt.Println("   → Process many tasks simultaneously")
	fmt.Println()
	fmt.Println("0. Exit")
	fmt.Println(strings.Repeat("═", 70))
}

// GetInput prompts the user for input with a message
func (c *CLI) GetInput(prompt string) string {
	fmt.Print(prompt + ": ")
	input, _ := c.reader.ReadString('\n')
	return strings.TrimSpace(input)
}

// GetInputWithDefault prompts with a default value option
func (c *CLI) GetInputWithDefault(prompt, defaultValue string) string {
	fmt.Printf("%s [%s]: ", prompt, defaultValue)
	input, _ := c.reader.ReadString('\n')
	input = strings.TrimSpace(input)
	if input == "" {
		return defaultValue
	}
	return input
}

// GetChoice prompts for a menu choice
func (c *CLI) GetChoice(prompt string) string {
	fmt.Print("\n" + prompt + " > ")
	input, _ := c.reader.ReadString('\n')
	return strings.TrimSpace(input)
}

// Confirm asks for yes/no confirmation
func (c *CLI) Confirm(prompt string) bool {
	response := c.GetInputWithDefault(prompt+" (y/n)", "y")
	response = strings.ToLower(response)
	return response == "y" || response == "yes"
}

// PrintSection prints a formatted section header
func (c *CLI) PrintSection(title string) {
	fmt.Println("\n" + strings.Repeat("─", 70))
	fmt.Printf("  %s\n", title)
	fmt.Println(strings.Repeat("─", 70))
}

// PrintSuccess prints a success message in green
func (c *CLI) PrintSuccess(message string) {
	fmt.Printf("\n✓ %s\n", message)
}

// PrintError prints an error message in red
func (c *CLI) PrintError(message string) {
	fmt.Printf("\n✗ %s\n", message)
}

// PrintInfo prints an informational message
func (c *CLI) PrintInfo(message string) {
	fmt.Printf("\nℹ %s\n", message)
}

// PrintTask prints task information
func (c *CLI) PrintTask(taskID, description string, priority int) {
	fmt.Printf("  [%s] %s (Priority: %d)\n", taskID, description, priority)
}

// PrintAgentStatus prints an agent's status
func (c *CLI) PrintAgentStatus(agentID, status string) {
	symbol := "●"
	fmt.Printf("  %s %-20s [%s]\n", symbol, agentID, status)
}

// WaitForEnter waits for user to press Enter
func (c *CLI) WaitForEnter(message string) {
	if message == "" {
		message = "Press Enter to continue"
	}
	fmt.Printf("\n%s...", message)
	c.reader.ReadString('\n')
}

// PrintTable prints data in a simple table format
func (c *CLI) PrintTable(headers []string, rows [][]string) {
	// Calculate column widths
	widths := make([]int, len(headers))
	for i, h := range headers {
		widths[i] = len(h)
	}
	for _, row := range rows {
		for i, cell := range row {
			if i < len(widths) && len(cell) > widths[i] {
				widths[i] = len(cell)
			}
		}
	}

	// Print header
	fmt.Println()
	for i, h := range headers {
		fmt.Printf("%-*s  ", widths[i], h)
	}
	fmt.Println()
	for i := range headers {
		fmt.Print(strings.Repeat("─", widths[i]) + "  ")
	}
	fmt.Println()

	// Print rows
	for _, row := range rows {
		for i, cell := range row {
			if i < len(widths) {
				fmt.Printf("%-*s  ", widths[i], cell)
			}
		}
		fmt.Println()
	}
}

// ClearScreen clears the terminal screen (basic version)
func (c *CLI) ClearScreen() {
	fmt.Print("\033[H\033[2J")
}

// PrintProgress shows a simple progress indicator
func (c *CLI) PrintProgress(current, total int, label string) {
	percent := float64(current) / float64(total) * 100
	bar := strings.Repeat("█", current) + strings.Repeat("░", total-current)
	fmt.Printf("\r%s [%s] %.0f%% (%d/%d)", label, bar, percent, current, total)
	if current == total {
		fmt.Println()
	}
}