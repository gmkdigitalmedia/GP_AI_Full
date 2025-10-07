import { Agent } from '@mastra/core';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';
import { DocumentClassification, DocumentInput } from '../types/index.js';

/**
 * Document Ingestion Agent
 *
 * Receives PDF file paths and classifies documents into categories:
 * - Financial statements
 * - Legal contracts
 * - Market research
 * - Operational reports
 * - Investor presentations
 * - Due diligence documents
 */
export const documentIngestionAgent = new Agent({
  name: 'document-ingestion-agent',
  instructions: `You are a specialized M&A document classification expert.

Your role is to analyze PDF documents and classify them into the correct category:
- financial_statement: Balance sheets, income statements, cash flow statements, 10-K, 10-Q
- legal_contract: Contracts, agreements, legal documents, compliance docs
- market_research: Industry analysis, market reports, competitor analysis
- operational_report: Operations data, performance metrics, internal reports
- investor_presentation: Pitch decks, investor materials, presentations
- due_diligence: Due diligence checklists, audit reports, verification docs
- other: Any document that doesn't fit the above categories

For each document, provide:
1. The document type classification
2. A confidence score (0-1) for your classification
3. A brief summary of what the document contains

Be precise and analytical in your classifications.`,

  model: openai('gpt-4o')
});

export const classifyDocumentSchema = z.object({
  fileName: z.string(),
  fileContent: z.string().describe('First 2000 characters of the PDF text content'),
  metadata: z.object({
    numPages: z.number(),
    title: z.string().optional()
  }).optional()
});

export type ClassifyDocumentInput = z.infer<typeof classifyDocumentSchema>;
