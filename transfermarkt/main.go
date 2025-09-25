/*
Football Player Value Analyzer - AI-powered market valuation tool

This application analyzes football player market values using OpenAI's GPT model
and compares them with Transfermarkt valuations. It includes a goals-per-match
multiplier system and fantasy football scoring.

Key Features:
- CSV data upload and parsing
- Real-time AI analysis with progress tracking
- Value comparison charts and visualizations
- Goals-per-match based value adjustments
- Fantasy football potential scoring

Technical Stack:
- Backend: Go (Golang) with standard library HTTP server
- Frontend: HTML/CSS/JavaScript with Chart.js
- AI: OpenAI GPT-3.5-turbo API
- Data: CSV parsing, no database required
*/

package main

import (
	"bytes"
	"encoding/csv"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"
)

// Player represents a football player with their stats and valuations
// JSON tags enable easy API responses and client-side JavaScript processing
type Player struct {
	Rank         int     `json:"rank"`         // Player's rank in the dataset (1-25)
	Name         string  `json:"name"`         // Full player name
	DisplayName  string  `json:"display_name"` // Display name (often same as Name)
	Position     string  `json:"position"`     // Playing position (Centre-Forward, Left Winger, etc.)
	Age          int     `json:"age"`          // Player's current age
	Nationality  string  `json:"nationality"`  // Player's nationality (all Brazilian in our dataset)
	Club         string  `json:"club"`         // Current club (full name)
	ClubShort    string  `json:"club_short"`   // Abbreviated club name for display
	League       string  `json:"league"`       // League name (varies in quality/prestige)
	Matches      int     `json:"matches"`      // Number of matches played this season
	Goals        int     `json:"goals"`        // Goals scored this season
	MarketValue  string  `json:"market_value"` // Transfermarkt's valuation (€250k, €2.00m, etc.)

	// AI-generated fields (populated after analysis)
	AIValue      string  `json:"ai_value,omitempty"`      // AI's estimated market value
	AIAnalysis   string  `json:"ai_analysis,omitempty"`   // AI's reasoning and analysis
	FantasyScore float64 `json:"fantasy_score,omitempty"` // Fantasy football potential (0-100)
}

// OpenAI API request structure
// These structs match OpenAI's expected JSON format for chat completions
type OpenAIRequest struct {
	Model    string    `json:"model"`    // AI model to use (gpt-3.5-turbo)
	Messages []Message `json:"messages"` // Conversation messages
}

type Message struct {
	Role    string `json:"role"`    // "user" or "assistant"
	Content string `json:"content"` // The actual message content
}

// OpenAI API response structure
type OpenAIResponse struct {
	Choices []Choice `json:"choices"` // AI can return multiple response options
}

type Choice struct {
	Message Message `json:"message"` // The AI's response message
}

// Global variables for application state
// In a production app, you'd use proper state management or database
var players []Player        // All loaded players from CSV
var analysisResults []Player // Players with completed AI analysis

// Real-time progress tracking for the analysis process
// This allows the web interface to show live updates
var analysisProgress struct {
	Current    int    `json:"current"`     // Current player being analyzed (1, 2, 3...)
	Total      int    `json:"total"`       // Total number of players to analyze
	Status     string `json:"status"`      // Human-readable status message
	PlayerName string `json:"player_name"` // Name of current player being analyzed
	Done       bool   `json:"done"`        // Whether analysis is complete
}

// Main function - application entry point
func main() {
	// Load the initial dataset of 25 Brazilian players
	loadPlayersFromCSV()

	// Set up HTTP routes
	// Go's built-in HTTP multiplexer handles routing
	http.HandleFunc("/", homeHandler)           // Main page with player data and upload form
	http.HandleFunc("/upload", uploadHandler)   // Handles CSV data uploads
	http.HandleFunc("/analyze", analyzeHandler) // Starts AI analysis (runs in background)
	http.HandleFunc("/progress", progressHandler) // JSON API for real-time progress updates
	http.HandleFunc("/results", resultsHandler) // Shows analysis results with charts
	http.HandleFunc("/static/", staticHandler)  // Serves static files (if any)

	// Start the web server
	// Using port 3001 to avoid conflicts with other common development servers
	fmt.Println("Server starting on :3001")
	fmt.Println("Visit: http://localhost:3001")
	log.Fatal(http.ListenAndServe(":3001", nil)) // log.Fatal ensures we see any startup errors
}

