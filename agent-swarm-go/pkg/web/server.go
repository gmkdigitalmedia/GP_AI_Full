package web

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"sync"
	"time"

	"agent-swarm-go/pkg/swarm"
	"agent-swarm-go/pkg/types"

	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool {
		return true // Allow all origins for demo
	},
}

// Server manages the web dashboard
type Server struct {
	swarm       *swarm.Swarm
	clients     map[*websocket.Conn]bool
	clientsMu   sync.RWMutex
	eventStream chan types.Event
}

// NewServer creates a new web server
func NewServer(s *swarm.Swarm) *Server {
	server := &Server{
		swarm:       s,
		clients:     make(map[*websocket.Conn]bool),
		eventStream: s.GetEventBus().Subscribe(),
	}

	// Start broadcasting events to websocket clients
	go server.broadcastEvents()

	return server
}

// Start starts the web server
func (s *Server) Start(port int) error {
	http.HandleFunc("/", s.handleIndex)
	http.HandleFunc("/ws", s.handleWebSocket)
	http.HandleFunc("/api/status", s.handleStatus)
	http.HandleFunc("/api/agents", s.handleAgents)

	addr := fmt.Sprintf(":%d", port)
	log.Printf("🌐 Web dashboard starting at http://localhost%s\n", addr)
	return http.ListenAndServe(addr, nil)
}

// handleIndex serves the main dashboard HTML
func (s *Server) handleIndex(w http.ResponseWriter, r *http.Request) {
	html := `<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Swarm Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 30px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 12px;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .panel {
            background: #1e293b;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .panel h2 {
            color: #60a5fa;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #334155;
            padding-bottom: 10px;
        }
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .agent-card {
            background: #334155;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #10b981;
            transition: transform 0.2s;
        }
        .agent-card:hover { transform: translateY(-2px); }
        .agent-card.busy { border-left-color: #f59e0b; }
        .agent-name { font-weight: bold; font-size: 1.1em; margin-bottom: 5px; }
        .agent-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-top: 8px;
        }
        .agent-status.idle { background: #10b981; }
        .agent-status.processing { background: #f59e0b; }
        .event-log {
            height: 500px;
            overflow-y: auto;
            background: #0f172a;
            border-radius: 8px;
            padding: 15px;
        }
        .event {
            padding: 12px;
            margin-bottom: 10px;
            border-left: 3px solid #3b82f6;
            background: #1e293b;
            border-radius: 4px;
            animation: slideIn 0.3s ease-out;
            word-wrap: break-word;
            white-space: pre-wrap;
            max-width: 100%;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .event.received { border-left-color: #3b82f6; }
        .event.started { border-left-color: #f59e0b; }
        .event.completed { border-left-color: #10b981; }
        .event.failed { border-left-color: #ef4444; }
        .event-time { color: #64748b; font-size: 0.85em; }
        .event-agent { color: #60a5fa; font-weight: bold; }
        .event-message { margin-top: 5px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: #1e293b;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            color: #60a5fa;
        }
        .stat-label {
            color: #94a3b8;
            margin-top: 8px;
        }
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
        }
        .connection-status.connected {
            background: #10b981;
        }
        .connection-status.disconnected {
            background: #ef4444;
        }
        .task-result {
            background: #1e293b;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            border-left: 4px solid #10b981;
        }
        .task-result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
        }
        .task-result-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #60a5fa;
        }
        .task-result-time {
            color: #64748b;
            font-size: 0.9em;
        }
        .task-result-content {
            background: #0f172a;
            padding: 15px;
            border-radius: 6px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.6;
            max-height: 400px;
            overflow-y: auto;
        }
        .task-result-agent {
            display: inline-block;
            background: #334155;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            margin-top: 10px;
        }
        .event-data {
            color: #94a3b8;
            font-size: 0.85em;
            margin-top: 5px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="connection-status" id="connection-status">● Connecting...</div>

    <div class="header">
        <h1>🚀 Agent Swarm Dashboard</h1>
        <p>Real-time Multi-Agent System Monitoring</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-value" id="total-agents">0</div>
            <div class="stat-label">Total Agents</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="active-agents">0</div>
            <div class="stat-label">Active Agents</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="tasks-completed">0</div>
            <div class="stat-label">Tasks Completed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value" id="tasks-processing">0</div>
            <div class="stat-label">Processing</div>
        </div>
    </div>

    <div class="dashboard">
        <div class="panel">
            <h2>🤖 Agents</h2>
            <div class="agent-grid" id="agents"></div>
        </div>
        <div class="panel">
            <h2>📊 Live Event Stream</h2>
            <div class="event-log" id="event-log"></div>
        </div>
    </div>

    <div class="panel" style="margin-top: 20px;" id="results-panel">
        <h2>📝 Task Results</h2>
        <div id="task-results" style="max-height: 600px; overflow-y: auto;"></div>
    </div>

    <script>
        let ws;
        let tasksCompleted = 0;
        let tasksProcessing = 0;
        let agents = {};

        function connect() {
            ws = new WebSocket('ws://' + window.location.host + '/ws');

            ws.onopen = () => {
                document.getElementById('connection-status').textContent = '● Connected';
                document.getElementById('connection-status').className = 'connection-status connected';
                loadInitialStatus();
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleEvent(data);
            };

            ws.onclose = () => {
                document.getElementById('connection-status').textContent = '● Disconnected';
                document.getElementById('connection-status').className = 'connection-status disconnected';
                setTimeout(connect, 3000);
            };
        }

        function loadInitialStatus() {
            fetch('/api/agents')
                .then(r => r.json())
                .then(data => {
                    agents = data;
                    updateAgentsDisplay();
                });
        }

        function handleEvent(event) {
            addEventToLog(event);

            if (event.type === 'task_completed') {
                tasksCompleted++;
                document.getElementById('tasks-completed').textContent = tasksCompleted;
                // Display the full result
                if (event.data) {
                    addTaskResult(event);
                }
            }

            if (event.type === 'task_started') {
                tasksProcessing++;
                document.getElementById('tasks-processing').textContent = tasksProcessing;
                if (agents[event.agent_id]) {
                    agents[event.agent_id].state = 'processing';
                    updateAgentsDisplay();
                }
            }

            if (event.type === 'task_completed' || event.type === 'task_failed') {
                tasksProcessing = Math.max(0, tasksProcessing - 1);
                document.getElementById('tasks-processing').textContent = tasksProcessing;
            }
        }

        function addTaskResult(event) {
            const resultsDiv = document.getElementById('task-results');
            const resultDiv = document.createElement('div');
            resultDiv.className = 'task-result';

            const time = new Date(event.timestamp).toLocaleTimeString();

            let resultContent = '';
            if (event.data && event.data.Data) {
                resultContent = String(event.data.Data);
            } else if (event.data) {
                resultContent = JSON.stringify(event.data, null, 2);
            }

            resultDiv.innerHTML = '<div class="task-result-header">' +
                '<div class="task-result-title">' + event.agent_id + '</div>' +
                '<div class="task-result-time">' + time + '</div>' +
                '</div>' +
                '<div class="task-result-content">' + escapeHtml(resultContent) + '</div>' +
                '<div class="task-result-agent">Task: ' + event.task_id + '</div>';

            resultsDiv.insertBefore(resultDiv, resultsDiv.firstChild);

            // Keep only last 10 results
            while (resultsDiv.children.length > 10) {
                resultsDiv.removeChild(resultsDiv.lastChild);
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        function addEventToLog(event) {
            const log = document.getElementById('event-log');
            const eventDiv = document.createElement('div');
            eventDiv.className = 'event ' + event.type.replace('task_', '');

            const time = new Date(event.timestamp).toLocaleTimeString();
            const icon = {
                'task_received': '📥',
                'task_started': '⚙️',
                'task_completed': '✅',
                'task_failed': '❌'
            }[event.type] || '📌';

            eventDiv.innerHTML = ` + "`" + `
                <div class="event-time">${time}</div>
                <div class="event-agent">${icon} ${event.agent_id}</div>
                <div class="event-message">${event.message}</div>
            ` + "`" + `;

            log.insertBefore(eventDiv, log.firstChild);

            // Keep only last 50 events
            while (log.children.length > 50) {
                log.removeChild(log.lastChild);
            }
        }

        function updateAgentsDisplay() {
            const container = document.getElementById('agents');
            container.innerHTML = '';

            let activeCount = 0;
            for (const [id, agent] of Object.entries(agents)) {
                const card = document.createElement('div');
                card.className = 'agent-card' + (agent.state === 'processing' ? ' busy' : '');

                const statusClass = agent.state === 'idle' ? 'idle' : 'processing';
                card.innerHTML = ` + "`" + `
                    <div class="agent-name">${id}</div>
                    <div class="agent-status ${statusClass}">${agent.state}</div>
                ` + "`" + `;

                container.appendChild(card);
                if (agent.state === 'processing') activeCount++;
            }

            document.getElementById('total-agents').textContent = Object.keys(agents).length;
            document.getElementById('active-agents').textContent = activeCount;
        }

        connect();
    </script>
</body>
</html>`

	w.Header().Set("Content-Type", "text/html")
	w.Write([]byte(html))
}

