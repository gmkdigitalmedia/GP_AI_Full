# M&A Agent Swarm Architecture

## System Overview

**9 Specialized AI Agents** working in a **sequential pipeline** to perform M&A due diligence.

## Agent Pipeline

```mermaid
graph TB
    subgraph Input
        PDFs[PDF Documents]
    end

    subgraph Stage1[Stage 1: Document Ingestion]
        A1[Document Ingestion Agent]
    end

    subgraph Stage2[Stage 2: Data Extraction]
        A2[Extraction Agent]
    end

    subgraph Stage3[Stage 3: Data Transformation]
        A3[Transformation Agent]
    end

    subgraph Stage4[Stage 4: Parallel Analysis]
        A4[Financial Analysis Agent]
        A5[Legal/Risk Analysis Agent]
        A6[Market Analysis Agent]
        A7[Operational Analysis Agent]
    end

    subgraph Stage5[Stage 5: Synthesis]
        A8[Synthesis Agent]
    end

    subgraph Stage6[Stage 6: Report Generation]
        A9[Report Generation Agent]
    end

    subgraph Output
        REPORT[PDF Report]
    end

    PDFs --> A1
    A1 -->|Document Classifications| A2
    A2 -->|Extracted Data| A3
    A3 -->|Normalized Data| A4
    A3 -->|Normalized Data| A5
    A3 -->|Normalized Data| A6
    A3 -->|Normalized Data| A7
    A4 -->|Financial Analysis| A8
    A5 -->|Legal Analysis| A8
    A6 -->|Market Analysis| A8
    A7 -->|Operational Analysis| A8
    A8 -->|Synthesis + Deal Score| A9
    A9 --> REPORT

    style A1 fill:#4CAF50,stroke:#2E7D32,stroke-width:2px,color:#fff
    style A2 fill:#2196F3,stroke:#1565C0,stroke-width:2px,color:#fff
    style A3 fill:#FF9800,stroke:#E65100,stroke-width:2px,color:#fff
    style A4 fill:#9C27B0,stroke:#6A1B9A,stroke-width:2px,color:#fff
    style A5 fill:#F44336,stroke:#C62828,stroke-width:2px,color:#fff
    style A6 fill:#00BCD4,stroke:#00838F,stroke-width:2px,color:#fff
    style A7 fill:#FFEB3B,stroke:#F57F17,stroke-width:2px,color:#000
    style A8 fill:#795548,stroke:#4E342E,stroke-width:2px,color:#fff
    style A9 fill:#607D8B,stroke:#37474F,stroke-width:2px,color:#fff
```

## Detailed Workflow

