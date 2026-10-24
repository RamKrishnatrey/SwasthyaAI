import { NextRequest, NextResponse } from 'next/server';
import { AgentRequest, AgentResponse, AgentStatus, SafetyLevel, SafetyFlag, ModelInfo } from '@/types/agent';

/**
 * SwasthyaAI Agent API Endpoint
 *
 * This is the integration point for Member 3's backend.
 * The actual agent logic should be implemented in the backend service.
 * This route serves as a proxy/mock for frontend development.
 *
 * Expected integration: POST /api/agent
 * Request: AgentRequest
 * Response: AgentResponse
 */

// Mock responses for development/demo purposes
const MOCK_RESPONSES: Record<string, Partial<AgentResponse>> = {
  'chest pain': {
    response: 'Chest pain can be a sign of serious conditions like a heart attack. This requires immediate medical evaluation.',
    status: 'escalated' as AgentStatus,
    safetyLevel: 'emergency' as SafetyLevel,
    safetyFlags: [
      {
        type: 'emergency',
        severity: 'critical',
        message: 'Chest pain may indicate a heart attack or other life-threatening condition.',
        recommendedAction: 'Call emergency services (112/108) immediately or go to the nearest emergency department.',
      },
    ],
    structuredData: {
      triageCategory: 'emergency' as const,
      riskScore: 0.95,
      suggestedActions: ['Call 112/108 immediately', 'Do not drive yourself', 'Chew aspirin if not allergic'],
      disclaimer: 'This is not medical advice. Seek immediate professional medical care.',
    },
  },
  'difficulty breathing': {
    response: 'Difficulty breathing is a serious symptom that needs urgent medical attention.',
    status: 'escalated' as AgentStatus,
    safetyLevel: 'emergency' as SafetyLevel,
    safetyFlags: [
      {
        type: 'emergency',
        severity: 'critical',
        message: 'Breathing difficulty can indicate severe respiratory or cardiac issues.',
        recommendedAction: 'Call emergency services (112/108) immediately.',
      },
    ],
    structuredData: {
      triageCategory: 'emergency' as const,
      riskScore: 0.9,
      suggestedActions: ['Call 112/108', 'Sit upright', 'Loosen tight clothing'],
      disclaimer: 'This is not medical advice. Seek immediate professional medical care.',
    },
  },
  'headache': {
    response: 'Headaches can have many causes. To help me understand better: How long have you had this headache? Is it on one side or both? Any nausea, vision changes, or neck stiffness?',
    status: 'awaiting_input' as AgentStatus,
    safetyLevel: 'caution' as SafetyLevel,
    safetyFlags: [
      {
        type: 'missing_data',
        severity: 'medium',
        message: 'Need more information to assess headache severity.',
        recommendedAction: 'Please answer the follow-up questions.',
      },
    ],
    followUpQuestion: 'How long have you had this headache? Is it on one side or both? Any nausea, vision changes, or neck stiffness?',
    structuredData: {
      triageCategory: 'non-urgent' as const,
      riskScore: 0.3,
      suggestedActions: ['Track headache patterns', 'Stay hydrated', 'Rest in a quiet, dark room'],
      disclaimer: 'This is not a diagnosis. Consult a healthcare provider for persistent headaches.',
    },
    modelInfo: {
      modelName: 'SwasthyaAI-Triage-v1',
      version: '1.0.0',
      confidence: 0.75,
      predictionType: 'symptom_check',
      limitations: ['Cannot diagnose', 'Limited by self-reported symptoms', 'Not a substitute for clinical evaluation'],
    },
  },
  'fever': {
    response: 'Fever indicates your body is fighting an infection. How high is the fever? How long have you had it? Any other symptoms like cough, rash, or pain?',
    status: 'awaiting_input' as AgentStatus,
    safetyLevel: 'caution' as SafetyLevel,
    safetyFlags: [
      {
        type: 'missing_data',
        severity: 'medium',
        message: 'Need temperature reading and duration to assess urgency.',
        recommendedAction: 'Please provide fever details and any other symptoms.',
      },
    ],
    followUpQuestion: 'What is your temperature? How long have you had the fever? Any other symptoms like cough, rash, body aches, or urinary symptoms?',
    structuredData: {
      triageCategory: 'semi-urgent' as const,
      riskScore: 0.5,
      suggestedActions: ['Monitor temperature', 'Stay hydrated', 'Rest'],
      disclaimer: 'This is not a diagnosis. Seek medical care if fever exceeds 103°F (39.4°C) or lasts more than 3 days.',
    },
    modelInfo: {
      modelName: 'SwasthyaAI-Triage-v1',
      version: '1.0.0',
      confidence: 0.8,
      predictionType: 'symptom_check',
      limitations: ['Cannot diagnose specific infection', 'Requires temperature measurement'],
    },
  },
  'stomach': {
    response: 'Stomach pain after eating could be indigestion, acid reflux, food intolerance, or other issues. Is the pain burning, cramping, or sharp? Any nausea, vomiting, or changes in bowel movements?',
    status: 'awaiting_input' as AgentStatus,
    safetyLevel: 'safe' as SafetyLevel,
    safetyFlags: [
      {
        type: 'missing_data',
        severity: 'low',
        message: 'Need more details about pain characteristics.',
        recommendedAction: 'Please describe the pain type and any associated symptoms.',
      },
    ],
    followUpQuestion: 'Is the pain burning, cramping, or sharp? Any nausea, vomiting, bloating, or changes in bowel movements?',
    structuredData: {
      triageCategory: 'non-urgent' as const,
      riskScore: 0.25,
      suggestedActions: ['Avoid trigger foods', 'Eat smaller meals', 'Stay upright after eating'],
      disclaimer: 'This is not a diagnosis. Consult a doctor if pain is severe, persistent, or accompanied by blood in stool.',
    },
    modelInfo: {
      modelName: 'SwasthyaAI-Triage-v1',
      version: '1.0.0',
      confidence: 0.7,
      predictionType: 'symptom_check',
      limitations: ['Cannot differentiate between GI conditions', 'Requires physical exam for accurate assessment'],
    },
  },
  'sleep': {
    response: 'Sleep difficulties can affect your overall health. How long has this been going on? Do you have trouble falling asleep, staying asleep, or waking too early? Any stress, caffeine, or screen use before bed?',
    status: 'awaiting_input' as AgentStatus,
    safetyLevel: 'safe' as SafetyLevel,
    safetyFlags: [
      {
        type: 'missing_data',
        severity: 'low',
        message: 'Need more details about sleep pattern.',
        recommendedAction: 'Please describe your sleep issues and habits.',
      },
    ],
    followUpQuestion: 'Do you have trouble falling asleep, staying asleep, or waking too early? Any stress, caffeine, alcohol, or screen use before bed?',
    structuredData: {
      triageCategory: 'self-care' as const,
      riskScore: 0.2,
      suggestedActions: ['Maintain consistent sleep schedule', 'Limit caffeine after 2 PM', 'Reduce screen time before bed', 'Create a relaxing bedtime routine'],
      disclaimer: 'This is not medical advice. Consult a healthcare provider if insomnia persists beyond 4 weeks.',
    },
    modelInfo: {
      modelName: 'SwasthyaAI-Triage-v1',
      version: '1.0.0',
      confidence: 0.85,
      predictionType: 'general',
      limitations: ['Cannot diagnose sleep disorders', 'CBT-I may be needed for chronic insomnia'],
    },
  },
};

