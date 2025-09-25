"""
LangGraph Workflow Engine - Customer Support Ticket Router
Demonstrates complex decision trees with state management

WHAT IS LANGGRAPH?
LangGraph is a library for building stateful, multi-agent workflows.
Unlike simple agent chaining (A->B->C), LangGraph provides:
- STATEFUL WORKFLOWS: Data persists and flows between nodes
- CONDITIONAL ROUTING: Different paths based on data analysis
- COMPLEX DECISION TREES: Multiple branching paths with business logic
- LOOP-BACK CAPABILITIES: Nodes can revisit earlier steps

KEY CONCEPTS:
1. StateGraph: The main workflow container
2. Nodes: Individual processing steps (analyze, route, respond)
3. Edges: Connections between nodes (simple or conditional)
4. State: Data structure that flows through all nodes
5. Conditional Edges: Smart routing based on state data

This example shows a customer support ticket router with:
- 7 different processing nodes
- Complex conditional routing logic
- Persistent state management
- Multiple possible workflow paths
"""

from typing import Dict, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END  # Core LangGraph components
from langchain_openai import ChatOpenAI      # LLM for analysis
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel              # Data validation
import os
from dotenv import load_dotenv

load_dotenv()

# LANGGRAPH STATE DEFINITION
# This TypedDict defines the data structure that flows through ALL nodes
# Every node receives this state, can modify it, and passes it to the next node
# This is what makes LangGraph "stateful" - data persists across the workflow
class WorkflowState(TypedDict):
    ticket_content: str      # Original customer message
    customer_tier: str       # basic/pro/enterprise (affects routing)
    urgency: str            # low/medium/high/critical (main routing factor)
    category: str           # technical/billing/feature_request/complaint
    assigned_team: str      # which team handles this ticket
    escalated: bool         # whether ticket needs human intervention
    resolution_steps: List[str]  # steps taken during processing
    final_response: str     # generated response to customer
    processing_log: List[str]    # audit trail of decisions made

# Response models
class TicketAnalysis(BaseModel):
    urgency: str  # low, medium, high, critical
    category: str  # technical, billing, feature_request, complaint
    sentiment: str  # positive, neutral, negative, angry
    requires_human: bool

class TeamAssignment(BaseModel):
    team: str  # support_l1, support_l2, engineering, billing, management
    reason: str
    estimated_resolution_hours: int