```mermaid
sequenceDiagram
    participant User
    participant Workflow as MA Workflow
    participant A1 as Document Ingestion Agent
    participant A2 as Extraction Agent
    participant A3 as Transformation Agent
    participant A4 as Financial Agent
    participant A5 as Legal Agent
    participant A6 as Market Agent
    participant A7 as Operational Agent
    participant A8 as Synthesis Agent
    participant A9 as Report Agent
    participant GPT as GPT-4 API
    participant FS as File System

    User->>Workflow: Run with PDFs

    Note over Workflow: Stage 1: Document Ingestion
    loop For each PDF
        Workflow->>FS: Read PDF
        FS-->>Workflow: PDF Content
        Workflow->>A1: Classify document
        A1->>GPT: Analyze content
        GPT-->>A1: Classification
        A1-->>Workflow: Document Type + Confidence
    end
    Workflow->>FS: Save classifications.json

    Note over Workflow: Stage 2: Data Extraction
    loop For each PDF
        Workflow->>A2: Extract data based on type
        A2->>GPT: Extract structured data
        GPT-->>A2: Extracted data
        A2-->>Workflow: Structured data
    end
    Workflow->>FS: Save extracted_data.json

    Note over Workflow: Stage 3: Data Transformation
    Workflow->>A3: Normalize all extracted data
    A3->>GPT: Transform and normalize
    GPT-->>A3: Normalized data
    A3-->>Workflow: Unified data structure
    Workflow->>FS: Save transformed_data.json

    Note over Workflow: Stage 4: Parallel Analysis
    par Financial Analysis
        Workflow->>A4: Analyze financials
        A4->>GPT: Financial analysis
        GPT-->>A4: Valuation, risks, trends
        A4-->>Workflow: Financial report
    and Legal Analysis
        Workflow->>A5: Analyze legal/risks
        A5->>GPT: Legal analysis
        GPT-->>A5: Compliance, contracts, risks
        A5-->>Workflow: Legal report
    and Market Analysis
        Workflow->>A6: Analyze market
        A6->>GPT: Market analysis
        GPT-->>A6: Competition, synergies
        A6-->>Workflow: Market report
    and Operational Analysis
        Workflow->>A7: Analyze operations
        A7->>GPT: Operational analysis
        GPT-->>A7: Integration, culture fit
        A7-->>Workflow: Operational report
    end
    Workflow->>FS: Save all analyses

    Note over Workflow: Stage 5: Synthesis
    Workflow->>A8: Synthesize all analyses
    A8->>GPT: Create overall assessment
    GPT-->>A8: Deal score + recommendation
    A8-->>Workflow: Synthesis report
    Workflow->>FS: Save synthesis.json

    Note over Workflow: Stage 6: Report Generation
    Workflow->>A9: Generate PDF report
    A9->>GPT: Create formatted report
    GPT-->>A9: Report content
    A9-->>Workflow: Report sections
    Workflow->>FS: Generate PDF
    FS-->>User: Final PDF Report
```

## Agent Details

### Agent 1: Document Ingestion Agent
- **Purpose**: Classify PDF documents into categories
- **Input**: PDF file path and preview text
- **Output**: Document type (financial_statement, legal_contract, market_research, etc.), confidence score, summary
- **Model**: GPT-4o

### Agent 2: Extraction Agent
- **Purpose**: Extract structured data based on document type
- **Input**: Full PDF text + document type
- **Output**: Structured data (financial metrics, legal terms, market data, etc.)
- **Model**: GPT-4o

### Agent 3: Transformation Agent
- **Purpose**: Normalize and standardize extracted data
- **Input**: All extracted data from multiple documents
- **Output**: Unified, normalized data structure
- **Model**: GPT-4o

### Agent 4: Financial Analysis Agent
- **Purpose**: Perform financial due diligence
- **Input**: Normalized financial data
- **Output**: Valuation analysis, financial health, trends, risks
- **Model**: GPT-4o

### Agent 5: Legal/Risk Analysis Agent
- **Purpose**: Analyze legal and compliance risks
- **Input**: Normalized legal data
- **Output**: Compliance issues, contractual risks, litigation concerns
- **Model**: GPT-4o

### Agent 6: Market Analysis Agent
- **Purpose**: Analyze market position and competitive landscape
- **Input**: Normalized market data
- **Output**: Market position, synergies, opportunities, risks
- **Model**: GPT-4o

### Agent 7: Operational Analysis Agent
- **Purpose**: Assess operational fit and integration
- **Input**: Normalized operational data
- **Output**: Integration complexity, cultural fit, operational risks
- **Model**: GPT-4o

### Agent 8: Synthesis Agent
- **Purpose**: Combine all analyses into overall assessment
- **Input**: All 4 analysis reports
- **Output**: Deal score (0-100), key findings, critical risks, recommendation
- **Model**: GPT-4o

### Agent 9: Report Generation Agent
- **Purpose**: Create comprehensive PDF report
- **Input**: All analyses + synthesis
- **Output**: Structured report content
- **Model**: GPT-4o
- **Post-processing**: PDF generation via PDFKit

## Data Flow