// loadPlayersFromCSV reads the initial dataset from players.csv
// This demonstrates CSV parsing - a common data ingestion pattern
func loadPlayersFromCSV() {
	// Open the CSV file - players.csv should be in the same directory as main.go
	file, err := os.Open("players.csv")
	if err != nil {
		// Graceful error handling - app continues without initial data
		log.Printf("Warning: Could not load players.csv: %v", err)
		return
	}
	defer file.Close() // Ensure file is closed when function ends

	// Go's built-in CSV reader handles parsing, escaping, and edge cases
	reader := csv.NewReader(file)
	records, err := reader.ReadAll() // Read entire file into memory
	if err != nil {
		log.Printf("Error reading CSV: %v", err)
		return
	}

	// Process each row of CSV data
	for i, record := range records {
		if i == 0 { // Skip header row
			continue
		}

		// Convert string values to appropriate types
		// strconv.Atoi returns 0 if conversion fails (graceful handling)
		rank, _ := strconv.Atoi(record[0])
		age, _ := strconv.Atoi(record[4])
		matches, _ := strconv.Atoi(record[9])  // Number of matches played
		goals, _ := strconv.Atoi(record[10])   // Goals scored

		// Create Player struct from CSV row
		// This mapping assumes specific column order - fragile but simple
		player := Player{
			Rank:        rank,          // 1-25 in our dataset
			Name:        record[1],     // Full name
			DisplayName: record[2],     // Display name (usually same as Name)
			Position:    record[3],     // Playing position
			Age:         age,           // Current age
			Nationality: record[5],     // All Brazilian in our dataset
			Club:        record[6],     // Current club
			ClubShort:   record[7],     // Abbreviated club name
			League:      record[8],     // League they play in
			Matches:     matches,       // Matches played this season
			Goals:       goals,         // Goals scored this season
			MarketValue: record[11],    // Transfermarkt's valuation (€250k, €2.00m, etc.)
		}
		players = append(players, player)
	}
	fmt.Printf("Loaded %d players from CSV\n", len(players))
}

func parseCSVData(csvData string) ([]Player, error) {
	reader := csv.NewReader(strings.NewReader(csvData))
	records, err := reader.ReadAll()
	if err != nil {
		return nil, err
	}

	var parsedPlayers []Player
	for i, record := range records {
		if i == 0 || len(record) < 12 { // Skip header or incomplete records
			continue
		}

		rank, _ := strconv.Atoi(record[0])
		age, _ := strconv.Atoi(record[4])
		matches, _ := strconv.Atoi(record[9])
		goals, _ := strconv.Atoi(record[10])

		player := Player{
			Rank:        rank,
			Name:        record[1],
			DisplayName: record[2],
			Position:    record[3],
			Age:         age,
			Nationality: record[5],
			Club:        record[6],
			ClubShort:   record[7],
			League:      record[8],
			Matches:     matches,
			Goals:       goals,
			MarketValue: record[11],
		}
		parsedPlayers = append(parsedPlayers, player)
	}
	return parsedPlayers, nil
}

