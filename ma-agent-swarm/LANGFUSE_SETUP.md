# 🎯 EASY SETUP: See Everything on Langfuse Dashboard

Langfuse is **FREE** and has excellent Mastra integration. Follow these exact steps:

## Step 1: Sign Up for Langfuse (30 seconds)

1. Go to **https://cloud.langfuse.com**
2. Click **"Sign Up"** (free forever plan available)
3. Sign up with GitHub or Google

## Step 2: Get Your API Keys (30 seconds)

Once logged in to Langfuse:

1. You'll see your dashboard
2. Click **Settings** (⚙️ icon on left sidebar)
3. Click **"API Keys"** tab
4. Click **"Create new API keys"**
5. Copy these 3 values:
   - **Public Key** (starts with `pk-lf-...`)
   - **Secret Key** (starts with `sk-lf-...`)
   - **Host** (should be `https://cloud.langfuse.com`)

## Step 3: Add Keys to Your Project (30 seconds)

1. Open your `.env` file in the project:
   ```bash
   nano .env  # or use your editor
   ```

2. Add these lines (replace with your actual keys):
   ```
   OPENAI_API_KEY=sk-your-openai-key

   LANGFUSE_PUBLIC_KEY=pk-lf-1234567890abcdef
   LANGFUSE_SECRET_KEY=sk-lf-0987654321fedcba
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

3. Save the file

## Step 4: Run Your Workflow

```bash
npm start
```

Add some PDFs to `data/input/` first!

## Step 5: Watch on Langfuse Dashboard! 🎉

1. Go back to **https://cloud.langfuse.com**
2. Click on **"Traces"** in the left sidebar
3. You'll see your M&A workflow running in REAL-TIME!

---

## 📊 What You'll See on Langfuse

### Traces View
Every agent execution as a trace:
```
MA Workflow Run
├── document-ingestion-agent
│   ├── Input: { fileName: "financial.pdf", content: "..." }
│   ├── LLM Call: GPT-4o (2.3s, 1,234 tokens, $0.025)
│   └── Output: { documentType: "financial_statement", ... }
├── extraction-agent
│   ├── Input: { documentType: "financial_statement", ... }
│   ├── LLM Call: GPT-4o (3.1s, 2,456 tokens, $0.049)
│   └── Output: { extractedData: {...} }
├── transformation-agent
│   ├── LLM Call: GPT-4o (4.2s, 3,567 tokens, $0.071)
│   └── Output: { normalizedData: {...} }
├── financial-analysis-agent (parallel)
│   └── LLM Call: GPT-4o (5.1s, 4,123 tokens, $0.082)
├── legal-risk-agent (parallel)
│   └── LLM Call: GPT-4o (4.8s, 3,891 tokens, $0.078)
├── market-analysis-agent (parallel)
│   └── LLM Call: GPT-4o (5.3s, 4,234 tokens, $0.085)
├── operational-analysis-agent (parallel)
│   └── LLM Call: GPT-4o (4.9s, 3,967 tokens, $0.079)
├── synthesis-agent
│   └── LLM Call: GPT-4o (3.7s, 2,789 tokens, $0.056)
└── report-generation-agent
    └── LLM Call: GPT-4o (6.2s, 5,123 tokens, $0.102)
```

### For Each Agent You See:
- ✅ **Input** - What was passed to the agent
- ✅ **Output** - What the agent returned
- ✅ **LLM Calls** - Every GPT-4 API call
- ✅ **Tokens** - Input/output token counts
- ✅ **Cost** - Exact cost in USD
- ✅ **Latency** - How long each step took
- ✅ **Errors** - If anything fails

### Dashboard Features:
- **Real-time updates** - See agents working live
- **Full conversation history** - See exact prompts and responses
- **Cost tracking** - Know exactly how much you're spending
- **Performance metrics** - Find slow agents
- **Error tracking** - Debug issues easily
- **Search & filter** - Find specific runs
- **Export data** - Download traces as JSON

---

## 🎬 Demo Time!

After running `npm start`, you'll see something like this in Langfuse:

**Project Dashboard:**
- Total Traces: 1
- Total Tokens: 37,384
- Total Cost: $0.627
- Avg Latency: 45.2s

**Click on the trace to see:**
- Full agent workflow tree
- Every LLM prompt and completion
- Token usage breakdown
- Timing waterfall chart

---

## ✅ That's It!

You now have **full observability** of your M&A Agent Swarm!

### Next Steps:
1. Run multiple analyses to compare
2. Track your costs
3. Optimize slow agents
4. Share traces with your team
5. Export data for your course presentation

---

## 🆚 Langfuse vs Mastra Cloud

| Feature | Langfuse | Mastra Cloud |
|---------|----------|--------------|
| **Free Plan** | ✅ Yes, generous | ⚠️ Beta access |
| **Setup** | 2 minutes | Unclear |
| **Dashboard** | ✅ Excellent | 🚧 In development |
| **Mastra Integration** | ✅ Official support | ✅ Native |
| **LLM Tracing** | ✅✅✅ Best-in-class | ✅ Good |
| **Cost Tracking** | ✅ Per token | ✅ Yes |
| **Ready to Use** | ✅ Now | ⏳ Soon |

**Recommendation:** Use Langfuse for your course. It's production-ready and FREE!

---

## 🐛 Troubleshooting

**"No traces showing up"**
- Check your `.env` has the correct Langfuse keys
- Make sure you saved the `.env` file
- Restart your workflow: `npm start`

**"Authentication error"**
- Double-check your Secret Key (starts with `sk-lf-`)
- Make sure there are no spaces in the keys

**"Still not working"**
- Remove and recreate API keys in Langfuse
- Make sure you're using the default project
- Check Langfuse status page

---

## 🎓 Perfect for Your Course!

Langfuse gives you:
- ✅ Visual proof your agents are working
- ✅ Real metrics to show (tokens, cost, time)
- ✅ Easy to demo in presentations
- ✅ Professional-looking dashboard
- ✅ Free forever!