// handleWebSocket handles WebSocket connections
func (s *Server) handleWebSocket(w http.ResponseWriter, r *http.Request) {
	conn, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Printf("WebSocket upgrade error: %v", err)
		return
	}

	s.clientsMu.Lock()
	s.clients[conn] = true
	s.clientsMu.Unlock()

	// Send initial status
	status := s.swarm.GetSwarmStatus()
	agents := make(map[string]interface{})
	for id, state := range status {
		agents[id] = map[string]interface{}{
			"state": string(state),
		}
	}
	conn.WriteJSON(map[string]interface{}{
		"type": "initial_status",
		"data": agents,
	})

	// Keep connection alive
	go func() {
		defer func() {
			s.clientsMu.Lock()
			delete(s.clients, conn)
			s.clientsMu.Unlock()
			conn.Close()
		}()

		for {
			_, _, err := conn.ReadMessage()
			if err != nil {
				break
			}
		}
	}()
}

// handleStatus returns current swarm status
func (s *Server) handleStatus(w http.ResponseWriter, r *http.Request) {
	status := s.swarm.GetSwarmStatus()
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(status)
}

// handleAgents returns all agents with their current status
func (s *Server) handleAgents(w http.ResponseWriter, r *http.Request) {
	status := s.swarm.GetSwarmStatus()
	agents := make(map[string]interface{})

	for id, state := range status {
		agents[id] = map[string]interface{}{
			"state": string(state),
			"id":    id,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(agents)
}

// broadcastEvents sends events to all connected WebSocket clients
func (s *Server) broadcastEvents() {
	for event := range s.eventStream {
		s.clientsMu.RLock()
		for client := range s.clients {
			err := client.WriteJSON(event)
			if err != nil {
				log.Printf("WebSocket write error: %v", err)
				client.Close()
				s.clientsMu.Lock()
				delete(s.clients, client)
				s.clientsMu.Unlock()
			}
		}
		s.clientsMu.RUnlock()

		// Small delay to avoid overwhelming clients
		time.Sleep(10 * time.Millisecond)
	}
}