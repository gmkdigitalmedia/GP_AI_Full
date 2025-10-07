#!/usr/bin/env node
/**
 * Simple test to see if agents actually work
 * Run with: npx tsx test-simple.ts
 */

import dotenv from 'dotenv';
import { documentIngestionAgent } from './src/agents/document-ingestion-agent.js';

dotenv.config();

async function simpleTest() {
  console.log('[TEST] Testing if M&A Agent Swarm actually works...\n');

  // Check OpenAI key
  if (!process.env.OPENAI_API_KEY) {
    console.error('[ERROR] OPENAI_API_KEY not found in .env file');
    console.error('Add your OpenAI API key to .env file first!');
    process.exit(1);
  }

  console.log('[OK] OpenAI API key found');
  console.log('[AGENT] Testing document ingestion agent...\n');

  try {
    // Simple test - just call one agent
    const result = await documentIngestionAgent.generateVNext(
      `Classify this document:

Filename: Q4_Financial_Report_2024.pdf
Number of Pages: 25

Content Preview:
CONSOLIDATED BALANCE SHEET
December 31, 2024

ASSETS
Current Assets:
  Cash and cash equivalents: $45,230,000
  Accounts receivable: $23,150,000
  Inventory: $12,890,000
  Total current assets: $81,270,000

Total Assets: $234,500,000

LIABILITIES
Current Liabilities:
  Accounts payable: $15,340,000
  Short-term debt: $8,200,000
  Total current liabilities: $23,540,000

Total Liabilities: $89,120,000

SHAREHOLDERS EQUITY: $145,380,000

Provide your classification in JSON format with documentType, confidence, and summary.`
    );

    console.log('[OK] Agent responded!\n');
    console.log('Report Response:');
    console.log('─'.repeat(60));
    console.log(result.text);
    console.log('─'.repeat(60));
    console.log('\n[OK] SUCCESS! The agent swarm is working!\n');
    console.log('Next steps:');
    console.log('1. Add real PDF files to data/input/');
    console.log('2. Run: npm start');
    console.log('3. Wait for the full workflow to complete');
    console.log('4. Check data/output/ for your PDF report\n');

  } catch (error) {
    console.error('\n[ERROR] FAILED!');
    console.error('Error:', error);
    process.exit(1);
  }
}

simpleTest();
