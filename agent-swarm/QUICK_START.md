# 🚀 Quick Start Guide - GP Agent Swarm

Get your AI agent swarm running in under 5 minutes!

## ⚡ One-Command Setup

```bash
python3 setup.py
```

That's it! The setup script will:
- ✅ Install all dependencies
- ✅ Verify your .env file and API key
- ✅ Test agent loading
- ✅ Test OpenAI API connectivity

## 🎮 Try It Out

### Option 1: Interactive Demo
```bash
python3 demo.py
```

Choose from 8 different demo scenarios:
1. **Research Report** - Research → Write → Review pipeline
2. **Product Launch Plan** - Creative → Coordinate → Analyze
3. **Content Marketing** - Research → Creative → Write
4. **Business Analysis** - Analyze → Coordinate → Review
5. **Innovation Workshop** - Creative → Research → Write
6. **Quality Audit** - All agents working together
7. **Custom Workflow** - Build your own agent workflow
8. **Agent Status** - View current agent status

### Option 2: Web Interface
```bash
python3 run_web.py
```

Then open http://localhost:5000 in your browser to see:
- 🔴 Real-time agent visualization
- 📊 Live task progress
- 🤖 Agent status dashboard
- 📈 Result analytics

## 🎯 What You Get

### 6 Pre-Built Agent Types
- **Researcher** - Information gathering and analysis
- **Writer** - Content creation and communication
- **Analyzer** - Data analysis and pattern recognition
- **Coordinator** - Project management and workflow planning
- **Reviewer** - Quality assurance and improvement
- **Creative** - Innovation and creative problem-solving

### No-Code Agent Creation
Create new agents by editing simple YAML files in the `configs/` directory. No Python coding required!

### Real-Time Collaboration
Watch agents work together in coordinated workflows, passing information and building on each other's outputs.

## 🛠️ Manual Setup (if needed)

If the automatic setup doesn't work:

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API Key**
   ```bash
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

3. **Test the System**
   ```bash
   python3 -c "
   from swarm_orchestrator import SwarmOrchestrator
   import asyncio

   async def test():
       orchestrator = SwarmOrchestrator()
       await orchestrator.load_agents_from_config('configs')
       print(f'✅ Loaded {len(orchestrator.agents)} agents!')

   asyncio.run(test())
   "
   ```

## 🎨 Example: Create Your First Custom Workflow

```python
from swarm_orchestrator import SwarmOrchestrator
from agent_base import TaskConfig

# Initialize the swarm
orchestrator = SwarmOrchestrator()
await orchestrator.load_agents_from_config('configs')

# Create a custom task
task = TaskConfig(
    name="Market Analysis Report",
    description="Analyze the AI tools market and create a report",
    assigned_agents=["research_specialist", "data_analyzer", "content_writer"],
    workflow=[
        {"agent": "research_specialist", "description": "Research AI tools market",
         "instruction": "Research current AI tools market trends and competitors"},
        {"agent": "data_analyzer", "description": "Analyze market data",
         "instruction": "Analyze the research data for patterns and opportunities"},
        {"agent": "content_writer", "description": "Write market report",
         "instruction": "Create a professional market analysis report"}
    ],
    expected_output="Comprehensive market analysis report"
)

# Execute the task
results = await orchestrator.execute_task(task)
```

## 🎪 Demo Scenarios You Can Try

1. **"Research quantum computing trends"** → Research Report
2. **"Launch an AI-powered fitness app"** → Product Launch Plan
3. **"Create content for a SaaS startup"** → Content Marketing
4. **"Analyze customer churn data"** → Business Analysis
5. **"Brainstorm office productivity solutions"** → Innovation Workshop

## 🚨 Troubleshooting

**"No agents loaded" error:**
- Check that `configs/` directory exists
- Verify YAML files are valid
- Make sure agent roles match available types

**API errors:**
- Verify OpenAI API key in `.env` file
- Check internet connection
- Monitor API usage limits

**Import errors:**
- Run `pip install -r requirements.txt`
- Make sure you're in the correct directory

## 🎯 What's Next?

- Explore the web interface at http://localhost:5000
- Create custom agents by editing YAML files in `configs/`
- Build your own workflows for your specific use cases
- Check the full README.md for advanced features

## 🤝 Support

Having issues? The system is designed to be user-friendly for you and your customers!

1. Run the setup script: `python3 setup.py`
2. Check this guide
3. Review the error messages - they're designed to be helpful
4. Try the web interface for a visual experience

**Happy swarming! 🤖✨**