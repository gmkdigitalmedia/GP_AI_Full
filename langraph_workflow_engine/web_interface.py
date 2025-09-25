"""
FastAPI Web Interface for LangGraph Workflow Engine

WHAT THIS DEMONSTRATES:
This file shows how to wrap a LangGraph workflow in a web API for production use.
Key patterns demonstrated:

1. FASTAPI INTEGRATION: How to expose LangGraph workflows via REST API
2. REQUEST/RESPONSE MODELS: Using Pydantic for data validation
3. ERROR HANDLING: Proper exception handling for workflow failures
4. WEB INTERFACE: HTML/CSS/JavaScript frontend for testing workflows
5. PRODUCTION PATTERNS: Health checks, CORS, proper HTTP status codes

ARCHITECTURE:
- FastAPI handles HTTP requests/responses
- LangGraph WorkflowEngine processes the business logic
- Pydantic models ensure type safety
- HTML interface provides interactive testing

This is how you'd deploy LangGraph workflows in production:
- Containerize with Docker
- Deploy behind a load balancer
- Add authentication/authorization
- Integrate with monitoring systems
"""

from fastapi import FastAPI, HTTPException  # Web framework
from fastapi.staticfiles import StaticFiles   # For serving static files
from fastapi.responses import HTMLResponse    # HTML response type
from pydantic import BaseModel              # Data validation
from workflow_engine import WorkflowEngine   # Our LangGraph workflow
import uvicorn                             # ASGI server
import os

# CREATE FASTAPI APPLICATION
# This is the main web application that will serve our LangGraph workflow
app = FastAPI(title="LangGraph Workflow Engine", version="1.0.0")

# INITIALIZE THE WORKFLOW ENGINE
# We create ONE instance that will handle all requests
# In production, you might want to use dependency injection
engine = WorkflowEngine()

# PYDANTIC MODELS FOR TYPE SAFETY
# These models ensure that incoming/outgoing data has the correct structure
class TicketRequest(BaseModel):
    content: str  # The customer's message

class TicketResponse(BaseModel):
    ticket: str           # Original ticket content
    urgency: str          # Analyzed urgency level
    category: str         # Ticket category
    customer_tier: str    # Customer tier
    assigned_team: str    # Which team handles this
    escalated: bool       # Whether escalated to human
    response: str         # Generated response
    processing_log: list  # Step-by-step processing log

