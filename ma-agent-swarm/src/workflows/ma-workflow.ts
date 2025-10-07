import fs from 'fs/promises';
import path from 'path';
import { documentIngestionAgent } from '../agents/document-ingestion-agent.js';
import { extractionAgent } from '../agents/extraction-agent.js';
import { transformationAgent } from '../agents/transformation-agent.js';
import { financialAnalysisAgent } from '../agents/financial-analysis-agent.js';
import { legalRiskAgent } from '../agents/legal-risk-agent.js';
import { marketAnalysisAgent } from '../agents/market-analysis-agent.js';
import { operationalAnalysisAgent } from '../agents/operational-analysis-agent.js';
import { synthesisAgent } from '../agents/synthesis-agent.js';
import { reportGenerationAgent } from '../agents/report-generation-agent.js';
import { parsePDF } from '../tools/pdf-parser.js';
import { generatePDFReport } from '../tools/pdf-generator.js';

export interface MAWorkflowInput {
  pdfDirectory: string; // Directory containing PDF files to analyze
  targetCompanyName?: string; // Optional name of target company
}

export interface MAWorkflowResult {
  success: boolean;
  reportPath?: string;
  error?: string;
  summary?: {
    documentsProcessed: number;
    dealScore?: number;
    recommendation?: string;
  };
}

/**
 * M&A Due Diligence Workflow
 *
 * Sequential pipeline:
 * 1. Document Ingestion - Classify PDFs
 * 2. Extraction - Extract raw data from each PDF
 * 3. Transformation - Normalize and structure data
 * 4. Analysis (Parallel) - Financial, Legal, Market, Operational
 * 5. Synthesis - Combine analyses into overall assessment
 * 6. Report Generation - Create PDF report
 */
