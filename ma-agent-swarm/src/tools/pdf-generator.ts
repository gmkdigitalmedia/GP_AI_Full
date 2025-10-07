import PDFDocument from 'pdfkit';
import fs from 'fs';

export interface ReportSection {
  title: string;
  content: string;
}

export interface MAReport {
  title: string;
  date: string;
  sections: ReportSection[];
}

/**
 * Generates a PDF report from M&A analysis data
 */
export async function generatePDFReport(
  report: MAReport,
  outputPath: string
): Promise<string> {
  return new Promise((resolve, reject) => {
    const doc = new PDFDocument({
      size: 'LETTER',
      margins: { top: 50, bottom: 50, left: 50, right: 50 }
    });

    const stream = fs.createWriteStream(outputPath);
    doc.pipe(stream);

    // Title page
    doc
      .fontSize(24)
      .font('Helvetica-Bold')
      .text(report.title, { align: 'center' });

    doc
      .moveDown()
      .fontSize(12)
      .font('Helvetica')
      .text(`Generated: ${report.date}`, { align: 'center' });

    doc.addPage();

    // Table of contents
    doc
      .fontSize(18)
      .font('Helvetica-Bold')
      .text('Table of Contents');

    doc.moveDown();
    doc.fontSize(12).font('Helvetica');

    report.sections.forEach((section, idx) => {
      doc.text(`${idx + 1}. ${section.title}`);
    });

    // Sections
    report.sections.forEach((section, idx) => {
      doc.addPage();

      doc
        .fontSize(18)
        .font('Helvetica-Bold')
        .text(`${idx + 1}. ${section.title}`);

      doc.moveDown();

      // Process content - handle lists and paragraphs
      const lines = section.content.split('\n');
      doc.fontSize(11).font('Helvetica');

      lines.forEach((line) => {
        if (line.trim() === '') {
          doc.moveDown(0.5);
        } else if (line.trim().startsWith('-') || line.trim().startsWith('•')) {
          doc.text(line, { indent: 20 });
        } else if (line.trim().match(/^\d+\./)) {
          doc.text(line, { indent: 20 });
        } else if (line.trim().startsWith('#')) {
          const headerText = line.replace(/^#+\s*/, '');
          doc.fontSize(14).font('Helvetica-Bold').text(headerText);
          doc.fontSize(11).font('Helvetica');
        } else {
          doc.text(line);
        }
      });
    });

    doc.end();

    stream.on('finish', () => {
      resolve(outputPath);
    });

    stream.on('error', (error) => {
      reject(error);
    });
  });
}

/**
 * Tool definition for Mastra agents
 */
export const pdfGeneratorTool = {
  id: 'generate-pdf-report',
  description: 'Generates a PDF report from M&A analysis data',
  parameters: {
    type: 'object' as const,
    properties: {
      report: {
        type: 'object' as const,
        description: 'Report data containing title, date, and sections'
      },
      outputPath: {
        type: 'string' as const,
        description: 'Path where the PDF should be saved'
      }
    },
    required: ['report', 'outputPath']
  },
  execute: async ({ report, outputPath }: { report: MAReport; outputPath: string }) => {
    return await generatePDFReport(report, outputPath);
  }
};