// analyzePlayerWithAI sends player data to OpenAI for market valuation analysis
// This is the core AI integration that evaluates player worth beyond simple stats
func analyzePlayerWithAI(player Player) (Player, error) {
	// API Key Management - Multiple sources for flexibility
	// Priority: .env file -> environment variable
	// This allows both local development and production deployment
	envData, err := os.ReadFile(".env")
	apiKey := ""
	if err == nil {
		lines := strings.Split(string(envData), "\n")
		for _, line := range lines {
			if strings.HasPrefix(line, "OPENAI_API_KEY=") {
				apiKey = strings.TrimPrefix(line, "OPENAI_API_KEY=")
				apiKey = strings.TrimSpace(apiKey)
				break
			}
		}
	}

	// Fallback to system environment variable (useful for production)
	if apiKey == "" {
		apiKey = os.Getenv("OPENAI_API_KEY")
	}

	if apiKey == "" {
		return player, fmt.Errorf("OPENAI_API_KEY not set in .env file or environment")
	}

	// Construct the AI prompt with comprehensive player analysis criteria
	// This prompt engineering is crucial - it guides the AI's evaluation process
	prompt := fmt.Sprintf(`Analyze this football player's real market value:

Player: %s (%s)
Position: %s
Age: %d
League: %s (%s)
Stats: %d goals in %d matches (%.2f per match)
Current Transfermarkt Value: %s

Consider these factors:
1. League quality/competitiveness (Armenia vs Portugal vs Qatar leagues vary greatly)
2. Age and career stage (peak years 24-28, declining after 30)
3. Performance stats relative to position (goals per match is key for forwards)
4. Market trends for Brazilian players (technical skill premium)
5. Club prestige and league exposure (affects transfer opportunities)

Provide:
1. Estimated real market value in euros (format: €X.XXm or €XXXk)
2. Brief analysis (max 100 words explaining your reasoning)
3. Fantasy football potential score (0-100, considering consistency, position scarcity, age)

IMPORTANT: Fantasy scoring criteria (be transparent about this):
- Goals/assists output: 40%% weight
- League competitiveness: 20%% weight
- Age factor: 20%% weight (25-29 = peak, 30+ = declining)
- Position scarcity: 10%% weight (strikers score higher than midfielders)
- Consistency/injury risk: 10%% weight

Format your response as JSON:
{
  "estimated_value": "€X.XXm",
  "analysis": "your analysis here",
  "fantasy_score": 85
}`, player.DisplayName, player.Name, player.Position, player.Age, player.League, player.Club, player.Goals, player.Matches, float64(player.Goals)/float64(player.Matches), player.MarketValue)

	reqBody := OpenAIRequest{
		Model: "gpt-3.5-turbo",
		Messages: []Message{
			{Role: "user", Content: prompt},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return player, err
	}

	req, err := http.NewRequest("POST", "https://api.openai.com/v1/chat/completions", bytes.NewBuffer(jsonData))
	if err != nil {
		return player, err
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+apiKey)

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return player, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return player, err
	}

	var openAIResp OpenAIResponse
	if err := json.Unmarshal(body, &openAIResp); err != nil {
		return player, err
	}

	if len(openAIResp.Choices) == 0 {
		return player, fmt.Errorf("no response from OpenAI")
	}

	// Parse the JSON response from AI
	var aiResult struct {
		EstimatedValue string  `json:"estimated_value"`
		Analysis       string  `json:"analysis"`
		FantasyScore   float64 `json:"fantasy_score"`
	}

	content := openAIResp.Choices[0].Message.Content
	if err := json.Unmarshal([]byte(content), &aiResult); err != nil {
		// If JSON parsing fails, use the raw content
		player.AIValue = "Analysis failed"
		player.AIAnalysis = content
		player.FantasyScore = 50.0
	} else {
		player.AIValue = aiResult.EstimatedValue
		player.AIAnalysis = aiResult.Analysis
		player.FantasyScore = aiResult.FantasyScore

		// CUSTOM VALUATION BOOST SYSTEM
		// This is our own proprietary scoring system that rewards high goal-scorers
		// Rationale: Goals per match is the most reliable predictor of striker value
		if player.Matches > 0 {
			goalsPerMatch := float64(player.Goals) / float64(player.Matches)

			// HARDCODED THRESHOLDS (you can adjust these):
			if goalsPerMatch > 0.9 {
				// DOUBLE VALUE: >0.9 goals/match indicates exceptional talent
				// Examples: Jonathan Júnior (10 goals in 6 matches = 1.67 goals/match)
				// This catches potential superstars in smaller leagues
				player.AIValue = adjustMarketValue(player.AIValue, 2.0)
				player.AIAnalysis += fmt.Sprintf(" [BOOST: Exceptional striker with %.2f goals/match - value doubled!]", goalsPerMatch)
			} else if goalsPerMatch > 0.7 {
				// 50% INCREASE: >0.7 goals/match shows strong consistent performance
				// This rewards players who consistently find the net
				player.AIValue = adjustMarketValue(player.AIValue, 1.5)
				player.AIAnalysis += fmt.Sprintf(" [BOOST: Strong striker with %.2f goals/match - value increased 50%%]", goalsPerMatch)
			}
			// Players with ≤0.7 goals/match get no boost (AI analysis only)
		}
	}

	return player, nil
}

