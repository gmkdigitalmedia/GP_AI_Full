import { z } from 'zod';

// Document classification types
export const DocumentType = z.enum([
  'financial_statement',
  'legal_contract',
  'market_research',
  'operational_report',
  'investor_presentation',
  'due_diligence',
  'other'
]);

export type DocumentType = z.infer<typeof DocumentType>;

// Input schema for document ingestion
export const DocumentInput = z.object({
  filePath: z.string(),
  fileName: z.string()
});

export type DocumentInput = z.infer<typeof DocumentInput>;

// Document classification output
export const DocumentClassification = z.object({
  fileName: z.string(),
  documentType: DocumentType,
  confidence: z.number().min(0).max(1),
  summary: z.string()
});

export type DocumentClassification = z.infer<typeof DocumentClassification>;

// Extracted data structure
export const ExtractedData = z.object({
  fileName: z.string(),
  documentType: DocumentType,
  rawText: z.string(),
  extractedTables: z.array(z.any()).optional(),
  metadata: z.record(z.any()).optional()
});

export type ExtractedData = z.infer<typeof ExtractedData>;

// Transformed/Normalized data
export const TransformedData = z.object({
  fileName: z.string(),
  documentType: DocumentType,
  structuredData: z.record(z.any()),
  keyMetrics: z.record(z.any()).optional(),
  riskFactors: z.array(z.string()).optional(),
  opportunities: z.array(z.string()).optional()
});

export type TransformedData = z.infer<typeof TransformedData>;

// Analysis outputs
export const FinancialAnalysis = z.object({
  valuation: z.string(),
  financialMetrics: z.record(z.any()),
  trends: z.array(z.string()),
  concerns: z.array(z.string()),
  strengths: z.array(z.string())
});

export type FinancialAnalysis = z.infer<typeof FinancialAnalysis>;

export const LegalRiskAnalysis = z.object({
  complianceIssues: z.array(z.string()),
  contractualRisks: z.array(z.string()),
  litigationConcerns: z.array(z.string()),
  recommendations: z.array(z.string())
});

export type LegalRiskAnalysis = z.infer<typeof LegalRiskAnalysis>;

export const MarketAnalysis = z.object({
  marketPosition: z.string(),
  competitiveLandscape: z.string(),
  synergies: z.array(z.string()),
  marketRisks: z.array(z.string()),
  growthOpportunities: z.array(z.string())
});

export type MarketAnalysis = z.infer<typeof MarketAnalysis>;

export const OperationalAnalysis = z.object({
  integrationComplexity: z.string(),
  culturalFit: z.string(),
  operationalRisks: z.array(z.string()),
  integrationPlan: z.array(z.string()),
  keyPersonnelRisks: z.array(z.string())
});

export type OperationalAnalysis = z.infer<typeof OperationalAnalysis>;

// Synthesized output
export const SynthesizedAnalysis = z.object({
  overallAssessment: z.string(),
  dealScore: z.number().min(0).max(100),
  keyFindings: z.array(z.string()),
  criticalRisks: z.array(z.string()),
  strategicBenefits: z.array(z.string()),
  recommendation: z.string()
});

export type SynthesizedAnalysis = z.infer<typeof SynthesizedAnalysis>;

// Final workflow output
export const MAWorkflowOutput = z.object({
  documentClassifications: z.array(DocumentClassification),
  extractedData: z.array(ExtractedData),
  transformedData: z.array(TransformedData),
  financialAnalysis: FinancialAnalysis,
  legalRiskAnalysis: LegalRiskAnalysis,
  marketAnalysis: MarketAnalysis,
  operationalAnalysis: OperationalAnalysis,
  synthesizedAnalysis: SynthesizedAnalysis,
  reportPath: z.string()
});

export type MAWorkflowOutput = z.infer<typeof MAWorkflowOutput>;
