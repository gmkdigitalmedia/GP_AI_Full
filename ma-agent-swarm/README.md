# M&A Agent Swarm - Due Diligence System

An intelligent multi-agent system built with [Mastra](https://mastra.ai) for automated M&A (Mergers & Acquisitions) due diligence. This system uses a sequential workflow of specialized AI agents to analyze documents, extract insights, and generate comprehensive due diligence reports.

## 🎯 Overview

The M&A Agent Swarm automates the due diligence process by analyzing PDF documents through a sophisticated pipeline of AI agents:

```
PDFs → Ingestion → Extraction → Transformation → Analysis → Synthesis → PDF Report
```

### Agent Pipeline

1. **Document Ingestion Agent** - Classifies documents (financial statements, legal contracts, market research, etc.)
2. **Extraction Agent** - Extracts structured data based on document type
3. **Transformation Agent** - Normalizes and structures data into consistent formats
4. **Analysis Agents** (Parallel):
   - **Financial Analysis** - Valuation, financial health, trends, risks
   - **Legal/Risk Analysis** - Compliance, contracts, litigation, IP
   - **Market Analysis** - Competitive landscape, synergies, opportunities
   - **Operational Analysis** - Integration complexity, cultural fit, risks
5. **Synthesis Agent** - Combines analyses into overall assessment with deal score
6. **Report Generation Agent** - Creates professional PDF report

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- OpenAI API key (for GPT-4)
- PDF documents for analysis

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd ma-agent-swarm
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=sk-your-api-key-here
   ```

4. **Add PDF documents**

   Place your PDF documents in the `data/input/` directory:
   ```bash
   # Your PDFs should be M&A related documents such as:
   # - Financial statements (10-K, 10-Q, balance sheets)
   # - Legal contracts and agreements
   # - Market research reports
   # - Operational reports
   # - Investor presentations
   # - Due diligence checklists
   ```

### Usage

**Basic usage (analyzes PDFs in `data/input/`):**
```bash
npm start
```

**Specify a custom PDF directory:**
```bash
npm start /path/to/pdfs
```

**Specify PDF directory and target company name:**
```bash
npm start /path/to/pdfs "Acme Corporation"
```

**Development mode (with watch):**
```bash
npm run dev
```

### Output

The workflow generates several outputs in `data/`:

```
data/
├── input/                          # Your PDF documents (input)
├── extracted/                      # Intermediate data
│   ├── classifications.json        # Document classifications
│   ├── extracted_data.json         # Extracted raw data
│   └── transformed_data.json       # Normalized data
└── output/                         # Final outputs
    ├── financial_analysis.json     # Financial analysis
    ├── legal_risk_analysis.json    # Legal/risk analysis
    ├── market_analysis.json        # Market analysis
    ├── operational_analysis.json   # Operational analysis
    ├── synthesis.json              # Overall synthesis
    └── MA_Due_Diligence_Report_YYYY-MM-DD.pdf  # 📄 FINAL REPORT
```

## 📊 What the System Analyzes

### Financial Analysis
- Valuation multiples (P/E, EV/EBITDA, P/B, P/S)
- Financial health (profitability, liquidity, leverage)
- Trend analysis (revenue growth, margin trends)
- Financial risks and red flags
- Quality of earnings assessment

### Legal & Risk Analysis
- Regulatory compliance
- Material contracts and obligations
- Litigation exposure
- Intellectual property assessment
- Recommended legal protections

### Market Analysis
- Market positioning and share
- Competitive landscape
- Synergy identification (revenue and cost)
- Growth opportunities
- Market risks and threats

### Operational Analysis
- Integration complexity assessment
- Cultural fit evaluation
- Key personnel risks
- Integration timeline and plan
- Change management requirements

### Final Synthesis
- Overall deal assessment
- Deal score (0-100)
- Key findings (top 5-7)
- Critical risks (top 5)
- Strategic benefits (top 5)
- Clear recommendation (STRONG BUY, BUY, CONDITIONAL BUY, HOLD, PASS)

## 🏗️ Project Structure

```
ma-agent-swarm/
├── src/
│   ├── agents/                     # AI agent definitions
│   │   ├── document-ingestion-agent.ts
│   │   ├── extraction-agent.ts
│   │   ├── transformation-agent.ts
│   │   ├── financial-analysis-agent.ts
│   │   ├── legal-risk-agent.ts
│   │   ├── market-analysis-agent.ts
│   │   ├── operational-analysis-agent.ts
│   │   ├── synthesis-agent.ts
│   │   └── report-generation-agent.ts
│   ├── tools/                      # Utility tools
│   │   ├── pdf-parser.ts          # PDF text extraction
│   │   └── pdf-generator.ts       # PDF report generation
│   ├── workflows/                  # Orchestration
│   │   └── ma-workflow.ts         # Main sequential workflow
│   ├── types/                      # TypeScript types
│   │   └── index.ts
│   └── index.ts                    # Main entry point
├── data/                           # Data directories
│   ├── input/                      # PDF inputs
│   ├── extracted/                  # Intermediate data
│   └── output/                     # Final outputs
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

## 🧪 Example Workflow

Here's what happens when you run the system:

```bash
$ npm start data/input "TechCorp Inc"

🔍 Starting M&A Due Diligence Workflow
=====================================

📥 Step 1: Document Ingestion & Classification
   Found 5 PDF files
   - Classifying: financial_statement_2024.pdf
     ✓ Classified as: financial_statement (confidence: 0.95)
   - Classifying: contracts.pdf
     ✓ Classified as: legal_contract (confidence: 0.88)
   ...

📊 Step 2: Data Extraction
   - Extracting data from: financial_statement_2024.pdf
     ✓ Extracted data from financial_statement_2024.pdf
   ...

🔄 Step 3: Data Transformation & Normalization
   ✓ Data transformation complete

📈 Step 4: Multi-Dimensional Analysis
   Running Financial, Legal, Market, and Operational analyses in parallel...
   ✓ Financial analysis complete
   ✓ Legal/risk analysis complete
   ✓ Market analysis complete
   ✓ Operational analysis complete

🎯 Step 5: Synthesis & Overall Assessment
   ✓ Synthesis complete

📝 Step 6: Generating PDF Report
   ✓ PDF report generated: MA_Due_Diligence_Report_2025-10-02.pdf

✅ M&A Workflow Complete!

📄 Report saved to: data/output/MA_Due_Diligence_Report_2025-10-02.pdf

🎉 SUCCESS!
=====================================
📄 Report: data/output/MA_Due_Diligence_Report_2025-10-02.pdf
📊 Documents Processed: 5
💯 Deal Score: 72/100
📝 Recommendation: BUY - Proceed with standard diligence
=====================================
```

## 🔧 Configuration

### Using Different LLM Models

The system uses GPT-4o by default. To use a different model, edit the agent files:

```typescript
// In src/agents/*.ts
import { openai } from '@ai-sdk/openai';

export const yourAgent = new Agent({
  model: openai('gpt-4o')  // Change to 'gpt-4-turbo', 'gpt-4', etc.
});
```

### Customizing Agents

Each agent has detailed instructions in `src/agents/*.ts`. You can customize:
- Instructions (agent behavior and expertise)
- Model selection
- Output schemas

### Adding New Analysis Dimensions

1. Create a new agent in `src/agents/`
2. Add it to the workflow in `src/workflows/ma-workflow.ts`
3. Include its output in the synthesis and report

## 📚 Learn More

- [Mastra Documentation](https://mastra.ai/en/docs)
- [Mastra GitHub](https://github.com/mastra-ai/mastra)
- [OpenAI API](https://platform.openai.com/docs)

## ⚠️ Important Notes

### For Educational Purposes

This system is designed for educational/course purposes and demonstrates:
- Multi-agent AI systems
- Sequential workflow orchestration
- Document processing and analysis
- LLM-powered insights generation

### Not Legal/Financial Advice

This tool:
- ❌ Should NOT replace professional due diligence
- ❌ Should NOT be used for actual M&A transactions without expert review
- ✅ Can be used for learning and prototyping
- ✅ Demonstrates AI-powered document analysis

### Data Privacy

- All processing happens locally (except LLM API calls)
- Documents are not stored by OpenAI (as of GPT-4 API usage)
- Extracted data is saved locally in `data/` directory
- Sensitive documents should be redacted before processing

## 🐛 Troubleshooting

**"No PDF files found"**
- Ensure PDFs are in `data/input/` or the directory you specified
- Check file extensions are `.pdf` (lowercase)

**"OPENAI_API_KEY not found"**
- Create a `.env` file in the project root
- Add your OpenAI API key

**"PDF parsing failed"**
- Ensure PDFs are text-based (not scanned images)
- If you need OCR support, add Tesseract.js

**Timeout or slow processing**
- Large PDFs may take time
- Each agent call to GPT-4 takes 10-30 seconds
- Consider using gpt-4o-mini for faster (but less accurate) results

## 📝 License

ISC

## 🤝 Contributing

This is an educational project. Feel free to fork and modify for your learning purposes!
