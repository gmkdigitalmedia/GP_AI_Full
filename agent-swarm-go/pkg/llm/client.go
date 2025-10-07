// Package llm provides integration with Large Language Model (LLM) APIs.
//
// This package abstracts the differences between OpenAI and Anthropic APIs,
// providing a unified interface for making LLM calls. It automatically detects
// which API to use based on available environment variables and handles the
// protocol differences between providers.
//
// # Supported Providers
//
// OpenAI (GPT-4):
//   - Environment Variable: OPENAI_API_KEY
//   - Model: gpt-4
//   - Endpoint: https://api.openai.com/v1/chat/completions
//   - System prompts: Included in messages array with role "system"
//
// Anthropic (Claude):
//   - Environment Variable: ANTHROPIC_API_KEY
//   - Model: claude-3-5-sonnet-20241022
//   - Endpoint: https://api.anthropic.com/v1/messages
//   - System prompts: Sent as separate "system" field (not in messages array)
//
// # API Key Priority
//
// The client checks for API keys in this order:
//   1. OPENAI_API_KEY (if found, uses OpenAI)
//   2. ANTHROPIC_API_KEY (if found, uses Anthropic)
//   3. None (falls back to mock mode with simulated responses)
//
// # Mock Mode
//
// When no API key is available, the client operates in mock mode:
//   - No actual API calls are made
//   - Returns simulated responses based on prompt keywords
//   - Useful for development/testing without API costs
//   - All mock responses include disclaimer text
//
// # Usage Example
//
// Basic usage:
//   client := llm.NewClient()
//   systemPrompt := "You are a helpful research assistant."
//   userPrompt := "Explain quantum computing in simple terms"
//   history := []llm.Message{} // Empty for first call
//   response, err := client.Complete(systemPrompt, userPrompt, history)
//   if err != nil {
//       log.Fatal(err)
//   }
//   fmt.Println(response)
//
// With conversation history:
//   history := []llm.Message{
//       {Role: "user", Content: "What is Go?"},
//       {Role: "assistant", Content: "Go is a programming language..."},
//   }
//   response, err := client.Complete(systemPrompt, "Tell me more", history)
//
// # Thread Safety
//
// The Client struct is designed to be safe for concurrent use:
//   - All fields are set during initialization and never modified
//   - Each Complete() call creates new request objects
//   - HTTP clients are created per-request (stdlib http.Client is thread-safe)
//
// # API Differences
//
// OpenAI API:
//   - System prompt is a message with role "system"
//   - Authorization: Bearer token in header
//   - Response format: {"choices": [{"message": {"content": "..."}}]}
//
// Anthropic API:
//   - System prompt is separate "system" field in request body
//   - Authorization: x-api-key header
//   - Requires anthropic-version header
//   - Response format: {"content": [{"text": "..."}]}
//
// This package handles these differences transparently.
package llm

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"strings"
)

// Client handles interactions with LLM APIs (OpenAI or Anthropic).
//
// The client automatically detects which API to use based on environment
// variables and handles all protocol differences between providers.
//
// Fields:
//   - apiKey: The API key for authentication (from environment)
//   - model: The model identifier (e.g., "gpt-4" or "claude-3-5-sonnet-20241022")
//   - provider: Either "openai" or "anthropic" (detected automatically)
//
// Thread Safety: Safe for concurrent use. All fields are read-only after initialization.
type Client struct {
	apiKey   string
	model    string
	provider string // "openai" or "anthropic"
}

// NewClient creates a new LLM client by auto-detecting the available API.
//
// Detection Logic:
//   1. Checks OPENAI_API_KEY environment variable first
//   2. If not found, checks ANTHROPIC_API_KEY
//   3. If neither found, creates client in mock mode (apiKey = "")
//
// Returns:
//   - For OpenAI: Client{apiKey: "sk-...", model: "gpt-4", provider: "openai"}
//   - For Anthropic: Client{apiKey: "sk-ant-...", model: "claude-3-5-sonnet-20241022", provider: "anthropic"}
//   - For Mock: Client{apiKey: "", model: "gpt-4", provider: "openai"} (will use mockResponse())
//
// Usage:
//   // In main.go, after loading .env file:
//   client := llm.NewClient()
//
//   // Check which mode:
//   if client.HasAPIKey() {
//       fmt.Println("Using", client.GetProvider())
//   } else {
//       fmt.Println("Running in mock mode (no API key)")
//   }
//
// Thread Safety: Safe to call concurrently.
func NewClient() *Client {
	// Try OpenAI first, then Anthropic
	apiKey := os.Getenv("OPENAI_API_KEY")
	provider := "openai"
	model := "gpt-4"

	if apiKey == "" {
		// OpenAI not available, try Anthropic
		apiKey = os.Getenv("ANTHROPIC_API_KEY")
		provider = "anthropic"
		model = "claude-3-5-sonnet-20241022"
	}

	return &Client{
		apiKey:   apiKey,
		model:    model,
		provider: provider,
	}
}

