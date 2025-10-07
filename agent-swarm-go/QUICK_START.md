# Quick Start Guide

## Installation & Setup

### 1. Set up your API key (Optional but Recommended)

For **real AI-powered research**, set one of these environment variables:

```bash
# Option A: OpenAI (GPT-4)
export OPENAI_API_KEY="sk-your-key-here"

# Option B: Anthropic (Claude 3.5 Sonnet)
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

> **Without an API key?** No problem! The system will run in **DEMO MODE** with simulated intelligent responses.

### 2. Run the System

```bash
cd agent-swarm-go
go run cmd/main.go
```

You'll see:
```
✅ Connected to openai for AI-powered agent swarm

Initializing agent swarm...

🌐 Web Dashboard: http://localhost:8080
📊 Open the URL above in your browser for real-time monitoring!
```

### 3. Open the Web Dashboard

Open http://localhost:8080 in your browser to see:
- Real-time agent status
- Live event stream
- Task statistics
- Visual feedback with colors and animations

## Using the Interactive CLI

### Main Menu

```
╔═══════════════════════════════════════════════════════════╗
║         AGENT SWARM - Interactive Multi-Agent System      ║
║                       Go Implementation                    ║
╚═══════════════════════════════════════════════════════════╝

MAIN MENU - Select a Scenario
══════════════════════════════════════════════════════════════
1. Research & Analysis Workflow    ⭐ RECOMMENDED
   → AI agents research a topic and create a professional report

2. Parallel Task Processing
   → Distribute multiple tasks across all workers

3. Custom Task Creation
   → Build your own agent workflow

4. Swarm Status
   → View all agents and their current states

5. Broadcast Message
   → Send a message to all agents

6. View Agent Details
   → Inspect specific agent information

7. Run Stress Test
   → Test swarm capacity with many tasks

0. Quit
   → Shutdown the swarm
```

### Option 1: Research & Analysis (Recommended First Use)

This is where the magic happens! Let's research a topic:

```
Select an option: 1

=== Research & Analysis Workflow ===

This workflow will:
  1. Research your topic with comprehensive findings
  2. Analyze the research data for insights and patterns
  3. Generate a professional executive report

Enter research topic [quantum computing]: artificial intelligence
```

The system will:
1. **Research Agent** investigates your topic (10-20 seconds)
2. **Analysis Agent** processes the findings (10-20 seconds)
3. **Report Agent** creates a professional report (10-20 seconds)

You'll get a comprehensive report like this:

```
🔬 Starting Research Workflow for: artificial intelligence
================================================================

📚 Step 1/3: Research Phase
[19:45:12] 📥 Researcher researcher-1 received task: Research the topic...
[19:45:25] ✅ Researcher researcher-1 completed: research-1234567890
✅ Research completed

📊 Step 2/3: Analysis Phase
[19:45:26] 📥 Analyzer analyzer-1 received task: Analyze the research...
[19:45:38] ✅ Analyzer analyzer-1 completed: analyze-1234567891
✅ Analysis completed

📝 Step 3/3: Report Generation Phase
[19:45:39] 📥 Reporter reporter-1 received task: Generate a comprehensive...
[19:45:52] ✅ Reporter reporter-1 completed: report-1234567892
✅ Report generated

🎉 Workflow completed in 45.2s

======================================================================
📚 RESEARCH FINDINGS
======================================================================
[AI-generated comprehensive research findings about your topic]

======================================================================
📊 ANALYSIS INSIGHTS
======================================================================
[AI-generated analysis with patterns and insights]

======================================================================
📝 FINAL REPORT
======================================================================
[Professional executive report synthesizing everything]
```

## Real-World Examples

### Example 1: Market Research

```
Topic: electric vehicle market trends 2025

Result: Comprehensive research on EV adoption rates, key players,
technological advances, market forecasts, and strategic recommendations.
```

### Example 2: Technology Analysis

```
Topic: blockchain scalability solutions

Result: Technical research on Layer 2 solutions, sharding, analysis
of trade-offs, and recommendations for different use cases.
```

### Example 3: Business Strategy

```
Topic: remote work productivity tools

Result: Research on available tools, analysis of effectiveness,
comparison of features, and recommendations for implementation.
```

## Monitoring in Real-Time

### Web Dashboard (http://localhost:8080)

Watch your agents work in real-time:

- **Agent Cards** turn orange when processing, green when idle
- **Event Stream** shows every action: task received, started, completed
- **Statistics** update live: tasks completed, agents active
- **Color Coding**:
  - 🔵 Blue: Task received
  - 🟠 Orange: Task started
  - 🟢 Green: Task completed
  - 🔴 Red: Task failed

### CLI Output

The terminal shows:
```
[19:45:12] 📥 Researcher researcher-1 received task: Research...
[19:45:12] ⚙️  Researcher researcher-1 started research-001
[19:45:25] ✅ Researcher researcher-1 completed research-001
```

## Tips for Best Results

### 1. Be Specific with Topics

❌ **Too vague**: "technology"
✅ **Better**: "quantum computing applications in cryptography"

❌ **Too vague**: "business"
✅ **Better**: "SaaS pricing strategies for B2B startups"

### 2. Use Demo Mode to Test

Without an API key, the system provides realistic demo responses so you can:
- Test the workflow
- See the agent coordination
- Understand the output format
- Verify everything works

Then add your API key for real AI-powered results.

### 3. Watch the Web Dashboard

Open http://localhost:8080 while running workflows to see:
- How agents coordinate
- Real-time task distribution
- Event sequencing
- System health

## Troubleshooting

### "No API key" Warning

```
⚠️  WARNING: No API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)
   Agents will run in DEMO MODE with simulated responses
```

**Solution**: Set an API key (see step 1) or continue in demo mode.

### Port 8080 Already in Use

```
Web server error: listen tcp :8080: bind: address already in use
```

**Solution**: Stop other services using port 8080 or modify the port in `cmd/main.go`.

### Slow Responses

- **With API key**: Normal (10-20 seconds per agent)
- **Without API key**: Should be instant (~1 second per agent)

If slow without API key, check system resources.

## Next Steps

1. ✅ Try the Research & Analysis workflow
2. ✅ Watch the web dashboard while it runs
3. ✅ Experiment with different topics
4. ✅ Try option 2 for parallel processing
5. ✅ Build custom workflows with option 3

## Getting Help

- Check the main [README.md](README.md) for full documentation
- Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand how it works
- Look at agent implementations in `pkg/agents/` for examples

---

**Ready to go? Run `go run cmd/main.go` and select option 1!** 🚀