```mermaid
graph LR
    subgraph Input Layer
        PDF1[Financial.pdf]
        PDF2[Contract.pdf]
        PDF3[Market.pdf]
    end

    subgraph Processing Layer
        CLASS[Classifications]
        EXTRACT[Extracted Data]
        TRANSFORM[Normalized Data]
    end

    subgraph Analysis Layer
        FIN[Financial Analysis]
        LEG[Legal Analysis]
        MKT[Market Analysis]
        OPS[Operational Analysis]
    end

    subgraph Synthesis Layer
        SYNTH[Synthesis<br/>Deal Score: 75/100<br/>Recommendation: BUY]
    end

    subgraph Output Layer
        REPORT[PDF Report<br/>25 pages]
    end

    PDF1 --> CLASS
    PDF2 --> CLASS
    PDF3 --> CLASS
    CLASS --> EXTRACT
    EXTRACT --> TRANSFORM
    TRANSFORM --> FIN
    TRANSFORM --> LEG
    TRANSFORM --> MKT
    TRANSFORM --> OPS
    FIN --> SYNTH
    LEG --> SYNTH
    MKT --> SYNTH
    OPS --> SYNTH
    SYNTH --> REPORT
```

## Technology Stack

- **Framework**: Mastra (TypeScript AI agent framework)
- **LLM**: OpenAI GPT-4o
- **PDF Parsing**: pdf-parse
- **PDF Generation**: PDFKit
- **Data Storage**: Local JSON files
- **Language**: TypeScript/Node.js

## File Structure

```
ma-agent-swarm/
├── src/
│   ├── agents/                     # 9 AI agent definitions
│   │   ├── document-ingestion-agent.ts
│   │   ├── extraction-agent.ts
│   │   ├── transformation-agent.ts
│   │   ├── financial-analysis-agent.ts
│   │   ├── legal-risk-agent.ts
│   │   ├── market-analysis-agent.ts
│   │   ├── operational-analysis-agent.ts
│   │   ├── synthesis-agent.ts
│   │   └── report-generation-agent.ts
│   ├── workflows/
│   │   └── ma-workflow.ts          # Sequential orchestrator
│   ├── tools/
│   │   ├── pdf-parser.ts           # PDF text extraction
│   │   └── pdf-generator.ts        # PDF report creation
│   └── types/
│       └── index.ts                # TypeScript schemas
├── data/
│   ├── input/                      # PDF inputs
│   ├── extracted/                  # Intermediate JSON
│   └── output/                     # Final report + JSON
└── package.json
```

## Execution Flow

1. **User runs**: `npm start`
2. **Workflow loads**: All PDF files from `data/input/`
3. **Sequential processing**:
   - Stage 1: Classify all PDFs (Agent 1)
   - Stage 2: Extract data from each PDF (Agent 2)
   - Stage 3: Normalize all data (Agent 3)
   - Stage 4: Parallel analysis (Agents 4-7)
   - Stage 5: Synthesize results (Agent 8)
   - Stage 6: Generate PDF report (Agent 9)
4. **Output**: Final report saved to `data/output/`

## Key Design Decisions

### Why Sequential Pipeline?
- **Data dependency**: Each stage needs output from previous stage
- **Quality control**: Errors caught early before expensive analysis
- **Clarity**: Easy to understand and debug

### Why Parallel Analysis (Stage 4)?
- **Independence**: 4 analyses don't depend on each other
- **Speed**: 4x faster than sequential
- **Efficiency**: Maximizes GPT-4 API usage

### Why 9 Agents?
- **Separation of concerns**: Each agent has single responsibility
- **Specialized prompts**: Expert-level instructions per domain
- **Modularity**: Easy to add/remove/modify agents
- **Testability**: Each agent can be tested independently

## Performance Characteristics

- **Total agents**: 9
- **Total LLM calls**: ~10-15 (depending on number of PDFs)
- **Estimated time**: 2-5 minutes (for 3-5 PDFs)
- **Token usage**: ~30,000-50,000 tokens
- **Estimated cost**: $0.50-$1.00 per run (GPT-4o pricing)

## Scalability

**Current limitations**:
- Sequential processing of PDFs (not parallelized)
- All data held in memory
- Local file system storage only

**Future enhancements**:
- Parallel PDF processing
- Database storage for large datasets
- Caching of classifications and extractions
- Streaming output for long reports