function findMockResponse(message: string): Partial<AgentResponse> | null {
  const lower = message.toLowerCase();

  // Check for emergency keywords first
  if (/(chest pain|heart attack|can't breathe|difficulty breathing|shortness of breath|suicide|kill myself)/i.test(lower)) {
    if (lower.includes('chest') || lower.includes('heart')) return MOCK_RESPONSES['chest pain'];
    if (lower.includes('breath') || lower.includes('breathing')) return MOCK_RESPONSES['difficulty breathing'];
  }

  // Check other keywords
  for (const [keyword, response] of Object.entries(MOCK_RESPONSES)) {
    if (lower.includes(keyword)) {
      return response;
    }
  }

  return null;
}

function generateDefaultResponse(message: string): Partial<AgentResponse> {
  return {
    response: `Thank you for sharing that. I understand you're experiencing "${message}". To help me provide better guidance, could you tell me more about:\n\n1. When did this start?\n2. How severe is it on a scale of 1-10?\n3. Any other symptoms?\n4. Any existing medical conditions or medications?`,
    status: 'awaiting_input' as AgentStatus,
    safetyLevel: 'safe' as SafetyLevel,
    safetyFlags: [
      {
        type: 'missing_data',
        severity: 'low',
        message: 'Initial assessment requires more information.',
        recommendedAction: 'Please provide details about onset, severity, and associated symptoms.',
      },
    ],
    followUpQuestion: 'When did this start? How severe (1-10)? Any other symptoms or existing conditions?',
    structuredData: {
      triageCategory: 'non-urgent' as const,
      riskScore: 0.3,
      suggestedActions: ['Monitor symptoms', 'Note any changes', 'Prepare details for healthcare provider'],
      disclaimer: 'This is not medical advice. This tool provides general health information only.',
    },
    modelInfo: {
      modelName: 'SwasthyaAI-Triage-v1',
      version: '1.0.0',
      confidence: 0.6,
      predictionType: 'general',
      limitations: ['Generic response - needs more specific symptoms', 'Cannot provide diagnosis'],
    },
  };
}

export async function POST(request: NextRequest) {
  try {
    const body: AgentRequest = await request.json();

    // Validate request
    if (!body.sessionId || !body.userMessage) {
      return NextResponse.json(
        { error: 'Missing required fields: sessionId, userMessage' },
        { status: 400 }
      );
    }

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));

    // Find matching mock response or generate default
    const mockResponse = findMockResponse(body.userMessage) || generateDefaultResponse(body.userMessage);

    // Build complete response
    const response: AgentResponse = {
      sessionId: body.sessionId,
      timestamp: new Date().toISOString(),
      response: mockResponse.response || 'I understand. Could you provide more details?',
      status: mockResponse.status || 'awaiting_input',
      safetyLevel: mockResponse.safetyLevel || 'safe',
      safetyFlags: mockResponse.safetyFlags || [],
      followUpQuestion: mockResponse.followUpQuestion,
      modelInfo: mockResponse.modelInfo,
      structuredData: mockResponse.structuredData,
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Agent API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Handle OPTIONS for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}