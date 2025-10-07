# Adding Mastra Dashboard/UI

The current implementation is CLI-only. To add the Mastra web dashboard, you have a few options:

## Option 1: Mastra Dev UI (Local Development)

Mastra has a built-in development UI for testing agents locally.

1. **Install Mastra CLI**
   ```bash
   npm install -g @mastra/cli
   ```

2. **Initialize Mastra project structure**
   ```bash
   mastra init
   ```

3. **Run the dev server**
   ```bash
   mastra dev
   ```

This will open `localhost:3000` with an agent playground where you can:
- Chat with individual agents
- See agent state and memory
- Test workflows interactively

However, this requires restructuring the project to match Mastra's expected layout.

## Option 2: Mastra Cloud (Hosted Dashboard)

For production observability with a web dashboard:

1. Sign up at [Mastra Cloud](https://cloud.mastra.ai)
2. Get your Mastra API key
3. Add to `.env`:
   ```
   MASTRA_API_KEY=your_mastra_api_key
   ```
4. Install observability package:
   ```bash
   npm install @mastra/observability
   ```
5. Add telemetry to agents (in each agent file):
   ```typescript
   import { telemetry } from '@mastra/observability';

   export const yourAgent = new Agent({
     name: 'your-agent',
     instructions: '...',
     model: openai('gpt-4o'),
     telemetry: telemetry // Add this
   });
   ```

Then you'll see:
- Real-time agent execution
- LLM calls and tokens
- Workflow progress
- Performance metrics
- Traces and logs

## Option 3: Build Custom Dashboard (Like the Go Example)

The Go agent-swarm you saw earlier has a custom web dashboard at `localhost:8080`. To replicate this:

1. **Install additional dependencies**
   ```bash
   npm install express socket.io
   npm install -D @types/express
   ```

2. **Create a simple web server** that:
   - Serves a web UI
   - Streams events via WebSocket
   - Shows workflow progress in real-time

Would you like me to build Option 3 - a custom real-time dashboard similar to the Go version?

## Recommendation for Your Course

**For learning/demos:**
- **Option 1 (Mastra Dev UI)** - Best for testing individual agents interactively
- **Option 3 (Custom Dashboard)** - Best for showing the full workflow in action with visual feedback

**For production use:**
- **Option 2 (Mastra Cloud)** - Production-grade observability and monitoring

---

## Quick Answer

**Current state:** CLI only - no web UI
**To see it on web:** Need to add Option 1, 2, or 3 above

Would you like me to implement Option 3 (custom dashboard with real-time updates)?
