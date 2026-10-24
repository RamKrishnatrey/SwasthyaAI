/**
 * SwasthyaAI Agent Types
 * Integration contract for run_healthcare_agent(session_id, user_message, context)
 */

export type AgentStatus = 'idle' | 'thinking' | 'awaiting_input' | 'completed' | 'error' | 'escalated';

export type SafetyLevel = 'safe' | 'caution' | 'urgent' | 'emergency';

export interface AgentContext {
  sessionId: string;
  language?: 'en' | 'hi' | 'hinglish';
  userProfile?: {
    age?: number;
    gender?: 'male' | 'female' | 'other';
    conditions?: string[];
    medications?: string[];
  };
  conversationHistory?: ConversationTurn[];
  metadata?: Record<string, unknown>;
}

export interface ConversationTurn {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    safetyFlags?: SafetyFlag[];
    modelInfo?: ModelInfo;
    followUpQuestion?: string;
  };
}

export interface SafetyFlag {
  type: 'emergency' | 'urgent' | 'missing_data' | 'unsupported_language' | 'uncertainty' | 'contraindication';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  recommendedAction: string;
}

export interface ModelInfo {
  modelName: string;
  version: string;
  confidence?: number;
  predictionType: 'triage' | 'risk_assessment' | 'symptom_check' | 'general';
  limitations?: string[];
}

export interface AgentResponse {
  response: string;
  status: AgentStatus;
  safetyLevel: SafetyLevel;
  safetyFlags: SafetyFlag[];
  followUpQuestion?: string;
  modelInfo?: ModelInfo;
  structuredData?: {
    triageCategory?: 'emergency' | 'urgent' | 'semi-urgent' | 'non-urgent' | 'self-care';
    riskScore?: number;
    suggestedActions?: string[];
    recommendedSpecialty?: string;
    disclaimer: string;
  };
  sessionId: string;
  timestamp: string;
}

export interface AgentRequest {
  sessionId: string;
  userMessage: string;
  context?: AgentContext;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: AgentStatus;
  safetyLevel?: SafetyLevel;
  safetyFlags?: SafetyFlag[];
  followUpQuestion?: string;
  modelInfo?: ModelInfo;
  structuredData?: AgentResponse['structuredData'];
  isStreaming?: boolean;
}

export interface SessionState {
  sessionId: string;
  messages: ChatMessage[];
  status: AgentStatus;
  context: AgentContext;
  createdAt: Date;
  updatedAt: Date;
}