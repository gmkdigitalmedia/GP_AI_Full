import { Mastra } from '@mastra/core';
import { createLogger } from '@mastra/core/logger';
import { LangfuseExporter } from 'langfuse-vercel';

/**
 * Mastra Configuration with Langfuse Observability
 *
 * This enables telemetry and logging to Langfuse dashboard
 * Get your keys from: https://cloud.langfuse.com
 */
export const mastra = new Mastra({
  telemetry: {
    serviceName: 'ai',
    enabled: !!process.env.LANGFUSE_SECRET_KEY, // Only enable if Langfuse is configured
    export: {
      type: 'custom',
      exporter: new LangfuseExporter({
        publicKey: process.env.LANGFUSE_PUBLIC_KEY!,
        secretKey: process.env.LANGFUSE_SECRET_KEY!,
        baseUrl: process.env.LANGFUSE_HOST || 'https://cloud.langfuse.com',
      }),
    },
  },
  logger: createLogger({
    level: 'info',
    type: 'pino'
  }),
});

export const logger = mastra.logger;
