#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

import { GmailService } from './services/gmail.js';
import { CalendarService } from './services/calendar.js';
import { ContactService } from './services/contacts.js';
import { TemplateService } from './services/templates.js';
import { AnalyticsService } from './services/analytics.js';
import { LinkedInService } from './services/linkedin.js';

interface MarketingMCPConfig {
  googleCredentialsPath?: string;
  databasePath?: string;
}

class MarketingMCPServer {
  private server: Server;
  private gmailService: GmailService;
  private calendarService: CalendarService;
  private contactService: ContactService;
  private templateService: TemplateService;
  private analyticsService: AnalyticsService;
  private linkedinService: LinkedInService;

  constructor(config: MarketingMCPConfig = {}) {
    this.server = new Server(
      {
        name: 'marketing-mcp-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    // Initialize services
    this.gmailService = new GmailService(config.googleCredentialsPath);
    this.calendarService = new CalendarService(config.googleCredentialsPath);
    this.contactService = new ContactService(config.databasePath);
    this.templateService = new TemplateService(config.databasePath);
    this.analyticsService = new AnalyticsService(config.databasePath);
    this.linkedinService = new LinkedInService();

    this.setupToolHandlers();
  }

  private setupToolHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          // Gmail Tools
          {
            name: 'send_email',
            description: 'Send a personalized email to a contact',
            inputSchema: {
              type: 'object',
              properties: {
                to: { type: 'string', description: 'Recipient email address' },
                subject: { type: 'string', description: 'Email subject line' },
                body: { type: 'string', description: 'Email body content' },
                templateId: { type: 'string', description: 'Optional template ID to use' },
                variables: { type: 'object', description: 'Variables for template substitution' },
              },
              required: ['to', 'subject', 'body'],
            },
          },
          {
            name: 'schedule_follow_up',
            description: 'Schedule a follow-up email for later',
            inputSchema: {
              type: 'object',
              properties: {
                contactId: { type: 'string', description: 'Contact ID' },
                templateId: { type: 'string', description: 'Email template to use' },
                scheduleDate: { type: 'string', description: 'When to send (ISO date)' },
                variables: { type: 'object', description: 'Template variables' },
              },
              required: ['contactId', 'templateId', 'scheduleDate'],
            },
          },

          // Calendar Tools
          {
            name: 'create_meeting',
            description: 'Create a calendar meeting with automatic scheduling links',
            inputSchema: {
              type: 'object',
              properties: {
                title: { type: 'string', description: 'Meeting title' },
                description: { type: 'string', description: 'Meeting description' },
                duration: { type: 'number', description: 'Duration in minutes' },
                attendeeEmail: { type: 'string', description: 'Attendee email address' },
                availableSlots: { type: 'array', items: { type: 'string' }, description: 'Available time slots' },
              },
              required: ['title', 'duration', 'attendeeEmail'],
            },
          },
          {
            name: 'get_availability',
            description: 'Get your calendar availability for scheduling',
            inputSchema: {
              type: 'object',
              properties: {
                startDate: { type: 'string', description: 'Start date (ISO format)' },
                endDate: { type: 'string', description: 'End date (ISO format)' },
                workingHours: { type: 'object', description: 'Working hours preference' },
              },
              required: ['startDate', 'endDate'],
            },
          },

          // Contact Management Tools
          {
            name: 'add_contact',
            description: 'Add a new contact to the CRM system',
            inputSchema: {
              type: 'object',
              properties: {
                name: { type: 'string', description: 'Contact full name' },
                email: { type: 'string', description: 'Contact email address' },
                company: { type: 'string', description: 'Company name' },
                position: { type: 'string', description: 'Job position' },
                linkedinUrl: { type: 'string', description: 'LinkedIn profile URL' },
                tags: { type: 'array', items: { type: 'string' }, description: 'Contact tags' },
                source: { type: 'string', description: 'How you found this contact' },
              },
              required: ['name', 'email'],
            },
          },
          {
            name: 'update_contact_status',
            description: 'Update contact status in sales pipeline',
            inputSchema: {
              type: 'object',
              properties: {
                contactId: { type: 'string', description: 'Contact ID' },
                status: { type: 'string', enum: ['cold', 'contacted', 'responded', 'interested', 'meeting_scheduled', 'closed'], description: 'New contact status' },
                notes: { type: 'string', description: 'Additional notes' },
              },
              required: ['contactId', 'status'],
            },
          },
          {
            name: 'search_contacts',
            description: 'Search contacts by various criteria',
            inputSchema: {
              type: 'object',
              properties: {
                query: { type: 'string', description: 'Search query' },
                company: { type: 'string', description: 'Filter by company' },
                status: { type: 'string', description: 'Filter by status' },
                tags: { type: 'array', items: { type: 'string' }, description: 'Filter by tags' },
                limit: { type: 'number', description: 'Max results to return' },
              },
            },
          },

          // Template Management Tools
          {
            name: 'create_template',
            description: 'Create a new email template',
            inputSchema: {
              type: 'object',
              properties: {
                name: { type: 'string', description: 'Template name' },
                subject: { type: 'string', description: 'Email subject template' },
                body: { type: 'string', description: 'Email body template with variables' },
                category: { type: 'string', description: 'Template category (outreach, follow-up, etc.)' },
                variables: { type: 'array', items: { type: 'string' }, description: 'Available variables' },
              },
              required: ['name', 'subject', 'body'],
            },
          },
          {
            name: 'get_templates',
            description: 'Get all available email templates',
            inputSchema: {
              type: 'object',
              properties: {
                category: { type: 'string', description: 'Filter by category' },
              },
            },
          },

          // LinkedIn Tools
          {
            name: 'extract_linkedin_profile',
            description: 'Extract information from LinkedIn profile URL',
            inputSchema: {
              type: 'object',
              properties: {
                profileUrl: { type: 'string', description: 'LinkedIn profile URL' },
              },
              required: ['profileUrl'],
            },
          },
          {
            name: 'generate_personalized_message',
            description: 'Generate personalized outreach message based on LinkedIn profile',
            inputSchema: {
              type: 'object',
              properties: {
                profileData: { type: 'object', description: 'LinkedIn profile data' },
                templateId: { type: 'string', description: 'Template to use as base' },
                tone: { type: 'string', enum: ['professional', 'casual', 'friendly'], description: 'Message tone' },
              },
              required: ['profileData'],
            },
          },

          // Analytics Tools
          {
            name: 'get_campaign_stats',
            description: 'Get email campaign performance statistics',
            inputSchema: {
              type: 'object',
              properties: {
                campaignId: { type: 'string', description: 'Campaign ID' },
                dateRange: { type: 'object', description: 'Date range for stats' },
              },
            },
          },
          {
            name: 'generate_report',
            description: 'Generate comprehensive outreach performance report',
            inputSchema: {
              type: 'object',
              properties: {
                reportType: { type: 'string', enum: ['weekly', 'monthly', 'campaign', 'contact'], description: 'Type of report' },
                format: { type: 'string', enum: ['json', 'csv', 'summary'], description: 'Report format' },
                dateRange: { type: 'object', description: 'Date range for report' },
              },
              required: ['reportType'],
            },
          },
        ] as Tool[],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          // Gmail tool handlers
          case 'send_email':
            return await this.gmailService.sendEmail(args);
          case 'schedule_follow_up':
            return await this.gmailService.scheduleFollowUp(args);

          // Calendar tool handlers
          case 'create_meeting':
            return await this.calendarService.createMeeting(args);
          case 'get_availability':
            return await this.calendarService.getAvailability(args);

          // Contact tool handlers
          case 'add_contact':
            return await this.contactService.addContact(args);
          case 'update_contact_status':
            return await this.contactService.updateContactStatus(args);
          case 'search_contacts':
            return await this.contactService.searchContacts(args);

          // Template tool handlers
          case 'create_template':
            return await this.templateService.createTemplate(args);
          case 'get_templates':
            return await this.templateService.getTemplates(args);

          // LinkedIn tool handlers
          case 'extract_linkedin_profile':
            return await this.linkedinService.extractProfile(args);
          case 'generate_personalized_message':
            return await this.linkedinService.generatePersonalizedMessage(args);

          // Analytics tool handlers
          case 'get_campaign_stats':
            return await this.analyticsService.getCampaignStats(args);
          case 'generate_report':
            return await this.analyticsService.generateReport(args);

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error executing ${name}: ${error instanceof Error ? error.message : String(error)}`,
            },
          ],
          isError: true,
        };
      }
    });
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Marketing MCP Server running on stdio');
  }
}

// CLI entry point
if (import.meta.url === `file://${process.argv[1]}`) {
  const config: MarketingMCPConfig = {
    googleCredentialsPath: process.env.GOOGLE_CREDENTIALS_PATH,
    databasePath: process.env.DATABASE_PATH || './marketing.db',
  };

  const server = new MarketingMCPServer(config);
  server.run().catch((error) => {
    console.error('Server error:', error);
    process.exit(1);
  });
}

export { MarketingMCPServer };