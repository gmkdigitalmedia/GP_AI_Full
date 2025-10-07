# GP Swarm - Web Visualization Interface

A beautiful, real-time web interface for watching AI agent swarms work together!

## What You'll See

### 🎯 Real-Time Agent Visualization
- **Live Workflow Display** - Watch agents work in sequence or parallel
- **Agent Status Indicators** - See which agents are working, idle, or completed
- **Progress Tracking** - Real-time progress bars and animations
- **Result Previews** - See agent outputs as they're generated

### 🎮 Interactive Control Panel
- **Quick Start Templates** - Pre-built workflows for common tasks
- **Custom Input** - Customize topics, products, or problems
- **One-Click Launch** - Start complex multi-agent workflows instantly
- **Task History** - Track completed tasks and success rates

### 📊 Live Monitoring
- **Agent Performance** - Success rates and task counts
- **Connection Status** - Real-time WebSocket connection indicator
- **Error Handling** - Visual feedback for failed tasks
- **Output Streaming** - See agent responses as they're generated

## How to Run

### 1. Quick Start
```bash
# From the agent-swarm directory
python run_web.py
```

### 2. Manual Start
```bash
cd web
python app.py
```

### 3. Open Browser
Navigate to: **http://localhost:5000**

## What You'll Experience

### Workflow Templates

**1. Research & Write Report**
- 🔍 Researcher gathers information
- ✍️ Writer creates professional content
- 👀 Reviewer polishes and improves
- **Watch**: Sequential agent collaboration

**2. Product Launch Planning**
- 💡 Creative generates launch ideas
- 📋 Coordinator creates project plan
- 📈 Analyzer evaluates market potential
- **Watch**: Strategic planning workflow

**3. Content Marketing Pipeline**
- 🔍 Researcher analyzes audience
- 🎨 Creative develops strategy
- ✍️ Writer produces content
- **Watch**: Marketing content creation

**4. Parallel Brainstorming**
- 💡 Creative thinks outside the box
- 📊 Analyzer evaluates feasibility
- 📋 Coordinator plans implementation
- **Watch**: Simultaneous agent thinking

## Visual Features

### 🎨 Beautiful Design
- **Gradient Backgrounds** - Modern, professional appearance
- **Animated Indicators** - Pulsing agents, progress bars
- **Color-Coded Status** - Easy to understand at a glance
- **Responsive Layout** - Works on desktop and mobile

### ⚡ Real-Time Updates
- **WebSocket Communication** - Instant updates, no refresh needed
- **Live Agent Cards** - Status changes in real-time
- **Workflow Animation** - Watch the process flow
- **Progress Tracking** - See exactly where you are

### 🔄 Interactive Elements
- **Clickable Templates** - Easy task selection
- **Custom Parameters** - Personalize your workflows
- **Status Monitoring** - Connection and health indicators
- **History Tracking** - See what you've accomplished

## Technical Features

### Backend (Flask + WebSocket)
- **Real-time Communication** - WebSocket for live updates
- **Async Task Execution** - Non-blocking agent workflows
- **Error Handling** - Graceful failure recovery
- **Result Persistence** - Automatic output saving

### Frontend (HTML5 + JavaScript)
- **WebSocket Client** - Real-time data synchronization
- **Responsive Design** - CSS Grid and Flexbox
- **Animation Engine** - CSS animations and transitions
- **Interactive Controls** - Dynamic template selection

### Agent Integration
- **Direct Orchestrator Interface** - No additional APIs needed
- **Live Status Updates** - Real-time agent monitoring
- **Result Streaming** - See outputs as they're generated
- **Error Visualization** - Clear failure indicators

## Usage Scenarios

### 📚 Educational Demonstrations
- **Show AI Agent Concepts** - Visual learning for students
- **Workflow Understanding** - See how agents collaborate
- **Real-time Feedback** - Immediate results and reactions
- **Interactive Learning** - Hands-on experience with AI

### 🔬 Development & Testing
- **Agent Debugging** - Watch workflow execution
- **Performance Monitoring** - Track agent efficiency
- **Output Validation** - Review agent responses
- **System Health** - Monitor connection status

### 🎪 Presentations & Demos
- **Live Demonstrations** - Show AI in action
- **Audience Engagement** - Interactive task selection
- **Visual Appeal** - Professional, modern interface
- **Reliable Performance** - Stable WebSocket connections

## Customization

### Add New Templates
Edit `app.py` to add new workflow templates:

```python
{
    'id': 'my_custom_workflow',
    'name': 'My Custom Process',
    'description': 'Description of what this does',
    'agents': ['agent1', 'agent2', 'agent3'],
    'estimated_time': '2-3 minutes'
}
```

### Modify Styling
Edit `templates/index.html` CSS section:
- Colors and gradients
- Animation timing
- Layout and spacing
- Component styling

### Extend Functionality
- Add new WebSocket events in `app.py`
- Create additional UI components
- Implement new monitoring features
- Add data visualization charts

## Troubleshooting

### Common Issues

**Web interface won't start:**
```bash
pip install flask flask-socketio eventlet
```

**Agents not loading:**
- Check `configs/` directory exists
- Verify YAML files are valid
- Ensure OpenAI API key is set

**WebSocket connection fails:**
- Check firewall settings
- Try different browser
- Verify port 5000 is available

**Tasks not starting:**
- Verify OpenAI API key
- Check internet connection
- Review browser console for errors

### Debug Mode
Run with debug enabled:
```bash
# Edit web/app.py, change last line to:
app.run(debug=True)
```

## Browser Compatibility

**Recommended Browsers:**
- Chrome 90+ ✅
- Firefox 88+ ✅
- Safari 14+ ✅
- Edge 90+ ✅

**Required Features:**
- WebSocket support
- CSS Grid and Flexbox
- ES6 JavaScript
- FontAwesome icons

## Performance Notes

- **WebSocket Efficiency** - Minimal bandwidth usage
- **Real-time Updates** - Sub-second response times
- **Memory Usage** - Lightweight client-side code
- **Mobile Support** - Responsive design works on phones

Perfect for teaching, demonstrations, and understanding how AI agent swarms operate in real-time!