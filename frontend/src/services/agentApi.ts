import type { AgentRequest, AgentResponse } from '../types/agent';
import { createDemoResponse } from './demoFixtures';

const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true';
const configuredBaseUrl = ((import.meta.env.VITE_API_BASE_URL as string | undefined) || 'http://127.0.0.1:8001').replace(/\/$/, '');

export class AgentApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'AgentApiError';
  }
}

/** Calls the agreed backend contract; demo responses are used only when VITE_DEMO_MODE=true. */
export async function sendAgentMessage(request: AgentRequest, turnCount: number): Promise<AgentResponse> {
  if (isDemoMode) {
    return createDemoResponse(request, turnCount);
  }

  if (!configuredBaseUrl) {
    throw new AgentApiError('API URL is missing. Set VITE_API_BASE_URL in your environment.');
  }

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 20_000);
  try {
    const response = await fetch(`${configuredBaseUrl}/api/agent/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: controller.signal,
    });
    if (!response.ok) {
      throw new AgentApiError(`The agent API returned HTTP ${response.status}.`, response.status);
    }
    const payload = (await response.json()) as Omit<AgentResponse, 'source'>;
    if (!payload || typeof payload.status !== 'string' || typeof payload.response !== 'string') {
      throw new AgentApiError('The agent API returned an unexpected response shape.');
    }
    return { ...payload, source: 'api' };
  } catch (error) {
    if (error instanceof AgentApiError) throw error;
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new AgentApiError('The agent took too long to respond. Please retry or use the configured support path.');
    }
    throw new AgentApiError('Could not reach SwasthyaAI. No live result was generated. Please retry.');
  } finally {
    window.clearTimeout(timeoutId);
  }
}