// Message represents a single message in a conversation with an LLM.
//
// Fields:
//   - Role: The speaker of the message ("system", "user", or "assistant")
//   - Content: The text content of the message
//
// Role Values:
//   - "system": System instructions that set the agent's behavior
//   - "user": Messages from the human user or application
//   - "assistant": Previous responses from the LLM
//
// Usage in Conversation History:
//   history := []llm.Message{
//       {Role: "user", Content: "What is Go?"},
//       {Role: "assistant", Content: "Go is a programming language..."},
//       {Role: "user", Content: "Tell me more about its concurrency"},
//   }
//
// Note: The agents (research_agent.go, etc.) maintain the last 6 messages
// in their history to provide context for multi-turn conversations.
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

// OpenAIRequest represents the JSON structure for an OpenAI API request.
//
// API Endpoint: POST https://api.openai.com/v1/chat/completions
//
// Example JSON:
//   {
//     "model": "gpt-4",
//     "messages": [
//       {"role": "system", "content": "You are a research specialist..."},
//       {"role": "user", "content": "Research quantum computing"}
//     ]
//   }
//
// Fields:
//   - Model: The model identifier (e.g., "gpt-4")
//   - Messages: Array of conversation messages including system prompt
type OpenAIRequest struct {
	Model    string    `json:"model"`
	Messages []Message `json:"messages"`
}

// OpenAIResponse represents the JSON structure for an OpenAI API response.
//
// Example JSON:
//   {
//     "choices": [
//       {
//         "message": {
//           "role": "assistant",
//           "content": "# Research Findings\n\n..."
//         }
//       }
//     ]
//   }
//
// Fields:
//   - Choices: Array of possible responses (we use Choices[0])
//   - Choices[].Message: The assistant's response message
//
// Error Handling:
//   - If len(Choices) == 0, returns error "no response from API"
//   - If HTTP status != 200, returns error "API error: ..."
type OpenAIResponse struct {
	Choices []struct {
		Message Message `json:"message"`
	} `json:"choices"`
}

// AnthropicRequest represents the JSON structure for an Anthropic API request.
//
// API Endpoint: POST https://api.anthropic.com/v1/messages
//
// Example JSON:
//   {
//     "model": "claude-3-5-sonnet-20241022",
//     "max_tokens": 4096,
//     "system": "You are a research specialist...",
//     "messages": [
//       {"role": "user", "content": "Research quantum computing"}
//     ]
//   }
//
// Important Difference from OpenAI:
//   - System prompt is NOT in the messages array
//   - System prompt goes in a separate "system" field
//   - Messages array only contains user/assistant messages
//
// Fields:
//   - Model: The model identifier (e.g., "claude-3-5-sonnet-20241022")
//   - MaxTokens: Maximum tokens in response (4096 is generous for our use case)
//   - Messages: Array of user/assistant messages (no system role)
type AnthropicRequest struct {
	Model     string    `json:"model"`
	MaxTokens int       `json:"max_tokens"`
	Messages  []Message `json:"messages"`
}

// AnthropicResponse represents the JSON structure for an Anthropic API response.
//
// Example JSON:
//   {
//     "content": [
//       {
//         "text": "# Research Findings\n\n..."
//       }
//     ]
//   }
//
// Fields:
//   - Content: Array of content blocks (we use Content[0])
//   - Content[].Text: The assistant's response text
//
// Error Handling:
//   - If len(Content) == 0, returns error "no response from API"
//   - If HTTP status != 200, returns error "API error: ..."
type AnthropicResponse struct {
	Content []struct {
		Text string `json:"text"`
	} `json:"content"`
}