// adjustMarketValue applies multipliers to currency strings (€500k, €2.00m, etc.)
// This handles the complex conversion between different currency formats
// LEARNING NOTE: String manipulation and floating point math in Go
func adjustMarketValue(currentValue string, multiplier float64) string {
	// Remove the Euro symbol and clean whitespace
	// Example: "€1.50m" becomes "1.50m"
	value := strings.Replace(currentValue, "€", "", -1)
	value = strings.TrimSpace(value)

	var numValueInK float64 // Normalize everything to thousands for calculation

	// Handle different suffixes (k = thousands, m = millions)
	if strings.HasSuffix(value, "m") {
		// "1.50m" -> 1.50 -> 1500k
		numValue, _ := strconv.ParseFloat(strings.Replace(value, "m", "", -1), 64)
		numValueInK = numValue * 1000 // Convert millions to thousands
	} else if strings.HasSuffix(value, "k") {
		// "500k" -> 500k (already in thousands)
		numValueInK, _ = strconv.ParseFloat(strings.Replace(value, "k", "", -1), 64)
	} else {
		// Pure number without suffix - assume thousands
		// This handles edge cases where AI returns just "500" instead of "€500k"
		numValueInK, _ = strconv.ParseFloat(value, 64)
	}

	// Apply the multiplier (1.5x for good, 2.0x for exceptional)
	adjustedValueInK := numValueInK * multiplier

	// Convert back to readable format with proper units
	if adjustedValueInK >= 1000 {
		// 1000k+ becomes millions: "1500k" -> "€1.50m"
		return fmt.Sprintf("€%.2fm", adjustedValueInK/1000)
	} else {
		// Under 1000k stays in thousands: "750k" -> "€750k"
		return fmt.Sprintf("€%.0fk", adjustedValueInK)
	}
}

func homeHandler(w http.ResponseWriter, r *http.Request) {
	tmpl := `
<!DOCTYPE html>
<html>
<head>
    <title>Football Player Value Analyzer</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #2c3e50; text-align: center; }
        .upload-section { background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }
        textarea { width: 100%; height: 200px; padding: 10px; }
        button { background: #3498db; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #2980b9; }
        .players-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .player-card { border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: #fafafa; }
        .stats { display: flex; justify-content: space-between; margin: 10px 0; }
        .value { font-weight: bold; color: #27ae60; }
        .nav { text-align: center; margin: 20px 0; }
        .nav a { margin: 0 10px; text-decoration: none; color: #3498db; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Football Player Value Analyzer</h1>
        <div class="nav">
            <a href="/">Home</a> |
            <a href="/results">Analysis Results</a>
        </div>

        <div class="upload-section">
            <h2>Upload Player Data</h2>
            <p>Paste CSV data in format: rank,name,display_name,position,age,nationality,club,club_short,league,goals,assists,market_value</p>
            <form action="/upload" method="post">
                <textarea name="csvdata" placeholder="Paste your CSV data here..."></textarea><br><br>
                <button type="submit">Upload & Parse Data</button>
            </form>
        </div>

        {{if .Players}}
        <h2>Current Player Database ({{len .Players}} players)</h2>
        <form onsubmit="startAnalysis(event)">
            <button type="submit" style="background: #e74c3c;">Analyze All Players with AI</button>
        </form>

        <div id="progress-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); z-index: 1000;">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 10px; text-align: center;">
                <h2>AI Analysis in Progress</h2>
                <div id="progress-bar" style="width: 300px; height: 20px; background: #f0f0f0; border-radius: 10px; margin: 20px 0;">
                    <div id="progress-fill" style="height: 100%; background: #3498db; border-radius: 10px; width: 0%; transition: width 0.5s;"></div>
                </div>
                <div id="progress-status">Starting analysis...</div>
                <div id="current-player" style="margin-top: 10px; font-weight: bold; color: #2c3e50;"></div>
                <div style="margin-top: 20px;">
                    <div style="display: inline-block; width: 20px; height: 20px; border: 3px solid #3498db; border-top: 3px solid transparent; border-radius: 50%; animation: spin 1s linear infinite;"></div>
                </div>
            </div>
        </div>

        <script>
        function startAnalysis(event) {
            event.preventDefault();
            document.getElementById('progress-modal').style.display = 'block';

            // Start the analysis
            fetch('/analyze', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started') {
                    updateProgress();
                }
            })
            .catch(err => {
                console.error('Error starting analysis:', err);
                alert('Failed to start analysis');
                document.getElementById('progress-modal').style.display = 'none';
            });
        }

        function updateProgress() {
            fetch('/progress')
                .then(response => response.json())
                .then(data => {
                    const progressPercent = (data.current / data.total) * 100;
                    document.getElementById('progress-fill').style.width = progressPercent + '%';
                    document.getElementById('progress-status').textContent = data.status;
                    document.getElementById('current-player').textContent = data.player_name ? 'Analyzing: ' + data.player_name : '';

                    if (!data.done) {
                        setTimeout(updateProgress, 1000); // Update every second
                    } else {
                        setTimeout(() => {
                            window.location.href = '/results';
                        }, 2000); // Wait 2 seconds then redirect
                    }
                })
                .catch(err => {
                    console.error('Error fetching progress:', err);
                    setTimeout(updateProgress, 2000); // Retry after 2 seconds
                });
        }
        </script>

        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        </style>

        <div class="players-grid">
            {{range .Players}}
            <div class="player-card">
                <h3>{{.DisplayName}}</h3>
                <p><strong>Position:</strong> {{.Position}} | <strong>Age:</strong> {{.Age}}</p>
                <p><strong>Club:</strong> {{.Club}}</p>
                <p><strong>League:</strong> {{.League}}</p>
                <div class="stats">
                    <span>{{.Goals}} goals in {{.Matches}} matches</span>
                    {{if gt .Matches 0}}<span>{{printf "%.2f" (div .Goals .Matches)}} goals/match</span>{{end}}
                </div>
                <div class="value">Market Value: {{.MarketValue}}</div>
            </div>
            {{end}}
        </div>
        {{else}}
        <p>No players loaded. Upload CSV data to get started!</p>
        {{end}}
    </div>
</body>
</html>`

	funcMap := template.FuncMap{
		"div": func(a, b int) float64 {
			if b == 0 {
				return 0
			}
			return float64(a) / float64(b)
		},
	}

	t, err := template.New("home").Funcs(funcMap).Parse(tmpl)
	if err != nil {
		http.Error(w, "Template error: "+err.Error(), http.StatusInternalServerError)
		return
	}

	data := struct {
		Players []Player
	}{
		Players: players,
	}

	err = t.Execute(w, data)
	if err != nil {
		http.Error(w, "Template execution error: "+err.Error(), http.StatusInternalServerError)
		return
	}
}

func uploadHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	csvData := r.FormValue("csvdata")
	if csvData == "" {
		http.Error(w, "No CSV data provided", http.StatusBadRequest)
		return
	}

	parsedPlayers, err := parseCSVData(csvData)
	if err != nil {
		http.Error(w, "Error parsing CSV data: "+err.Error(), http.StatusBadRequest)
		return
	}

	players = parsedPlayers
	fmt.Printf("Uploaded %d players\n", len(players))

	http.Redirect(w, r, "/", http.StatusSeeOther)
}

func analyzeHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Redirect(w, r, "/", http.StatusSeeOther)
		return
	}

	if len(players) == 0 {
		http.Error(w, "No players to analyze", http.StatusBadRequest)
		return
	}

	// Start analysis in background
	go func() {
		analysisResults = []Player{}

		// Analyze all players
		maxAnalyze := len(players)

		// Initialize progress
		analysisProgress.Current = 0
		analysisProgress.Total = maxAnalyze
		analysisProgress.Status = "Starting analysis..."
		analysisProgress.Done = false

		for i := 0; i < maxAnalyze; i++ {
			// Update progress
			analysisProgress.Current = i + 1
			analysisProgress.PlayerName = players[i].DisplayName
			analysisProgress.Status = fmt.Sprintf("Analyzing player %d of %d", i+1, maxAnalyze)

			fmt.Printf("Analyzing player %d/%d: %s\n", i+1, maxAnalyze, players[i].DisplayName)
			analyzed, err := analyzePlayerWithAI(players[i])
			if err != nil {
				fmt.Printf("Error analyzing %s: %v\n", players[i].DisplayName, err)
				analyzed.AIValue = "Analysis failed"
				analyzed.AIAnalysis = err.Error()
				analyzed.FantasyScore = 0
			}
			analysisResults = append(analysisResults, analyzed)

			// Add delay to avoid rate limiting
			time.Sleep(2 * time.Second)
		}

		// Mark as done
		analysisProgress.Done = true
		analysisProgress.Status = "Analysis complete!"
	}()

	// Return immediately
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{"status": "started"})
}

func progressHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(analysisProgress)
}

