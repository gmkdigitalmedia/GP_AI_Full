# No-Code Agent Swarm System

A powerful system for creating and coordinating multiple AI agents that work together on complex tasks - **no Python coding required!**

## What Makes This Special

**True No-Code Agent Creation:** Create new AI agents by simply editing YAML configuration files. No programming experience needed!

**6 Pre-Built Agent Types:**
- **Researcher** - Information gathering and analysis
- **Writer** - Content creation and communication
- **Analyzer** - Data analysis and pattern recognition
- **Coordinator** - Project management and workflow planning
- **Reviewer** - Quality assurance and improvement
- **Creative** - Innovation and creative problem-solving

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up OpenAI API
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run the Interactive Demo
```bash
python demo.py
```

## How It Works

### No-Code Agent Creation
Create new agents by editing simple YAML files:

```yaml
# configs/my_agent.yaml
name: "marketing_specialist"
role: "writer"
system_prompt: |
  You are a marketing specialist focused on creating compelling
  campaigns that drive engagement and conversions.
model: "gpt-4o-mini"
temperature: 0.7
skills:
  - "campaign_creation"
  - "audience_targeting"
  - "conversion_optimization"
```

### Agent Swarm Workflows
Agents work together in coordinated workflows:

```
Research Task → Researcher Agent → Analysis → Analyzer Agent → Report → Writer Agent → Review → Reviewer Agent
```

### Real-Time Collaboration
Watch agents collaborate in real-time:
- Each agent receives context from previous agents
- Results are automatically passed between workflow steps
- All interactions are logged and saved

## Demo Scenarios

### 1. Research Report Pipeline
- **Researcher** gathers comprehensive information
- **Writer** creates professional report
- **Reviewer** polishes and improves quality

### 2. Product Launch Planning
- **Creative** generates innovative launch ideas
- **Coordinator** creates detailed project plan
- **Analyzer** evaluates market potential

### 3. Content Marketing Creation
- **Researcher** analyzes target audience and trends
- **Creative** develops content strategy and angles
- **Writer** produces engaging marketing content

### 4. Parallel Brainstorming
- Multiple agents work simultaneously on the same problem
- Each provides unique perspective based on their role
- Results are aggregated for comprehensive solutions

### 5. Quality Audit Process
- **Researcher** gathers quality standards
- **Analyzer** identifies patterns and issues
- **Reviewer** provides comprehensive assessment

## File Structure

```
agent-swarm/
├── agent_base.py              # Core agent framework
├── agent_types.py             # Specialized agent implementations
├── swarm_orchestrator.py      # Workflow coordination
├── demo.py                    # Interactive demonstration
├── configs/                   # No-code agent configurations
│   ├── researcher_agent.yaml
│   ├── writer_agent.yaml
│   ├── analyzer_agent.yaml
│   ├── creative_agent.yaml
│   ├── reviewer_agent.yaml
│   └── coordinator_agent.yaml
├── outputs/                   # Generated results (auto-created)
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## Creating Custom Agents

### Step 1: Choose Agent Type
Select from available roles:
- `researcher` - Information gathering
- `writer` - Content creation
- `analyzer` - Data analysis
- `coordinator` - Project management
- `reviewer` - Quality assurance
- `creative` - Innovation

### Step 2: Create Configuration File
```yaml
name: "your_agent_name"
role: "chosen_role"
system_prompt: |
  Define your agent's personality, expertise, and behavior here.
  Be specific about what the agent should do and how.
model: "gpt-4o-mini"
temperature: 0.7  # 0.0 = focused, 1.0 = creative
max_tokens: 1500
skills:
  - "skill_1"
  - "skill_2"