// Complete sends a prompt to the LLM and returns the AI-generated response.
//
// This is the main entry point for all LLM interactions. It handles:
//   - Mock mode fallback when no API key is available
//   - Building the complete message array with system prompt and history
//   - Routing to the appropriate API (OpenAI or Anthropic)
//
// Parameters:
//   - systemPrompt: Instructions that define the agent's role and behavior
//     Example: "You are a research specialist agent..."
//   - userPrompt: The current task or question from the user
//     Example: "Research quantum computing applications"
//   - conversationHistory: Previous messages for context (usually last 6)
//     Example: [{Role: "user", Content: "..."}, {Role: "assistant", Content: "..."}]
//
// Returns:
//   - string: The AI-generated response (usually in Markdown format)
//   - error: Any error from API call, JSON parsing, or HTTP issues
//
// Message Construction:
//   The function builds the messages array in this order:
//   1. System message (if systemPrompt != "")
//   2. Conversation history (previous user/assistant exchanges)
//   3. Current user message (the new prompt)
//
//   Example final messages array:
//   [
//     {Role: "system", Content: "You are a research specialist..."},
//     {Role: "user", Content: "What is AI?"},
//     {Role: "assistant", Content: "AI is..."},
//     {Role: "user", Content: "Tell me more"}  // Current prompt
//   ]
//
// Typical Response Time: 10-30 seconds (depends on LLM provider and load)
//
// Usage in Agents:
//   // In research_agent.go ProcessTask():
//   systemPrompt := "You are a research specialist..."
//   userPrompt := fmt.Sprintf("Research: %s", task.Description)
//   response, err := ra.llmClient.Complete(systemPrompt, userPrompt, ra.history)
//   if err != nil {
//       return types.Result{Success: false, Error: err.Error()}
//   }
//   // response now contains AI-generated research report
//
// Thread Safety: Safe to call concurrently. Each call creates new request objects.
func (c *Client) Complete(systemPrompt string, userPrompt string, conversationHistory []Message) (string, error) {
	// If no API key, use mock mode (simulated responses)
	if c.apiKey == "" {
		return c.mockResponse(userPrompt), nil
	}

	// Build complete messages array:
	// 1. Start with copy of conversation history
	messages := append([]Message{}, conversationHistory...)

	// 2. Prepend system prompt if provided
	if systemPrompt != "" {
		messages = append([]Message{{Role: "system", Content: systemPrompt}}, messages...)
	}

	// 3. Append current user prompt
	messages = append(messages, Message{Role: "user", Content: userPrompt})

	// Route to appropriate API based on provider
	if c.provider == "anthropic" {
		return c.callAnthropic(messages)
	}
	return c.callOpenAI(messages)
}

// callOpenAI makes an HTTP request to the OpenAI API.
//
// API Details:
//   - Endpoint: POST https://api.openai.com/v1/chat/completions
//   - Model: gpt-4
//   - Authentication: Bearer token in Authorization header
//   - Content-Type: application/json
//
// Request Format:
//   {
//     "model": "gpt-4",
//     "messages": [
//       {"role": "system", "content": "..."},
//       {"role": "user", "content": "..."}
//     ]
//   }
//
// Response Format:
//   {
//     "choices": [
//       {
//         "message": {
//           "role": "assistant",
//           "content": "# AI-generated response..."
//         }
//       }
//     ]
//   }
//
// Parameters:
//   - messages: Complete messages array including system prompt and history
//
// Returns:
//   - string: The assistant's response content (from Choices[0].Message.Content)
//   - error: HTTP errors, JSON parsing errors, or API errors
//
// Error Handling:
//   - HTTP status != 200: Returns "API error: {response body}"
//   - Empty choices array: Returns "no response from API"
//   - Network errors: Returns underlying error
//
// Typical Response Time: 10-30 seconds
//
// Thread Safety: Safe to call concurrently. Creates new HTTP client per request.
func (c *Client) callOpenAI(messages []Message) (string, error) {
	// 1. Create request body
	reqBody := OpenAIRequest{
		Model:    c.model,
		Messages: messages,
	}

	// 2. Marshal to JSON
	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	// 3. Create HTTP request
	req, err := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	// 4. Set headers (OpenAI uses Bearer token)
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.apiKey)

	// 5. Send request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	// 6. Read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	// 7. Check HTTP status
	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API error: %s", string(body))
	}

	// 8. Parse JSON response
	var openAIResp OpenAIResponse
	if err := json.Unmarshal(body, &openAIResp); err != nil {
		return "", err
	}

	// 9. Validate response has content
	if len(openAIResp.Choices) == 0 {
		return "", fmt.Errorf("no response from API")
	}

	// 10. Extract and return assistant's response
	return openAIResp.Choices[0].Message.Content, nil
}

