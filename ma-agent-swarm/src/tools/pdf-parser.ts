import fs from 'fs/promises';
import pdfParse from 'pdf-parse';

export interface PDFContent {
  text: string;
  numPages: number;
  metadata: any;
}

/**
 * Extracts text content from a PDF file
 */
export async function parsePDF(filePath: string): Promise<PDFContent> {
  const dataBuffer = await fs.readFile(filePath);
  const data = await pdfParse(dataBuffer);

  return {
    text: data.text,
    numPages: data.numpages,
    metadata: data.metadata || {}
  };
}

/**
 * Tool definition for Mastra agents
 */
export const pdfParserTool = {
  id: 'parse-pdf',
  description: 'Extracts text content from PDF files',
  parameters: {
    type: 'object' as const,
    properties: {
      filePath: {
        type: 'string' as const,
        description: 'Path to the PDF file to parse'
      }
    },
    required: ['filePath']
  },
  execute: async ({ filePath }: { filePath: string }) => {
    return await parsePDF(filePath);
  }
};
