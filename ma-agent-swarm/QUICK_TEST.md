# Quick Test - Does It Actually Work?

Forget dashboards. Let's just test if the agents work.

## Step 1: Add Your OpenAI API Key

```bash
# Create .env file
cp .env.example .env

# Edit it and add your OpenAI key:
OPENAI_API_KEY=sk-your-actual-key-here

# You can ignore the Langfuse stuff for now
```

## Step 2: Run Simple Test

```bash
npx tsx test-simple.ts
```

This will:
- Check if your OpenAI key works
- Call ONE agent (document ingestion)
- Show you the response
- Take about 5 seconds

If this works, the whole system works.

## Step 3: Run Full Workflow (Optional)

If the simple test passes:

```bash
# Create a dummy test file
echo "This is a test financial document with revenue of $1M" > data/input/test.txt

# Run the full workflow
npm start
```

**Problem:** It needs PDFs, not text files.

**Solution:** Either:
1. Add a real PDF to `data/input/`
2. Or I'll create a text-based version for testing

## What Should Happen

**Simple test (5 seconds):**
```
🧪 Testing if M&A Agent Swarm actually works...

✅ OpenAI API key found
🤖 Testing document ingestion agent...

✅ Agent responded!

📄 Response:
────────────────────────────────────────────────────────────
{
  "fileName": "Q4_Financial_Report_2024.pdf",
  "documentType": "financial_statement",
  "confidence": 0.98,
  "summary": "Consolidated balance sheet showing assets of $234.5M..."
}
────────────────────────────────────────────────────────────

✅ SUCCESS! The agent swarm is working!
```

**Full workflow (2-5 minutes with PDFs):**
- Processes all PDFs in `data/input/`
- Runs all 9 agents
- Generates final PDF report in `data/output/`

## Common Issues

**"No OpenAI API key"**
- Make sure `.env` file exists
- Make sure it has `OPENAI_API_KEY=sk-...`
- No quotes needed

**"Module not found"**
- Run `npm install` first

**"No PDF files found"**
- For full workflow, you need actual PDFs in `data/input/`
- Simple test doesn't need PDFs

## Bottom Line

Run `npx tsx test-simple.ts` - if that works, everything works!