func (c *Client) callAnthropic(messages []Message) (string, error) {
	// Anthropic doesn't support system role in messages array
	var systemPrompt string
	filteredMessages := []Message{}

	for _, msg := range messages {
		if msg.Role == "system" {
			systemPrompt = msg.Content
		} else {
			filteredMessages = append(filteredMessages, msg)
		}
	}

	reqBody := map[string]interface{}{
		"model":      c.model,
		"max_tokens": 4096,
		"messages":   filteredMessages,
	}

	if systemPrompt != "" {
		reqBody["system"] = systemPrompt
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return "", err
	}

	req, err := http.NewRequest("POST", "https://api.anthropic.com/v1/messages", bytes.NewBuffer(jsonData))
	if err != nil {
		return "", err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", c.apiKey)
	req.Header.Set("anthropic-version", "2023-06-01")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", err
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API error: %s", string(body))
	}

	var anthropicResp AnthropicResponse
	if err := json.Unmarshal(body, &anthropicResp); err != nil {
		return "", err
	}

	if len(anthropicResp.Content) == 0 {
		return "", fmt.Errorf("no response from API")
	}

	return anthropicResp.Content[0].Text, nil
}

// mockResponse provides simulated responses when no API key is available
func (c *Client) mockResponse(prompt string) string {
	prompt = strings.ToLower(prompt)

	if strings.Contains(prompt, "research") {
		return fmt.Sprintf("# Research Findings\n\n" +
			"Based on comprehensive analysis:\n\n" +
			"## Key Points:\n" +
			"1. Current trends show significant growth in this area\n" +
			"2. Market analysis indicates strong demand\n" +
			"3. Technical feasibility is high\n\n" +
			"## Recommendations:\n" +
			"- Continue monitoring developments\n" +
			"- Consider strategic partnerships\n" +
			"- Invest in related technologies\n\n" +
			"*Note: This is a simulated response. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for real AI analysis.*")
	}

	if strings.Contains(prompt, "analyze") {
		return fmt.Sprintf("# Analysis Results\n\n" +
			"## Data Quality: High\n" +
			"## Key Patterns:\n" +
			"- Pattern A: Shows consistent growth\n" +
			"- Pattern B: Seasonal variations detected\n" +
			"- Pattern C: Strong correlation with market trends\n\n" +
			"## Insights:\n" +
			"The data suggests positive momentum with manageable risks.\n\n" +
			"*Note: This is a simulated response. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for real AI analysis.*")
	}

	if strings.Contains(prompt, "report") || strings.Contains(prompt, "summary") {
		return fmt.Sprintf("# Executive Report\n\n" +
			"## Overview\n" +
			"This report synthesizes findings from research and analysis phases.\n\n" +
			"## Key Findings:\n" +
			"- Finding 1: Market opportunity is substantial\n" +
			"- Finding 2: Technical approach is sound\n" +
			"- Finding 3: Timeline is achievable\n\n" +
			"## Recommendations:\n" +
			"1. Proceed with phase 2 planning\n" +
			"2. Allocate additional resources\n" +
			"3. Schedule stakeholder review\n\n" +
			"*Note: This is a simulated response. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for real AI analysis.*")
	}

	return fmt.Sprintf("Task completed successfully.\n\n" +
		"Analysis shows positive outcomes with actionable next steps identified.\n\n" +
		"*Note: This is a simulated response. Set OPENAI_API_KEY or ANTHROPIC_API_KEY for real AI-powered results.*")
}

// HasAPIKey returns true if an API key is configured
func (c *Client) HasAPIKey() bool {
	return c.apiKey != ""
}

// GetProvider returns the current provider
func (c *Client) GetProvider() string {
	if !c.HasAPIKey() {
		return "mock"
	}
	return c.provider
}