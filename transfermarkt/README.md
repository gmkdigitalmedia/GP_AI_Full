# ⚽ Football Player Value Analyzer

An AI-powered web application that analyzes football players' real market value using OpenAI, compares it with Transfermarkt values, and provides fantasy football scores.

## 🚀 Features

- **CSV Data Upload**: Paste Transfermarkt player data directly
- **AI Analysis**: Uses OpenAI to evaluate real player values
- **Value Comparison**: Visual charts comparing Transfermarkt vs AI estimates
- **Fantasy Football Scoring**: AI-generated fantasy potential scores (0-100)
- **Interactive Charts**: Real-time data visualization
- **Simple Go Backend**: No database required, runs on localhost:3000

## 📋 Quick Start

### 1. Setup Environment
```bash
cd transfermarkt
cp .env.example .env
# Add your OpenAI API key to .env file
```

### 2. Run the Application
```bash
go run main.go
```

Visit: http://localhost:3000

### 3. Upload Player Data
Copy and paste CSV data in this format:
```
rank,name,display_name,position,age,nationality,club,club_short,league,goals,assists,market_value
1,Bruno Michel,Bruno Michel,Left Winger,26,Brazil,FC Urartu Yerevan,FC Urartu,Armenia Premier League,6,7,€250k
```

## 🤖 How It Works

### AI Analysis Process
1. **Data Input**: Upload CSV with player stats and Transfermarkt values
2. **AI Evaluation**: OpenAI analyzes each player considering:
   - League quality and competitiveness
   - Age and career stage
   - Performance stats relative to position
   - Market trends for Brazilian players
   - Club prestige and league exposure
3. **Value Estimation**: AI provides realistic market value in euros
4. **Fantasy Scoring**: Generates 0-100 fantasy football potential score
5. **Visualization**: Interactive charts comparing values

### Fantasy Football Integration
The AI considers these factors for fantasy scoring:
- Goals and assists per game
- Position scarcity
- League competitiveness
- Age and consistency
- Injury risk assessment

## 📊 Features

### Web Interface
- Clean, responsive design
- Real-time analysis progress
- Interactive value comparison charts
- Fantasy score visualization
- Mobile-friendly layout

### Data Analysis
- **Value Comparison**: Side-by-side Transfermarkt vs AI estimates
- **Performance Metrics**: Goals, assists, age factors
- **League Analysis**: Quality assessment across different leagues
- **Market Trends**: Brazilian player market analysis

### Charts & Visualizations
- **Bar Chart**: Value comparison (Transfermarkt vs AI)
- **Doughnut Chart**: Fantasy score distribution
- **Responsive Design**: Works on all device sizes

## 🛠️ Technical Details

### Backend (Go)
- Lightweight HTTP server
- CSV parsing and validation
- OpenAI API integration
- Real-time analysis processing
- No database dependencies

### Frontend (HTML/CSS/JS)
- Vanilla JavaScript
- Chart.js for visualizations
- Responsive CSS Grid
- Form handling for CSV upload

### API Integration
- OpenAI GPT-3.5-turbo for analysis
- Structured JSON responses
- Rate limiting protection
- Error handling

## 🎯 Perfect for Students

### Learning Outcomes
1. **Web Development**: Go backend + HTML/CSS/JS frontend
2. **API Integration**: OpenAI API usage and JSON parsing
3. **Data Processing**: CSV parsing and data transformation
4. **Visualization**: Creating interactive charts
5. **Sports Analytics**: Understanding player valuation factors

### Project Extensions
- Add more leagues and players
- Implement player comparison features
- Create transfer prediction models
- Add historical value tracking
- Build fantasy league management

### Real-World Applications
- Sports analytics and scouting
- Fantasy football optimization
- Transfer market analysis
- Player development tracking

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Rate Limiting
- Analyzes max 5 players per request (to avoid API limits)
- 2-second delay between API calls
- Graceful error handling for failed analyses

## 🚀 Deployment

### Local Development
```bash
go run main.go
```

### Production Ready
```bash
go build -o transfermarkt main.go
./transfermarkt
```

## 📈 Sample Analysis Output

```json
{
  "estimated_value": "€1.2m",
  "analysis": "Player shows strong goal-scoring ability in a competitive league. Age factor and recent performance suggest higher value than Transfermarkt listing. Good potential for European move.",
  "fantasy_score": 78
}
```

## 🎮 Fantasy Football Usage

The AI generates fantasy scores based on:
- **Attacking Output**: Goals + assists per game
- **League Multiplier**: Stronger leagues = higher base scores
- **Position Scarcity**: Rare positions get bonus points
- **Age Factor**: Prime age players score higher
- **Consistency**: Regular playing time bonus

## 🔄 Workflow for Students

1. **Data Collection**: Find interesting player datasets
2. **Upload & Parse**: Use the web interface
3. **AI Analysis**: Let OpenAI evaluate each player
4. **Results Analysis**: Compare AI vs market values
5. **Fantasy Planning**: Use scores for team selection
6. **Extension Projects**: Add features and improvements

This project combines sports analytics, web development, and AI in an engaging, practical application perfect for student learning!