# MAIN WORKFLOW ENGINE CLASS
# This class demonstrates core LangGraph patterns:
# 1. Building a StateGraph with nodes and edges
# 2. Implementing conditional routing logic
# 3. Managing state flow through complex decision trees
class WorkflowEngine:
    def __init__(self):
        # Initialize LLM for ticket analysis
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,  # Low temperature for consistent analysis
            api_key=os.getenv("OPENAI_API_KEY")
        )
        # Build and compile the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        BUILD THE LANGGRAPH WORKFLOW
        This is where the magic happens - we define:
        1. All processing nodes (steps in the workflow)
        2. Simple edges (always go to next node)
        3. Conditional edges (routing based on state data)
        4. Entry and exit points
        """

        # Create the main workflow graph with our state structure
        workflow = StateGraph(WorkflowState)

        # STEP 1: ADD ALL NODES
        # Each node is a function that processes the state
        # Node names are strings, functions are the actual processors
        workflow.add_node("analyze_ticket", self.analyze_ticket)           # Uses LLM to analyze content
        workflow.add_node("determine_customer_tier", self.determine_customer_tier)  # Detects customer level
        workflow.add_node("route_by_urgency", self.route_by_urgency)       # Preparation for routing
        workflow.add_node("assign_team", self.assign_team)                 # Business logic for team assignment
        workflow.add_node("check_escalation", self.check_escalation)       # Escalation rules
        workflow.add_node("generate_response", self.generate_response)     # Auto-generate response
        workflow.add_node("escalate_to_human", self.escalate_to_human)    # Human handoff
        workflow.add_node("auto_resolve", self.auto_resolve)               # Simple resolution

        # STEP 2: SET ENTRY POINT
        # All tickets start here
        workflow.set_entry_point("analyze_ticket")

        # STEP 3: ADD SIMPLE EDGES (always flow to next node)
        workflow.add_edge("analyze_ticket", "determine_customer_tier")
        workflow.add_edge("determine_customer_tier", "route_by_urgency")

        # STEP 4: ADD CONDITIONAL EDGES (smart routing based on data)
        # This is the heart of LangGraph - conditional logic
        # Based on urgency level, tickets take different paths:
        workflow.add_conditional_edges(
            "route_by_urgency",                    # FROM this node
            self.route_urgency_condition,          # CALL this function to decide
            {                                      # POSSIBLE destinations:
                "critical": "escalate_to_human",   # Critical -> immediate human
                "high": "assign_team",             # High -> team assignment
                "medium": "assign_team",           # Medium -> team assignment
                "low": "auto_resolve"              # Low -> auto-resolve
            }
        )

        # After team assignment, always check escalation
        workflow.add_edge("assign_team", "check_escalation")

        # Another conditional branch - escalation decision
        workflow.add_conditional_edges(
            "check_escalation",                    # FROM this node
            self.escalation_condition,             # CALL this function
            {                                      # POSSIBLE destinations:
                "escalate": "escalate_to_human",   # Needs escalation
                "continue": "generate_response"     # Continue normal flow
            }
        )

        # STEP 5: ADD END CONNECTIONS
        # All final nodes lead to END (workflow completion)
        workflow.add_edge("generate_response", END)
        workflow.add_edge("escalate_to_human", END)
        workflow.add_edge("auto_resolve", END)

        # STEP 6: COMPILE THE WORKFLOW
        # This creates the executable workflow from our graph definition
        return workflow.compile()

    # LANGGRAPH NODE FUNCTIONS
    # Each function below is a "node" in the workflow
    # Key points about LangGraph nodes:
    # 1. They receive the current state as input
    # 2. They modify the state (add data, update fields)
    # 3. They return the updated state
    # 4. State flows automatically to the next node

    async def analyze_ticket(self, state: WorkflowState) -> WorkflowState:
        """
        NODE 1: ANALYZE TICKET CONTENT
        This node uses an LLM to analyze the customer's message and extract:
        - Urgency level (critical/high/medium/low)
        - Category (technical/billing/feature_request/complaint)
        - Sentiment (for escalation decisions)

        This is where AI does the heavy lifting - understanding customer intent
        """

        system_prompt = """You are a customer service AI analyzing support tickets.
        Analyze the ticket and return urgency (low/medium/high/critical),
        category (technical/billing/feature_request/complaint),
        sentiment (positive/neutral/negative/angry), and if it requires human intervention."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Ticket: {state['ticket_content']}")
        ]

        response = await self.llm.ainvoke(messages)

        # Parse LLM response (simplified - in production use structured output)
        analysis_text = response.content.lower()

        # Extract urgency level using keyword matching
        if "critical" in analysis_text:
            urgency = "critical"
        elif "high" in analysis_text:
            urgency = "high"
        elif "medium" in analysis_text:
            urgency = "medium"
        else:
            urgency = "low"

        # Extract category using keyword matching
        if "billing" in analysis_text:
            category = "billing"
        elif "technical" in analysis_text or "bug" in analysis_text:
            category = "technical"
        elif "feature" in analysis_text:
            category = "feature_request"
        else:
            category = "complaint"

        # UPDATE STATE - This is key to LangGraph
        # We modify the state object, and it flows to the next node
        state["urgency"] = urgency
        state["category"] = category
        state["processing_log"].append(f"Analyzed ticket: {urgency} urgency, {category} category")

        return state  # State flows to next node automatically

    async def determine_customer_tier(self, state: WorkflowState) -> WorkflowState:
        """Determine customer tier (enterprise/pro/basic)"""

        # Simulate customer tier lookup
        # In real implementation, this would query a database
        tier_keywords = {
            "enterprise": ["enterprise", "business", "company", "organization"],
            "pro": ["pro", "professional", "premium"],
            "basic": ["basic", "free", "trial"]
        }

        content_lower = state["ticket_content"].lower()

        for tier, keywords in tier_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                state["customer_tier"] = tier
                break
        else:
            state["customer_tier"] = "basic"

        state["processing_log"].append(f"Customer tier: {state['customer_tier']}")
        return state

    async def route_by_urgency(self, state: WorkflowState) -> WorkflowState:
        """Route based on urgency level"""
        state["processing_log"].append(f"Routing by urgency: {state['urgency']}")
        return state

    # CONDITIONAL ROUTING FUNCTIONS
    # These functions are called by LangGraph to decide which path to take
    # They examine the current state and return a string that matches
    # one of the keys in the conditional_edges mapping

    def route_urgency_condition(self, state: WorkflowState) -> str:
        """
        CONDITIONAL ROUTING FUNCTION #1
        This function decides which path to take based on urgency level

        LangGraph calls this function and uses the return value to route:
        - Returns "critical" -> goes to "escalate_to_human" node
        - Returns "high" -> goes to "assign_team" node
        - Returns "medium" -> goes to "assign_team" node
        - Returns "low" -> goes to "auto_resolve" node

        The magic: Different tickets take completely different paths!
        """
        return state["urgency"]  # Return the urgency level for routing

    async def assign_team(self, state: WorkflowState) -> WorkflowState:
        """Assign appropriate team based on category and tier"""

        # Complex assignment logic
        category = state["category"]
        tier = state["customer_tier"]
        urgency = state["urgency"]

        if category == "billing":
            team = "billing"
        elif category == "technical" and urgency == "high":
            team = "support_l2"
        elif category == "technical":
            team = "support_l1"
        elif category == "feature_request" and tier == "enterprise":
            team = "engineering"
        else:
            team = "support_l1"

        # Upgrade team for enterprise customers
        if tier == "enterprise" and team == "support_l1":
            team = "support_l2"

        state["assigned_team"] = team
        state["processing_log"].append(f"Assigned to team: {team}")

        return state

    async def check_escalation(self, state: WorkflowState) -> WorkflowState:
        """Check if ticket needs escalation"""

        # Escalation rules
        escalate = False

        if (state["urgency"] == "high" and
            state["customer_tier"] == "enterprise"):
            escalate = True

        if (state["category"] == "complaint" and
            "angry" in state["ticket_content"].lower()):
            escalate = True

        state["escalated"] = escalate
        state["processing_log"].append(f"Escalation check: {escalate}")

        return state

    def escalation_condition(self, state: WorkflowState) -> str:
        """Conditional routing for escalation"""
        return "escalate" if state["escalated"] else "continue"

    async def generate_response(self, state: WorkflowState) -> WorkflowState:
        """Generate automated response"""

        system_prompt = f"""Generate a professional customer service response.
        Customer tier: {state['customer_tier']}
        Urgency: {state['urgency']}
        Category: {state['category']}
        Assigned team: {state['assigned_team']}

        Keep it helpful and professional."""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Original ticket: {state['ticket_content']}")
        ]

        response = await self.llm.ainvoke(messages)

        state["final_response"] = response.content
        state["processing_log"].append("Generated automated response")

        return state

    async def escalate_to_human(self, state: WorkflowState) -> WorkflowState:
        """Escalate to human agent"""

        state["final_response"] = f"""This ticket has been escalated to our {state.get('assigned_team', 'senior support')} team due to its {state['urgency']} priority level.

A human agent will contact you within 2 hours for {state['customer_tier']} customers.

Reference ID: ESCALATED-{hash(state['ticket_content']) % 10000}"""

        state["processing_log"].append("Escalated to human agent")

        return state

    async def auto_resolve(self, state: WorkflowState) -> WorkflowState:
        """Auto-resolve simple tickets"""

        auto_responses = {
            "billing": "Please check your account dashboard for billing details. Contact us if you need further assistance.",
            "feature_request": "Thank you for your suggestion! We've added it to our product roadmap for review.",
            "technical": "Please try clearing your browser cache and refreshing. If the issue persists, contact our technical team."
        }

        state["final_response"] = auto_responses.get(
            state["category"],
            "Thank you for contacting us. Your request has been processed."
        )
        state["assigned_team"] = "auto_resolved"
        state["processing_log"].append("Auto-resolved ticket")

        return state

    async def process_ticket(self, ticket_content: str) -> Dict:
        """Process a ticket through the workflow"""

        initial_state: WorkflowState = {
            "ticket_content": ticket_content,
            "customer_tier": "",
            "urgency": "",
            "category": "",
            "assigned_team": "",
            "escalated": False,
            "resolution_steps": [],
            "final_response": "",
            "processing_log": []
        }

        # Run the workflow
        result = await self.workflow.ainvoke(initial_state)

        return {
            "ticket": ticket_content,
            "urgency": result["urgency"],
            "category": result["category"],
            "customer_tier": result["customer_tier"],
            "assigned_team": result["assigned_team"],
            "escalated": result["escalated"],
            "response": result["final_response"],
            "processing_log": result["processing_log"]
        }


# Demo function
async def demo():
    """Demo the workflow engine with sample tickets"""

    engine = WorkflowEngine()

    test_tickets = [
        "Hi, I'm from ABC Enterprise and our production system is completely down! This is CRITICAL!",
        "Hello, I'd like to request a new feature for bulk data export in the pro plan",
        "My billing seems incorrect this month, can someone help?",
        "This app is terrible! Nothing works and I'm very angry about it!",
        "Quick question about how to use the search feature"
    ]

    print("🔄 LangGraph Workflow Engine Demo\n")

    for i, ticket in enumerate(test_tickets, 1):
        print(f"--- Ticket #{i} ---")
        print(f"Content: {ticket}")

        result = await engine.process_ticket(ticket)

        print(f"Urgency: {result['urgency']}")
        print(f"Category: {result['category']}")
        print(f"Customer Tier: {result['customer_tier']}")
        print(f"Assigned Team: {result['assigned_team']}")
        print(f"Escalated: {result['escalated']}")
        print(f"Response: {result['response'][:100]}...")
        print(f"Processing Steps: {len(result['processing_log'])} steps")
        print()

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())