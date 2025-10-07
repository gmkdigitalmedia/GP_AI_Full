# 🚀 Mastra Cloud Setup - See Everything on the Dashboard

Follow these exact steps to see your M&A Agent Swarm running live on the Mastra Cloud dashboard.

## Step 1: Sign Up for Mastra Cloud

1. Go to **https://cloud.mastra.ai**
2. Sign up for an account (it's in public beta - free)
3. Once logged in, you'll see your dashboard

## Step 2: Get Your Credentials

From the Mastra Cloud dashboard:

1. Navigate to **Settings** or **API Keys**
2. Copy your:
   - **OTLP Endpoint** (something like `https://otlp.mastra.ai` or similar)
   - **API Key** (looks like `mst_xxxxxxxxxxxxx`)

## Step 3: Configure Your Project

1. **Update your `.env` file:**

   ```bash
   # Open your .env file
   nano .env  # or use your editor
   ```

   Add these lines (replace with your actual values):
   ```
   OPENAI_API_KEY=sk-your-openai-key

   # Mastra Cloud Observability
   OTEL_EXPORTER_OTLP_ENDPOINT=https://your-actual-endpoint
   OTEL_EXPORTER_OTLP_HEADERS=x-api-key=mst_your_actual_api_key
   ```

2. **Update your agents to use Mastra config:**

   The agents are already set up, but need to use the Mastra instance with telemetry.

   I'll update the workflow to use the centralized Mastra config.

## Step 4: Install Additional Dependencies (if needed)

```bash
npm install @mastra/core@latest
```

## Step 5: Run Your Workflow

```bash
npm start
```

## Step 6: View on Mastra Cloud Dashboard

1. Go back to **https://cloud.mastra.ai**
2. Click on **Observability** or **Traces**
3. You'll see in real-time:
   - ✅ Each agent execution
   - ✅ LLM calls and responses
   - ✅ Token usage and costs
   - ✅ Execution time
   - ✅ Full trace of the workflow
   - ✅ Logs from each step

## What You'll See on the Dashboard

### Agents Tab
- List of all your agents (document-ingestion-agent, extraction-agent, etc.)
- Status: idle, processing, completed
- Recent activity

### Traces Tab
- Complete workflow trace showing:
  ```
  MA Workflow
  ├── Document Ingestion
  │   └── GPT-4o call (2.3s, 1,234 tokens)
  ├── Extraction (3 documents)
  │   ├── financial_statement.pdf (3.1s, 2,456 tokens)
  │   ├── contract.pdf (2.8s, 1,892 tokens)
  │   └── market_research.pdf (3.5s, 2,145 tokens)
  ├── Transformation
  │   └── GPT-4o call (4.2s, 3,567 tokens)
  ├── Analysis (Parallel)
  │   ├── Financial Analysis (5.1s, 4,123 tokens)
  │   ├── Legal Analysis (4.8s, 3,891 tokens)
  │   ├── Market Analysis (5.3s, 4,234 tokens)
  │   └── Operational Analysis (4.9s, 3,967 tokens)
  ├── Synthesis
  │   └── GPT-4o call (3.7s, 2,789 tokens)
  └── Report Generation
      └── GPT-4o call (6.2s, 5,123 tokens)
  ```

### Logs Tab
- Detailed logs with timestamps
- Severity levels (info, warn, error)
- Searchable and filterable

### Metrics Tab
- Total tokens used
- Total cost
- Average response time
- Success/failure rates

## Troubleshooting

**"No data appearing on dashboard"**
- Check your `.env` has correct OTEL endpoint and API key
- Make sure telemetry is enabled in `src/config/mastra.ts`
- Check Mastra Cloud status

**"Authentication failed"**
- Verify your API key is correct
- Check the header format: `x-api-key=your_key`

**"Still can't see anything"**
- Check the Mastra Cloud documentation for any updates
- The service is in public beta, so setup might have changed
- Contact Mastra support: https://mastra.ai

## Alternative: Use Langfuse (Free & Open Source)

If Mastra Cloud setup is complex, you can use Langfuse instead:

1. Sign up at **https://cloud.langfuse.com** (free)
2. Get your Langfuse keys
3. Update `.env`:
   ```
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```
4. Mastra has built-in Langfuse support

Langfuse provides similar observability with a great dashboard.

---

**Next Steps After Setup:**
1. Run `npm start` with your PDFs
2. Watch the Mastra Cloud dashboard light up with real-time data
3. Explore traces to see exactly what each agent is doing
4. Check token usage and costs
5. Debug any issues by viewing detailed logs