export async function runMAWorkflow(input: MAWorkflowInput): Promise<MAWorkflowResult> {
  try {
    console.log('\n[SEARCH] Starting M&A Due Diligence Workflow');
    console.log('=====================================\n');

    // Step 1: Document Ingestion
    console.log('[STEP 1] Step 1: Document Ingestion & Classification');
    const pdfFiles = await fs.readdir(input.pdfDirectory);
    const pdfPaths = pdfFiles
      .filter((f) => f.endsWith('.pdf'))
      .map((f) => path.join(input.pdfDirectory, f));

    if (pdfPaths.length === 0) {
      throw new Error('No PDF files found in the specified directory');
    }

    console.log(`   Found ${pdfPaths.length} PDF files`);

    const documentClassifications = [];

    for (const pdfPath of pdfPaths) {
      const fileName = path.basename(pdfPath);
      console.log(`   - Classifying: ${fileName}`);

      const pdfContent = await parsePDF(pdfPath);
      const preview = pdfContent.text.substring(0, 2000);

      const classificationResult = await documentIngestionAgent.generateVNext(
        `Classify this document:

Filename: ${fileName}
Number of Pages: ${pdfContent.numPages}

Content Preview:
${preview}

Provide your classification in the following JSON format:
{
  "fileName": "${fileName}",
  "documentType": "one of: financial_statement, legal_contract, market_research, operational_report, investor_presentation, due_diligence, other",
  "confidence": 0.0 to 1.0,
  "summary": "brief summary of document contents"
}`
      );

      try {
        const classification = JSON.parse(classificationResult.text);
        documentClassifications.push(classification);
        console.log(`     OK Classified as: ${classification.documentType} (confidence: ${classification.confidence})`);
      } catch (e) {
        console.log(`     X Failed to parse classification, using raw response`);
        documentClassifications.push({
          fileName,
          documentType: 'other',
          confidence: 0.5,
          summary: classificationResult.text
        });
      }
    }

    // Save classifications
    await fs.writeFile(
      path.join(process.cwd(), 'data/extracted/classifications.json'),
      JSON.stringify(documentClassifications, null, 2)
    );

    // Step 2: Extraction
    console.log('\n[STEP 2] Step 2: Data Extraction');
    const extractedDataArray = [];

    for (let i = 0; i < pdfPaths.length; i++) {
      const pdfPath = pdfPaths[i];
      const classification = documentClassifications[i];
      const fileName = path.basename(pdfPath);

      console.log(`   - Extracting data from: ${fileName}`);

      const pdfContent = await parsePDF(pdfPath);

      const extractionResult = await extractionAgent.generateVNext(
        `Extract structured data from this ${classification.documentType} document:

Filename: ${fileName}
Document Type: ${classification.documentType}

Full Content:
${pdfContent.text}

Extract all relevant data points according to the document type. Return as structured JSON.`
      );

      const extractedData = {
        fileName,
        documentType: classification.documentType,
        rawText: pdfContent.text,
        extractedContent: extractionResult.text
      };

      extractedDataArray.push(extractedData);
      console.log(`     OK Extracted data from ${fileName}`);
    }

    // Save extracted data
    await fs.writeFile(
      path.join(process.cwd(), 'data/extracted/extracted_data.json'),
      JSON.stringify(extractedDataArray, null, 2)
    );

    // Step 3: Transformation
    console.log('\n[STEP 3] Step 3: Data Transformation & Normalization');

    const transformationResult = await transformationAgent.generateVNext(
      `Normalize and structure the following extracted data from multiple documents:

${JSON.stringify(extractedDataArray, null, 2)}

Create a unified, normalized data structure. Ensure consistency across documents. Output as clean JSON.`
    );

    const transformedData = transformationResult.text;

    await fs.writeFile(
      path.join(process.cwd(), 'data/extracted/transformed_data.json'),
      transformedData
    );
    console.log('   OK Data transformation complete');

    // Step 4: Analysis (Running in parallel for efficiency)
    console.log('\n[STEP 4] Step 4: Multi-Dimensional Analysis');
    console.log('   Running Financial, Legal, Market, and Operational analyses in parallel...');

    const [financialResult, legalResult, marketResult, operationalResult] = await Promise.all([
      financialAnalysisAgent.generateVNext(`Perform comprehensive financial analysis:\n\n${transformedData}`),
      legalRiskAgent.generateVNext(`Perform legal and risk analysis:\n\n${transformedData}`),
      marketAnalysisAgent.generateVNext(`Perform market and competitive analysis:\n\n${transformedData}`),
      operationalAnalysisAgent.generateVNext(`Perform operational analysis:\n\n${transformedData}`)
    ]);

    console.log('   OK Financial analysis complete');
    console.log('   OK Legal/risk analysis complete');
    console.log('   OK Market analysis complete');
    console.log('   OK Operational analysis complete');

    // Save individual analyses
    await fs.writeFile(
      path.join(process.cwd(), 'data/output/financial_analysis.json'),
      JSON.stringify({ analysis: financialResult.text }, null, 2)
    );
    await fs.writeFile(
      path.join(process.cwd(), 'data/output/legal_risk_analysis.json'),
      JSON.stringify({ analysis: legalResult.text }, null, 2)
    );
    await fs.writeFile(
      path.join(process.cwd(), 'data/output/market_analysis.json'),
      JSON.stringify({ analysis: marketResult.text }, null, 2)
    );
    await fs.writeFile(
      path.join(process.cwd(), 'data/output/operational_analysis.json'),
      JSON.stringify({ analysis: operationalResult.text }, null, 2)
    );

    // Step 5: Synthesis
    console.log('\n[STEP 5] Step 5: Synthesis & Overall Assessment');

    const synthesisResult = await synthesisAgent.generateVNext(
      `Synthesize the following analyses into an overall M&A assessment:

FINANCIAL ANALYSIS:
${financialResult.text}

LEGAL/RISK ANALYSIS:
${legalResult.text}

MARKET ANALYSIS:
${marketResult.text}

OPERATIONAL ANALYSIS:
${operationalResult.text}

Provide: overall assessment, deal score (0-100), key findings, critical risks, strategic benefits, and clear recommendation.`
    );

    console.log('   OK Synthesis complete');

    await fs.writeFile(
      path.join(process.cwd(), 'data/output/synthesis.json'),
      JSON.stringify({ synthesis: synthesisResult.text }, null, 2)
    );

    // Step 6: Report Generation
    console.log('\n[STEP 6] Step 6: Generating PDF Report');

    const reportContentResult = await reportGenerationAgent.generateVNext(
      `Generate a comprehensive M&A due diligence report:

TARGET COMPANY: ${input.targetCompanyName || 'Target Company'}

DOCUMENTS ANALYZED:
${documentClassifications.map(d => `- ${d.fileName} (${d.documentType})`).join('\n')}

SYNTHESIZED ANALYSIS:
${synthesisResult.text}

FINANCIAL ANALYSIS:
${financialResult.text}

LEGAL/RISK ANALYSIS:
${legalResult.text}

MARKET ANALYSIS:
${marketResult.text}

OPERATIONAL ANALYSIS:
${operationalResult.text}

Create a well-structured report with clear sections and professional formatting.`
    );

    // Parse report content and generate PDF
    const reportText = reportContentResult.text;
    const sections = parseReportSections(reportText);

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const reportFileName = `MA_Due_Diligence_Report_${timestamp}.pdf`;
    const reportPath = path.join(process.cwd(), 'data/output', reportFileName);

    await generatePDFReport(
      {
        title: `M&A Due Diligence Report\n${input.targetCompanyName || 'Target Company'}`,
        date: new Date().toLocaleDateString(),
        sections
      },
      reportPath
    );

    console.log(`   OK PDF report generated: ${reportFileName}`);
    console.log('\n[OK] M&A Workflow Complete!\n');
    console.log(`Report saved to: ${reportPath}`);

    // Extract deal score and recommendation for summary
    const dealScoreMatch = synthesisResult.text.match(/deal score[:\s]+(\d+)/i);
    const recommendationMatch = synthesisResult.text.match(/recommendation[:\s]+([^\n]+)/i);

    return {
      success: true,
      reportPath,
      summary: {
        documentsProcessed: pdfPaths.length,
        dealScore: dealScoreMatch ? parseInt(dealScoreMatch[1]) : undefined,
        recommendation: recommendationMatch ? recommendationMatch[1].trim() : undefined
      }
    };

  } catch (error) {
    console.error('\n[ERROR] Workflow failed:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

/**
 * Helper function to parse report text into sections
 */
function parseReportSections(reportText: string): Array<{ title: string; content: string }> {
  const sections: Array<{ title: string; content: string }> = [];

  // Split by common section headers (looking for numbered sections or all-caps headers)
  const lines = reportText.split('\n');
  let currentSection: { title: string; content: string } | null = null;

  for (const line of lines) {
    // Check if line is a section header (various patterns)
    const isHeader =
      /^\d+\.\s+[A-Z]/.test(line) || // "1. EXECUTIVE SUMMARY"
      /^#{1,3}\s+/.test(line) ||      // "## Executive Summary"
      (/^[A-Z][A-Z\s&]+$/.test(line) && line.length < 60); // "EXECUTIVE SUMMARY"

    if (isHeader) {
      if (currentSection) {
        sections.push(currentSection);
      }
      currentSection = {
        title: line.replace(/^#+\s+/, '').replace(/^\d+\.\s+/, '').trim(),
        content: ''
      };
    } else if (currentSection) {
      currentSection.content += line + '\n';
    }
  }

  if (currentSection) {
    sections.push(currentSection);
  }

  // If no sections were found, create one big section
  if (sections.length === 0) {
    sections.push({
      title: 'M&A Due Diligence Report',
      content: reportText
    });
  }

  return sections;
}