@app.get("/", response_class=HTMLResponse)
async def get_interface():
    """Serve the web interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LangGraph Workflow Engine</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            .header { text-align: center; margin-bottom: 30px; color: #333; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; color: #555; }
            textarea { width: 100%; height: 120px; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 14px; }
            button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
            button:hover { background: #0056b3; }
            button:disabled { background: #6c757d; cursor: not-allowed; }
            .result { margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 6px; border-left: 4px solid #007bff; }
            .result h3 { margin-top: 0; color: #007bff; }
            .metadata { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .metadata div { background: white; padding: 10px; border-radius: 4px; border: 1px solid #eee; }
            .metadata strong { color: #333; }
            .response { background: #e7f3ff; padding: 15px; border-radius: 6px; margin: 15px 0; }
            .processing-log { background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px; }
            .escalated { color: #dc3545; font-weight: bold; }
            .loading { display: none; text-align: center; padding: 20px; }
            .decision-tree { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border: 1px solid #ddd; }
            .decision-tree h3 { margin-top: 0; color: #333; text-align: center; }
            .tree-diagram { display: flex; flex-direction: column; align-items: center; }
            .tree-node { background: white; padding: 8px 16px; border: 2px solid #007bff; border-radius: 6px; margin: 5px; font-weight: bold; }
            .tree-node.start { background: #e7f3ff; border-color: #0056b3; }
            .tree-node.decision { background: #fff3cd; border-color: #ffc107; }
            .tree-node.end { background: #d1ecf1; border-color: #17a2b8; }
            .arrow { font-size: 18px; color: #666; margin: 2px 0; }
            .tree-branches { display: flex; justify-content: space-around; width: 100%; max-width: 800px; }
            .branch { display: flex; flex-direction: column; align-items: center; margin: 0 10px; }
            .branch-label { background: #6c757d; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin: 5px 0; }
            .sub-branches { display: flex; margin-top: 10px; }
            .sub-branch { display: flex; flex-direction: column; align-items: center; margin: 0 10px; }
            .examples { margin-bottom: 20px; }
            .example { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 4px; cursor: pointer; font-size: 14px; }
            .example:hover { background: #e9ecef; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>LangGraph Workflow Engine</h1>
                <p>Customer Support Ticket Router with Complex Decision Trees</p>
            </div>

            <div class="decision-tree">
                <h3>Decision Tree Flow</h3>
                <div class="tree-diagram">
                    <div class="tree-node start">Ticket Input</div>
                    <div class="arrow">↓</div>
                    <div class="tree-node">Analyze Content</div>
                    <div class="arrow">↓</div>
                    <div class="tree-node">Customer Tier Detection</div>
                    <div class="arrow">↓</div>
                    <div class="tree-node decision">Route by Urgency</div>
                    <div class="tree-branches">
                        <div class="branch">
                            <div class="branch-label">CRITICAL</div>
                            <div class="arrow">↓</div>
                            <div class="tree-node end">Escalate to Human</div>
                        </div>
                        <div class="branch">
                            <div class="branch-label">HIGH/MEDIUM</div>
                            <div class="arrow">↓</div>
                            <div class="tree-node">Assign Team</div>
                            <div class="arrow">↓</div>
                            <div class="tree-node decision">Check Escalation</div>
                            <div class="sub-branches">
                                <div class="sub-branch">
                                    <div class="branch-label">YES</div>
                                    <div class="arrow">↓</div>
                                    <div class="tree-node end">Human Agent</div>
                                </div>
                                <div class="sub-branch">
                                    <div class="branch-label">NO</div>
                                    <div class="arrow">↓</div>
                                    <div class="tree-node end">Generate Response</div>
                                </div>
                            </div>
                        </div>
                        <div class="branch">
                            <div class="branch-label">LOW</div>
                            <div class="arrow">↓</div>
                            <div class="tree-node end">Auto-Resolve</div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="examples">
                <label>Example Tickets (click to use):</label>
                <div class="example" onclick="setTicket('Hi, I\\'m from ABC Enterprise and our production system is completely down! This is CRITICAL!')">
                    Critical Enterprise Issue
                </div>
                <div class="example" onclick="setTicket('Hello, I\\'d like to request a new feature for bulk data export in the pro plan')">
                    Pro Feature Request
                </div>
                <div class="example" onclick="setTicket('My billing seems incorrect this month, can someone help?')">
                    Billing Question
                </div>
                <div class="example" onclick="setTicket('This app is terrible! Nothing works and I\\'m very angry about it!')">
                    Angry Customer Complaint
                </div>
                <div class="example" onclick="setTicket('Quick question about how to use the search feature')">
                    Simple Question
                </div>
            </div>

            <form onsubmit="processTicket(event)">
                <div class="form-group">
                    <label for="ticket">Customer Support Ticket:</label>
                    <textarea id="ticket" name="ticket" placeholder="Enter customer support ticket content here..." required></textarea>
                </div>
                <button type="submit" id="submitBtn">Process Ticket</button>
            </form>

            <div class="loading" id="loading">
                <p>🔄 Processing ticket through workflow...</p>
            </div>

            <div id="result" class="result" style="display: none;">
                <h3>Workflow Result</h3>
                <div id="resultContent"></div>
            </div>
        </div>

        <script>
            function setTicket(text) {
                document.getElementById('ticket').value = text;
            }

            async function processTicket(event) {
                event.preventDefault();

                const ticket = document.getElementById('ticket').value;
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                const result = document.getElementById('result');

                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                loading.style.display = 'block';
                result.style.display = 'none';

                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ content: ticket })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const data = await response.json();

                    const escalatedBadge = data.escalated ?
                        '<span class="escalated">ESCALATED</span>' :
                        'Auto-processed';

                    document.getElementById('resultContent').innerHTML = `
                        <div class="metadata">
                            <div><strong>Urgency:</strong> ${data.urgency.toUpperCase()}</div>
                            <div><strong>Category:</strong> ${data.category}</div>
                            <div><strong>Customer Tier:</strong> ${data.customer_tier}</div>
                            <div><strong>Assigned Team:</strong> ${data.assigned_team}</div>
                            <div><strong>Status:</strong> ${escalatedBadge}</div>
                        </div>

                        <div class="response">
                            <strong>Response:</strong><br>
                            ${data.response}
                        </div>

                        <details>
                            <summary><strong>Processing Log (${data.processing_log.length} steps)</strong></summary>
                            <div class="processing-log">
                                ${data.processing_log.map((step, i) => `${i+1}. ${step}`).join('<br>')}
                            </div>
                        </details>
                    `;

                    result.style.display = 'block';

                } catch (error) {
                    console.error('Error:', error);
                    document.getElementById('resultContent').innerHTML = `
                        <div style="color: red;">
                            <strong>Error:</strong> ${error.message}<br>
                            Make sure your OpenAI API key is set in the .env file.
                        </div>
                    `;
                    result.style.display = 'block';
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Process Ticket';
                    loading.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """

# FASTAPI ENDPOINTS
# These are the REST API endpoints that clients can call

@app.post("/process", response_model=TicketResponse)
async def process_ticket(request: TicketRequest):
    """
    MAIN WORKFLOW ENDPOINT
    This is where the magic happens - we receive a ticket and run it
    through the entire LangGraph workflow.

    Process:
    1. Validate incoming request (Pydantic handles this automatically)
    2. Call the LangGraph workflow engine
    3. Return structured response
    4. Handle any errors gracefully

    This endpoint demonstrates how to wrap LangGraph workflows for production use.
    """

    # Input validation
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Ticket content cannot be empty")

    try:
        # Call the LangGraph workflow - this is where all the magic happens
        # The workflow will run through all nodes, make routing decisions,
        # and return the final result
        result = await engine.process_ticket(request.content)

        # Return the structured response using our Pydantic model
        return TicketResponse(**result)

    except Exception as e:
        # Production error handling - log the error and return a clean response
        # In production, you'd want proper logging here
        raise HTTPException(status_code=500, detail=f"Workflow processing failed: {str(e)}")

@app.get("/health")
async def health_check():
    """
    HEALTH CHECK ENDPOINT
    Production systems need health checks for:
    - Load balancer health monitoring
    - Kubernetes liveness/readiness probes
    - Service discovery systems
    - Monitoring and alerting
    """
    return {"status": "healthy", "workflow": "ready"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting LangGraph Workflow Engine on http://localhost:{port}")
    print("📝 Make sure to set OPENAI_API_KEY in your .env file")
    uvicorn.run(app, host="0.0.0.0", port=port)