dependencies: ["other_agent_names"]  # Optional
output_format: "markdown"  # or "json" or "text"
```

### Step 3: Place in Configs Directory
Save as `configs/your_agent.yaml` and restart the system.

## Workflow Templates

### Pre-Built Templates

**research_and_write:**
```python
# Research → Write → Review pipeline
task = orchestrator.create_workflow_from_template(
    "research_and_write",
    topic="quantum computing",
    content_type="technical article"
)
```

**brainstorm_and_analyze:**
```python
# Creative → Analyze → Coordinate pipeline
task = orchestrator.create_workflow_from_template(
    "brainstorm_and_analyze",
    problem="reduce customer churn"
)
```

**content_pipeline:**
```python
# Research → Creative → Write → Review pipeline
task = orchestrator.create_workflow_from_template(
    "content_pipeline",
    topic="AI trends",
    content_type="blog post"
)
```

## Advanced Features

### Custom Workflows
Create your own multi-step workflows:

```python
workflow = [
    {"agent": "researcher", "description": "Market analysis",
     "instruction": "Research market trends and competitors"},
    {"agent": "creative", "description": "Strategy development",
     "instruction": "Develop innovative marketing strategies"},
    {"agent": "coordinator", "description": "Implementation plan",
     "instruction": "Create actionable implementation timeline"}
]
```

### Parallel Execution
Run multiple agents simultaneously:

```python
# All agents work on the same task in parallel
results = await orchestrator.execute_parallel_task(task)
```

### Result Management
Automatic result saving and tracking:

```python
# Results saved to outputs/ directory
filename = orchestrator.save_results(task_id, "custom_name.json")

# View agent performance
orchestrator.show_swarm_status()
```

## Sample Outputs

### Research Report Example
```markdown
# Artificial Intelligence Research Report

## Executive Summary
AI technology has experienced unprecedented growth, with applications
spanning healthcare, finance, and autonomous systems...

## Key Findings
- 40% increase in enterprise AI adoption
- Healthcare AI showing 15% efficiency improvements
- Regulatory frameworks still developing

## Recommendations
1. Invest in AI literacy training
2. Develop ethical AI guidelines
3. Create cross-functional AI teams
```

### Product Launch Plan Example
```markdown
# AI Mobile App Launch Strategy

## Phase 1: Pre-Launch (Weeks 1-4)
- Market research and competitive analysis
- Beta testing with 100 users
- Content creation and marketing materials

## Phase 2: Soft Launch (Weeks 5-6)
- Release to limited geographic markets
- Monitor user feedback and metrics
- Refine based on early data

## Success Metrics
- 10K downloads in first month
- 4.0+ app store rating
- 25% user retention after 30 days
```

## Technical Architecture

### Agent Communication
Agents communicate through structured messages:

```python
class SwarmMessage:
    from_agent: str
    to_agent: str
    message_type: str  # "task_result", "request", "notification"
    content: str
    timestamp: datetime
    metadata: dict
```

### Task Configuration
Tasks are defined with structured workflows:

```python
class TaskConfig:
    name: str
    description: str
    assigned_agents: List[str]
    workflow: List[Dict]  # Step-by-step instructions
    expected_output: str
    priority: int
```

### Result Tracking
All agent outputs are tracked and saved:

```python
class AgentResult:
    agent_name: str
    task_id: str
    timestamp: datetime
    success: bool
    content: str
    metadata: dict
    next_steps: List[str]
```

## Educational Value

This system demonstrates:

1. **Agent Architecture Patterns** - How to structure AI agents
2. **Workflow Orchestration** - Coordinating multiple AI systems
3. **No-Code Configuration** - Making AI accessible to non-programmers
4. **Inter-Agent Communication** - How agents share information
5. **Asynchronous Processing** - Handling concurrent AI operations
6. **Result Aggregation** - Combining outputs from multiple sources

## Extending the System

### Add New Agent Types
1. Create new class inheriting from `BaseAgent`
2. Implement `_execute_task()` method
3. Add to `AGENT_TYPES` registry
4. Create configuration template

### Add New Workflow Templates
1. Define workflow steps in `create_workflow_from_template()`
2. Specify agent sequence and instructions
3. Add template documentation

### Custom Output Formats
1. Modify agent configurations
2. Update system prompts for desired format
3. Add post-processing if needed

## Troubleshooting

### Common Issues

**No agents loaded:**
- Check `configs/` directory exists
- Verify YAML syntax in config files
- Ensure agent roles match available types

**API errors:**
- Verify OpenAI API key in `.env` file
- Check internet connection
- Monitor API usage limits

**Workflow failures:**
- Check agent dependencies are met
- Verify agent names in workflow match configs
- Review error messages in outputs

### Debug Mode
Enable detailed logging by setting environment variable:
```bash
export DEBUG=true
python demo.py
```

## Performance Tips

1. **Batch Operations** - Group related tasks together
2. **Parallel Processing** - Use parallel execution for independent tasks
3. **Temperature Settings** - Lower for consistent results, higher for creativity
4. **Token Limits** - Adjust based on expected output length
5. **Caching** - Reuse results where appropriate

Perfect for teaching modern AI agent development, workflow orchestration, and no-code AI system design!