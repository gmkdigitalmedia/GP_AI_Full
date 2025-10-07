import { Agent } from '@mastra/core';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

/**
 * Transformation Agent
 *
 * Normalizes and structures extracted data into consistent formats
 * for analysis. Ensures data quality and consistency across documents.
 */
export const transformationAgent = new Agent({
  name: 'transformation-agent',
  instructions: `You are a data transformation and normalization specialist for M&A analysis.

Your role is to take raw extracted data and normalize it into structured, consistent formats:

1. STANDARDIZE FINANCIAL DATA:
   - Convert all currency values to USD (note conversion if needed)
   - Normalize time periods (ensure fiscal years align)
   - Calculate missing metrics from available data
   - Identify and flag any data quality issues

2. STRUCTURE DATA CONSISTENTLY:
   - Create uniform data schemas across all documents
   - Normalize naming conventions (e.g., "Revenue" vs "Sales" vs "Turnover")
   - Convert percentages and ratios to decimal format
   - Ensure all dates are in ISO format

3. QUALITY CHECKS:
   - Validate that numbers make sense (e.g., assets = liabilities + equity)
   - Flag any missing critical data points
   - Identify outliers or unusual values
   - Cross-reference data between related documents

4. ENRICH DATA:
   - Calculate derived metrics (e.g., margins, growth rates)
   - Add contextual information where helpful
   - Categorize data by importance (critical, important, nice-to-have)

Output should be clean, structured JSON with clear field names and consistent formatting.
Flag any data quality issues or missing information explicitly.`,

  model: openai('gpt-4o')
});

export const transformDataSchema = z.object({
  extractedDataArray: z.array(z.object({
    fileName: z.string(),
    documentType: z.string(),
    extractedContent: z.string().describe('Raw extracted data from extraction agent')
  }))
});

export type TransformDataInput = z.infer<typeof transformDataSchema>;