func resultsHandler(w http.ResponseWriter, r *http.Request) {
	tmpl := `
<!DOCTYPE html>
<html>
<head>
    <title>Analysis Results</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        h1 { color: #2c3e50; text-align: center; }
        .nav { text-align: center; margin: 20px 0; }
        .nav a { margin: 0 10px; text-decoration: none; color: #3498db; }
        .analysis-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; }
        .player-analysis { border: 1px solid #ddd; padding: 20px; border-radius: 10px; background: #fafafa; }
        .value-comparison { display: flex; justify-content: space-between; margin: 15px 0; padding: 10px; background: #ecf0f1; border-radius: 5px; }
        .original-value { color: #e74c3c; }
        .ai-value { color: #27ae60; }
        .analysis-text { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .fantasy-score { text-align: center; font-size: 24px; font-weight: bold; color: #8e44ad; }
        .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 30px 0; }
        canvas { max-height: 400px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Analysis Results</h1>
        <div class="nav">
            <a href="/">Home</a> |
            <a href="/results">Analysis Results</a>
        </div>

        {{if .Results}}
        <div class="charts">
            <div>
                <h3>Value Comparison Chart</h3>
                <canvas id="valueChart"></canvas>
            </div>
            <div>
                <h3>Fantasy Score Distribution</h3>
                <canvas id="fantasyChart"></canvas>
            </div>
        </div>

        <div class="analysis-grid">
            {{range .Results}}
            <div class="player-analysis">
                <h3>{{.DisplayName}} ({{.Position}})</h3>
                <p><strong>Age:</strong> {{.Age}} | <strong>Club:</strong> {{.ClubShort}} | <strong>Stats:</strong> {{.Goals}}G in {{.Matches}}M</p>

                <div class="value-comparison">
                    <div>
                        <div class="original-value">Transfermarkt: {{.MarketValue}}</div>
                        <div class="ai-value">AI Estimate: {{.AIValue}}</div>
                    </div>
                </div>

                <div class="fantasy-score">Fantasy Score: {{printf "%.0f" .FantasyScore}}/100</div>

                <div class="analysis-text">
                    <strong>AI Analysis:</strong><br>
                    {{.AIAnalysis}}
                </div>
            </div>
            {{end}}
        </div>

        <script>
        // Value Comparison Chart
        const players = {{.ResultsJSON}};
        const playerNames = players.map(p => p.display_name.split(' ')[0]);
        const originalValues = players.map(p => {
            const val = p.market_value.replace(/[€kmKM-]/g, '');
            if (p.market_value.includes('m')) return parseFloat(val) * 1000;
            return parseFloat(val) || 0;
        });
        const aiValues = players.map(p => {
            const val = p.ai_value.replace(/[€kmKM-]/g, '');
            if (p.ai_value.includes('m')) return parseFloat(val) * 1000;
            return parseFloat(val) || 0;
        });

        new Chart(document.getElementById('valueChart'), {
            type: 'bar',
            data: {
                labels: playerNames,
                datasets: [{
                    label: 'Transfermarkt Value (k€)',
                    data: originalValues,
                    backgroundColor: '#e74c3c'
                }, {
                    label: 'AI Estimated Value (k€)',
                    data: aiValues,
                    backgroundColor: '#27ae60'
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });

        // Fantasy Score Chart
        const fantasyScores = players.map(p => p.fantasy_score);
        new Chart(document.getElementById('fantasyChart'), {
            type: 'doughnut',
            data: {
                labels: playerNames,
                datasets: [{
                    data: fantasyScores,
                    backgroundColor: [
                        '#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6'
                    ]
                }]
            },
            options: {
                responsive: true
            }
        });
        </script>

        {{else}}
        <p>No analysis results available. <a href="/">Go back</a> and run the analysis first.</p>
        {{end}}
    </div>
</body>
</html>`

	t, err := template.New("results").Parse(tmpl)
	if err != nil {
		http.Error(w, "Template error: "+err.Error(), http.StatusInternalServerError)
		return
	}

	resultsJSON, _ := json.Marshal(analysisResults)

	data := struct {
		Results     []Player
		ResultsJSON template.JS
	}{
		Results:     analysisResults,
		ResultsJSON: template.JS(resultsJSON),
	}
	err = t.Execute(w, data)
	if err != nil {
		http.Error(w, "Template execution error: "+err.Error(), http.StatusInternalServerError)
		return
	}
}

func staticHandler(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, r.URL.Path[1:])
}