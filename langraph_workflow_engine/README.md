# LangGraph Workflow Engine

A production-ready customer support ticket router demonstrating **complex decision trees** using LangGraph and LangChain.

## Code Structure Explained

### `workflow_engine.py` - Core LangGraph Implementation

**What LangGraph Does:**
LangGraph creates stateful workflows where data flows through nodes with conditional branching. Unlike simple agent chaining (A→B→C), LangGraph enables:

- **Stateful Processing**: Data persists across all workflow steps
- **Conditional Routing**: Different paths based on runtime decisions
- **Complex Decision Trees**: Multiple branching points with business logic
- **Loop-Back Capabilities**: Ability to revisit earlier nodes

**Key Components:**

1. **WorkflowState (Lines 41-50)**
   ```python
   class WorkflowState(TypedDict):
       ticket_content: str      # Flows through all nodes
       urgency: str            # Determines routing path
       escalated: bool         # Influences final destination
   ```
   This state object travels through every node, accumulating data.

2. **StateGraph Construction (Lines 90-148)**
   ```python
   workflow = StateGraph(WorkflowState)
   workflow.add_node("analyze_ticket", self.analyze_ticket)
   workflow.add_conditional_edges("route_by_urgency",
                                 self.route_urgency_condition,
                                 {"critical": "escalate_to_human"})
   ```
   Defines the workflow structure with conditional branching.

3. **Node Functions (Lines 158+)**
   Each node receives state, processes it, and returns updated state:
   ```python
   async def analyze_ticket(self, state: WorkflowState) -> WorkflowState:
       # Process ticket content with LLM
       state["urgency"] = extracted_urgency
       return state  # State flows to next node
   ```

4. **Conditional Routing (Lines 245+)**
   ```python
   def route_urgency_condition(self, state: WorkflowState) -> str:
       return state["urgency"]  # "critical" → escalate_to_human
   ```
   LangGraph calls this to decide routing path.

### `web_interface.py` - FastAPI Integration

**Production Deployment Patterns:**

1. **API Wrapper (Lines 276-308)**
   ```python
   @app.post("/process")
   async def process_ticket(request: TicketRequest):
       result = await engine.process_ticket(request.content)
       return TicketResponse(**result)
   ```
   Wraps LangGraph workflow in REST API for production use.

2. **Type Safety (Lines 46-57)**
   ```python
   class TicketResponse(BaseModel):
       urgency: str
       escalated: bool
       processing_log: list
   ```
   Pydantic models ensure data validation and API documentation.

3. **Error Handling (Lines 305-308)**
   Production-ready exception handling with proper HTTP status codes.

## What This Demonstrates

- **Complex Decision Trees**: Multi-path routing based on urgency, category, and customer tier
- **State Management**: Persistent state across workflow steps
- **Conditional Logic**: Dynamic routing based on analysis results
- **LangGraph Integration**: Real workflow orchestration, not just sequential agents
- **Production Patterns**: Error handling, logging, and web interface

## 🏗️ Architecture

```
Ticket Input → Analyze → Customer Tier → Route by Urgency
                                              ↓
Auto-resolve ← Low                           Medium/High
                                              ↓
                                         Assign Team
                                              ↓
                                      Check Escalation
                                         ↓        ↓
                                 Continue    Escalate
                                     ↓           ↓
                              Generate     Human Agent
                              Response         ↓
                                   ↓         END
                                  END
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API Key**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Run Demo**
   ```bash
   python workflow_engine.py
   ```

4. **Launch Web Interface**
   ```bash
   python web_interface.py
   ```
   Visit: http://localhost:8000

## 🎮 Demo Scenarios

The system handles these complex routing scenarios:

### 1. **Critical Enterprise Issue**
```
Input: "Hi, I'm from ABC Enterprise and our production system is completely down! This is CRITICAL!"

Workflow: Analyze → Enterprise Tier → Critical Urgency → ESCALATE → Human Agent
Output: Immediate escalation to senior support team
```

### 2. **Simple Question**
```
Input: "Quick question about how to use the search feature"

Workflow: Analyze → Basic Tier → Low Urgency → AUTO-RESOLVE
Output: Automated helpful response
```

### 3. **Angry Customer**
```
Input: "This app is terrible! Nothing works and I'm very angry!"

Workflow: Analyze → Complaint Category → Escalation Check → Human Agent
Output: Escalated due to negative sentiment
```

## 🔧 Decision Tree Logic

### Urgency Routing
- **Critical** → Immediate human escalation
- **High** → Team assignment + escalation check
- **Medium** → Team assignment
- **Low** → Auto-resolution

### Team Assignment
- **Billing** issues → Billing team
- **Technical + High urgency** → L2 Support
- **Technical** → L1 Support
- **Feature requests (Enterprise)** → Engineering
- **Enterprise customers** → Upgraded team level

### Escalation Triggers
- High urgency + Enterprise customer
- Complaint + Negative sentiment
- Manual escalation flags

## 🛠️ Key Features

### LangGraph Workflow
```python
# Complex conditional routing
workflow.add_conditional_edges(
    "route_by_urgency",
    self.route_urgency_condition,
    {
        "critical": "escalate_to_human",
        "high": "assign_team",
        "medium": "assign_team",
        "low": "auto_resolve"
    }
)
```

### State Management
```python
class WorkflowState(TypedDict):
    ticket_content: str
    customer_tier: str
    urgency: str
    category: str
    assigned_team: str
    escalated: bool
    resolution_steps: List[str]
    final_response: str
    processing_log: List[str]
```

### Production-Ready
- ✅ Error handling
- ✅ Logging and observability
- ✅ Web interface
- ✅ Health checks
- ✅ Structured responses

## 🎯 Learning Outcomes

After building this, you'll understand:

1. **LangGraph Fundamentals**: State graphs, conditional routing, node composition
2. **Complex Decision Trees**: Multi-path workflows with business logic
3. **State Management**: Persistent data across workflow steps
4. **Production Patterns**: Error handling, logging, monitoring
5. **Integration**: Combining LangGraph with FastAPI and web interfaces

## 🔄 Workflow Visualization

The system creates a visual decision tree:

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│ Analyze     │ -> │ Customer     │ -> │ Route by    │
│ Ticket      │    │ Tier         │    │ Urgency     │
└─────────────┘    └──────────────┘    └─────────────┘
                                               │
                   ┌─────────────────────────────┼─────────────────────────────┐
                   │                             │                             │
              ┌────▼────┐                 ┌──────▼──────┐                ┌─────▼──────┐
              │ Critical│                 │ Medium/High │                │ Low        │
              │Escalate │                 │ Assign Team │                │Auto-Resolve│
              └─────────┘                 └─────────────┘                └────────────┘
                                                  │
                                          ┌───────▼──────┐
                                          │ Check        │
                                          │ Escalation   │
                                          └──────┬───────┘
                                                 │
                                    ┌────────────┼────────────┐
                                    │                         │
                            ┌───────▼───────┐      ┌─────────▼──────┐
                            │ Generate      │      │ Escalate to    │
                            │ Response      │      │ Human          │
                            └───────────────┘      └────────────────┘
```

## 📊 Example Processing Log

```
1. Analyzed ticket: critical urgency, technical category
2. Customer tier: enterprise
3. Routing by urgency: critical
4. Escalated to human agent
```

## 🎬 Perfect for Video Demo

- **Visual workflow** in web interface
- **Real-time processing** with step-by-step logs
- **Multiple scenarios** showing different paths
- **Production-ready** code students can extend
- **Clear learning progression** from simple to complex

This demonstrates **real LangGraph capabilities** beyond basic agent chaining!