#!/usr/bin/env python3
"""
GP Swarm - Web Interface for Agent Swarm Visualization

Real-time web interface to watch AI agents working together in swarms.
Shows agent status, task progress, and results as they happen.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import threading
import time

# Add parent directory to path to import swarm modules
sys.path.append(str(Path(__file__).parent.parent))

from swarm_orchestrator import SwarmOrchestrator
from agent_base import TaskConfig, AgentConfig
from agent_types import create_agent

class GPSwarmWeb:
    """
    Web interface for visualizing and controlling the agent swarm.

    Provides real-time updates via WebSocket as agents work on tasks.
    """

    def __init__(self):
        """Initialize the web application and swarm orchestrator."""
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'gp-swarm-secret-key-2024'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode='eventlet')

        # Initialize swarm orchestrator
        self.orchestrator = SwarmOrchestrator()
        self.current_task = None
        self.agent_status = {}
        self.task_history = []

        # Set up routes and socket handlers
        self._setup_routes()
        self._setup_socket_handlers()

    def _setup_routes(self):
        """Set up Flask routes for the web interface."""

        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('index.html')

        @self.app.route('/api/agents')
        def get_agents():
            """Get list of available agents."""
            agents_info = []
            for name, agent in self.orchestrator.agents.items():
                status = agent.get_status()
                agents_info.append({
                    'name': name,
                    'role': status['role'],
                    'total_tasks': status['total_tasks'],
                    'successful_tasks': status['successful_tasks'],
                    'skills': status['skills']
                })
            return jsonify(agents_info)

        @self.app.route('/api/task_templates')
        def get_task_templates():
            """Get available workflow templates."""
            templates = [
                {
                    'id': 'research_and_write',
                    'name': 'Research & Write Report',
                    'description': 'Research a topic and create a professional report',
                    'agents': ['researcher', 'writer', 'reviewer'],
                    'estimated_time': '2-3 minutes'
                },
                {
                    'id': 'product_launch',
                    'name': 'Product Launch Planning',
                    'description': 'Generate ideas, plan, and analyze product launch',
                    'agents': ['creative', 'coordinator', 'analyzer'],
                    'estimated_time': '2-4 minutes'
                },
                {
                    'id': 'content_marketing',
                    'name': 'Content Marketing Pipeline',
                    'description': 'Research, strategize, and create marketing content',
                    'agents': ['researcher', 'creative', 'writer'],
                    'estimated_time': '3-4 minutes'
                },
                {
                    'id': 'brainstorm_parallel',
                    'name': 'Parallel Brainstorm',
                    'description': 'Multiple agents brainstorm solutions simultaneously',
                    'agents': ['creative', 'analyzer', 'coordinator'],
                    'estimated_time': '1-2 minutes'
                }
            ]
            return jsonify(templates)

        @self.app.route('/api/start_task', methods=['POST'])
        def start_task():
            """Start a new task with the swarm."""
            data = request.json
            template_id = data.get('template_id')
            params = data.get('params', {})

            if template_id == 'research_and_write':
                topic = params.get('topic', 'artificial intelligence')
                task = self.orchestrator.create_workflow_from_template(
                    'research_and_write',
                    topic=topic,
                    content_type='report',
                    task_name=f'Research Report: {topic}'
                )
            elif template_id == 'product_launch':
                product = params.get('product', 'AI mobile app')
                task = self._create_product_launch_task(product)
            elif template_id == 'content_marketing':
                brand = params.get('brand', 'TechCorp')
                task = self._create_content_marketing_task(brand)
            elif template_id == 'brainstorm_parallel':
                problem = params.get('problem', 'improve productivity')
                task = self._create_brainstorm_task(problem)
            else:
                return jsonify({'error': 'Unknown template'}), 400

            # Start task in background
            self.current_task = task
            threading.Thread(target=self._execute_task_with_updates, args=(task,)).start()

            return jsonify({
                'task_id': task.id,
                'name': task.name,
                'status': 'started'
            })

    def _setup_socket_handlers(self):
        """Set up WebSocket event handlers."""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            print(f"Client connected: {request.sid}")
            # Send current agent status
            emit('agent_status_update', self._get_agent_status())

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            print(f"Client disconnected: {request.sid}")

        @self.socketio.on('request_status')
        def handle_status_request():
            """Handle status update request."""
            emit('agent_status_update', self._get_agent_status())

    def _get_agent_status(self):
        """Get current status of all agents."""
        status = {
            'agents': {},
            'current_task': None,
            'task_history': self.task_history[-5:]  # Last 5 tasks
        }

        for name, agent in self.orchestrator.agents.items():
            agent_info = agent.get_status()
            status['agents'][name] = {
                'name': name,
                'role': agent_info['role'],
                'status': 'idle',  # Will be updated during task execution
                'total_tasks': agent_info['total_tasks'],
                'success_rate': 0 if agent_info['total_tasks'] == 0 else
                               (agent_info['successful_tasks'] / agent_info['total_tasks']) * 100,
                'current_output': ''
            }

        if self.current_task:
            status['current_task'] = {
                'id': self.current_task.id,
                'name': self.current_task.name,
                'description': self.current_task.description
            }

        return status

    def _execute_task_with_updates(self, task):
        """Execute task with real-time WebSocket updates."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Notify task started
            self.socketio.emit('task_started', {
                'task_id': task.id,
                'name': task.name,
                'workflow': [{'agent': step.get('agent'), 'description': step.get('description')}
                           for step in task.workflow]
            })

            # Execute workflow steps
            results = {}
            context = {}

            for i, step in enumerate(task.workflow):
                agent_name = step.get('agent')
                step_description = step.get('description', '')

                if agent_name not in self.orchestrator.agents:
                    continue

                # Notify step started
                self.socketio.emit('step_started', {
                    'task_id': task.id,
                    'step_index': i,
                    'agent_name': agent_name,
                    'description': step_description
                })

                # Create sub-task for this step
                step_task = TaskConfig(
                    name=f"{task.name} - {step_description}",
                    description=step.get('instruction', step_description),
                    assigned_agents=[agent_name],
                    workflow=[],
                    expected_output=step.get('expected_output', '')
                )

                # Execute step
                result = loop.run_until_complete(
                    self.orchestrator.agents[agent_name].process_task(step_task, context)
                )

                results[agent_name] = result

                # Update context for next agents
                if result.success:
                    context[agent_name] = result.content

                # Notify step completed
                self.socketio.emit('step_completed', {
                    'task_id': task.id,
                    'step_index': i,
                    'agent_name': agent_name,
                    'success': result.success,
                    'output': result.content[:500] + ('...' if len(result.content) > 500 else ''),
                    'full_output': result.content
                })

                # Small delay for visualization
                time.sleep(1)

            # Task completed
            self.orchestrator.results[task.id] = list(results.values())

            # Save results
            filename = self.orchestrator.save_results(task.id)

            # Add to history
            self.task_history.append({
                'id': task.id,
                'name': task.name,
                'completed_at': datetime.now().isoformat(),
                'success': all(r.success for r in results.values()),
                'agent_count': len(results),
                'output_file': filename
            })

            # Notify task completed
            self.socketio.emit('task_completed', {
                'task_id': task.id,
                'name': task.name,
                'results': {name: {'success': r.success, 'content': r.content}
                           for name, r in results.items()},
                'output_file': filename
            })

            self.current_task = None

        except Exception as e:
            # Notify error
            self.socketio.emit('task_error', {
                'task_id': task.id,
                'error': str(e)
            })
            self.current_task = None

        finally:
            loop.close()

    def _create_product_launch_task(self, product):
        """Create product launch planning task."""
        workflow = [
            {
                'agent': 'creative_innovator',
                'description': 'Generate launch ideas',
                'instruction': f'Generate creative marketing and launch strategies for {product}'
            },
            {
                'agent': 'project_coordinator',
                'description': 'Create launch plan',
                'instruction': 'Create a detailed project plan for the product launch'
            },
            {
                'agent': 'data_analyzer',
                'description': 'Analyze market potential',
                'instruction': 'Analyze the market potential and success factors'
            }
        ]

        return TaskConfig(
            name=f'Product Launch: {product}',
            description=f'Comprehensive launch planning for {product}',
            assigned_agents=['creative_innovator', 'project_coordinator', 'data_analyzer'],
            workflow=workflow,
            expected_output='Complete product launch strategy'
        )

    def _create_content_marketing_task(self, brand):
        """Create content marketing task."""
        workflow = [
            {
                'agent': 'research_specialist',
                'description': 'Market research',
                'instruction': f'Research {brand} target audience and market trends'
            },
            {
                'agent': 'creative_innovator',
                'description': 'Content strategy',
                'instruction': 'Develop creative content angles and messaging strategies'
            },
            {
                'agent': 'content_writer',
                'description': 'Create content',
                'instruction': f'Write engaging marketing content for {brand}'
            }
        ]

        return TaskConfig(
            name=f'Content Marketing: {brand}',
            description=f'Create marketing content for {brand}',
            assigned_agents=['research_specialist', 'creative_innovator', 'content_writer'],
            workflow=workflow,
            expected_output='Professional marketing content'
        )

    def _create_brainstorm_task(self, problem):
        """Create parallel brainstorming task."""
        return TaskConfig(
            name=f'Brainstorm: {problem}',
            description=f'Generate solutions for: {problem}',
            assigned_agents=['creative_innovator', 'data_analyzer', 'project_coordinator'],
            workflow=[
                {'agent': 'creative_innovator', 'description': 'Creative solutions', 'instruction': f'Generate creative solutions for {problem}'},
                {'agent': 'data_analyzer', 'description': 'Analyze feasibility', 'instruction': 'Analyze the feasibility of proposed solutions'},
                {'agent': 'project_coordinator', 'description': 'Implementation plan', 'instruction': 'Create implementation plan for best solutions'}
            ],
            expected_output='Multiple solution perspectives'
        )

    async def load_agents(self):
        """Load agents from configuration files."""
        # Try different config paths depending on where the script is run from
        import os
        possible_paths = ['../configs', 'configs', './configs']
        for path in possible_paths:
            if os.path.exists(path):
                await self.orchestrator.load_agents_from_config(path)
                break
        else:
            # If no config directory found, try relative to script location
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(script_dir, '..', 'configs')
            await self.orchestrator.load_agents_from_config(config_path)

    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Run the web application."""
        print(f"Starting GP Swarm Web Interface...")
        print(f"Loading agents from configuration files...")

        # Load agents synchronously for startup
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.load_agents())
        loop.close()

        agent_count = len(self.orchestrator.agents)
        print(f"Loaded {agent_count} agents successfully!")
        print(f"Starting web server at http://{host}:{port}")
        print(f"Open your browser and navigate to the URL above to see GP Swarm in action!")

        self.socketio.run(self.app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    app = GPSwarmWeb()
    app.run(debug=True)