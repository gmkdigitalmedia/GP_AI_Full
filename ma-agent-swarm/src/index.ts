#!/usr/bin/env node
import dotenv from 'dotenv';
import { runMAWorkflow } from './workflows/ma-workflow.js';
import path from 'path';

// Load environment variables
dotenv.config();

async function main() {
  // Check for OpenAI API key
  if (!process.env.OPENAI_API_KEY) {
    console.error('[ERROR] OPENAI_API_KEY not found in environment variables');
    console.error('Please create a .env file with your OpenAI API key');
    console.error('Example: OPENAI_API_KEY=sk-...');
    process.exit(1);
  }

  // Get PDF directory from command line or use default
  const pdfDirectory = process.argv[2] || path.join(process.cwd(), 'data/input');
  const targetCompanyName = process.argv[3];

  console.log('M&A Agent Swarm - Due Diligence System');
  console.log('==========================================\n');
  console.log(`PDF Directory: ${pdfDirectory}`);
  if (targetCompanyName) {
    console.log(`Target Company: ${targetCompanyName}`);
  }
  console.log('');

  const result = await runMAWorkflow({
    pdfDirectory,
    targetCompanyName
  });

  if (result.success) {
    console.log('\nSUCCESS!');
    console.log('=====================================');
    console.log(`Report: ${result.reportPath}`);
    if (result.summary) {
      console.log(`Documents Processed: ${result.summary.documentsProcessed}`);
      if (result.summary.dealScore) {
        console.log(`Deal Score: ${result.summary.dealScore}/100`);
      }
      if (result.summary.recommendation) {
        console.log(`Recommendation: ${result.summary.recommendation}`);
      }
    }
    console.log('=====================================\n');
  } else {
    console.error('\n[FAILED]');
    console.error('=====================================');
    console.error(`Error: ${result.error}`);
    console.error('=====================================\n');
    process.exit(1);
  }
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
