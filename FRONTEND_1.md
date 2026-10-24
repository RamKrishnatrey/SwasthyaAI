# SwasthyaAI Frontend - Complete Code Documentation

## Project Overview
A professional healthcare triage dashboard built with Next.js 16, React 19, TypeScript, and Tailwind CSS 4. Features structured symptom input, AI-powered triage assessment, safety escalation, patient queue management, and multi-language support (English, Hindi, Hinglish).

## File Structure
```
SwasthyaAI/frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main dashboard
│   │   ├── layout.tsx            # Root layout with metadata
│   │   ├── globals.css           # Tailwind v4 + accessibility styles
│   │   └── api/agent/route.ts    # Mock API endpoint
│   ├── components/
│   │   ├── triage/
│   │   │   ├── TriageForm.tsx           # Structured symptom input form
│   │   │   ├── TriageResults.tsx        # Assessment results display
│   │   │   ├── SafetyAlert.tsx          # Emergency/warning banners
│   │   │   ├── FollowUpSection.tsx      # Interactive follow-up questions
│   │   │   ├── PatientQueue.tsx         # Patient queue with priority
│   │   │   ├── ResourcePanel.tsx        # Context-aware resources
│   │   │   ├── LanguageSelector.tsx     # EN/HI/Hinglish selector
│   │   │   ├── ModelInfoPanel.tsx       # Model transparency panel
│   │   │   └── index.ts                 # Barrel exports
│   │   └── layout/
│   │       └── Header.tsx               # Sticky header with status & language
│   ├── hooks/
│   │   └── useTriageSession.ts          # Core state management
│   ├── lib/
│   │   └── utils.ts                      # Helper functions
│   └── types/
│       └── agent.ts                      # TypeScript types for integration
├── package.json
├── tsconfig.json
├── next.config.ts
├── eslint.config.mjs
└── .gitignore
```

---

## Core Files Content

### 1. src/app/page.tsx - Main Dashboard
```tsx
'use client';

import React from 'react';
import { Header } from '@/components/layout/Header';
import { 
  TriageForm, 
  TriageResults, 
  SafetyAlert, 
  FollowUpSection, 
  PatientQueue, 
  ResourcePanel, 
  LanguageSelector, 
  ModelInfoPanel 
} from '@/components/triage';
import { useTriageSession } from '@/hooks/useTriageSession';

export default function TriageDashboard() {
  const {
    state,
    submitAssessment,
    answerFollowUp,
    skipFollowUp,
    addToQueue,
    clearResults,
    setLanguage,
  } = useTriageSession();

  return (
    <div className="flex flex-col h-screen bg-background">
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <Header
        sessionStatus={state.status}
        currentLanguage={state.language}
        onLanguageChange={setLanguage}
        onNewAssessment={clearResults}
      />

      <main id="main-content" className="flex-1 overflow-auto" role="main">
        <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
          <LanguageSelector
            currentLanguage={state.language}
            onChange={setLanguage}
            disabled={state.status === 'processing'}
          />

          {state.safetyAlert && (
            <SafetyAlert alert={state.safetyAlert} onDismiss={() => {}} />
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-6">
              {!state.results && (
                <TriageForm
                  onSubmit={submitAssessment}
                  disabled={state.status === 'processing'}
                  language={state.language}
                  prefillData={state.prefillData}
                />
              )}

              {state.followUpQuestion && (
                <FollowUpSection
                  question={state.followUpQuestion}
                  onAnswer={answerFollowUp}
                  onSkip={skipFollowUp}
                  disabled={state.status === 'processing'}
                  language={state.language}
                />
              )}

              {state.results && (
                <TriageResults
                  results={state.results}
                  onNewAssessment={clearResults}
                  onAddToQueue={addToQueue}
                  language={state.language}
                />
              )}

              {state.results?.modelInfo && (
                <ModelInfoPanel modelInfo={state.results.modelInfo} language={state.language} />
              )}
            </div>

            <div className="lg:col-span-1 space-y-6">
              <PatientQueue
                queue={state.queue}
                currentPatientId={state.currentPatientId}
                onSelectPatient={(id) => {}}
                language={state.language}
              />

              <ResourcePanel
                triageCategory={state.results?.structuredData?.triageCategory}
                resources={state.results?.structuredData?.suggestedActions}
                language={state.language}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
```

### 2. src/app/api/agent/route.ts - Mock API Endpoint
```ts
import { NextRequest, NextResponse } from 'next/server';
import { AgentRequest, AgentResponse, AgentStatus, SafetyLevel, SafetyFlag } from '@/types/agent';

const MOCK_RESPONSES: Record<string, Partial<AgentResponse>> = {
  'chest pain': {
    response: 'Chest pain can be a sign of serious conditions like a heart attack. This requires immediate medical evaluation.',
    status: 'escalated' as AgentStatus,
    safetyLevel: 'emergency' as SafetyLevel,
    safetyFlags: [{
      type: 'emergency', severity: 'critical',
      message: 'Chest pain may indicate a heart attack or other life-threatening condition.',
      recommendedAction: 'Call emergency services (112/108) immediately or go to the nearest emergency department.'
    }],
    structuredData: {
      triageCategory: 'emergency' as const, riskScore: 0.95,
      suggestedActions: ['Call 112/108 immediately', 'Do not drive yourself', 'Chew aspirin if not allergic'],
      disclaimer: 'This is not medical advice. Seek immediate professional medical care.'
    }
  },
  'difficulty breathing': { /* similar structure */ },
  'headache': {
    response: 'Headaches can have many causes. To help me understand better: How long have you had this headache? Is it on one side or both? Any nausea, vision changes, or neck stiffness?',
    status: 'awaiting_input' as AgentStatus,
    safetyLevel: 'caution' as SafetyLevel,
    safetyFlags: [{ type: 'missing_data', severity: 'medium', message: 'Need more information to assess headache severity.', recommendedAction: 'Please answer the follow-up questions.' }],
    followUpQuestion: 'How long have you had this headache? Is it on one side or both? Any nausea, vision changes, or neck stiffness?',
    modelInfo: { modelName: 'SwasthyaAI-Triage-v1', version: '1.0.0', confidence: 0.75, predictionType: 'symptom_check', limitations: ['Cannot diagnose', 'Limited by self-reported symptoms', 'Not a substitute for clinical evaluation'] },
    structuredData: { triageCategory: 'non-urgent' as const, riskScore: 0.3, suggestedActions: ['Track headache patterns', 'Stay hydrated', 'Rest in a quiet, dark room'], disclaimer: 'This is not a diagnosis. Consult a healthcare provider for persistent headaches.' }
  },
  // ... fever, stomach, sleep responses
};

export async function POST(request: NextRequest) {
  try {
    const body: AgentRequest = await request.json();
    if (!body.sessionId || !body.userMessage) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }
    await new Promise(resolve => setTimeout(resolve, 800 + Math.random() * 400));
    
    const mockResponse = findMockResponse(body.userMessage) || generateDefaultResponse(body.userMessage);
    const response: AgentResponse = {
      sessionId: body.sessionId, timestamp: new Date().toISOString(),
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
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

### 3. src/hooks/useTriageSession.ts - State Management
```ts
'use client';
import { useState, useCallback, useRef } from 'react';
import { AgentRequest, AgentResponse, AgentStatus, SafetyLevel, SafetyFlag } from '@/types/agent';
import { generateId } from '@/lib/utils';

const API_ENDPOINT = '/api/agent';

interface TriageState {
  status: AgentStatus;
  language: 'en' | 'hi' | 'hinglish';
  prefillData?: any;
  results: AgentResponse | null;
  followUpQuestion: string | null;
  safetyAlert: { level: SafetyLevel; flags: SafetyFlag[] } | null;
  queue: PatientQueueItem[];
  currentPatientId: string | null;
  error: string | null;
}

export function useTriageSession() {
  const [state, setState] = useState<TriageState>(INITIAL_STATE);
  const abortControllerRef = useRef<AbortController | null>(null);
  const patientCounter = useRef(0);

  const callAgent = useCallback(async (request: AgentRequest): Promise<AgentResponse> => {
    abortControllerRef.current = new AbortController();
    const res = await fetch(API_ENDPOINT, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request), signal: abortControllerRef.current.signal,
    });
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error || `Failed: ${res.status}`);
    return res.json();
  }, []);

  const submitAssessment = useCallback(async (formData: any) => {
    setState(prev => ({ ...prev, status: 'processing', error: null, followUpQuestion: null, safetyAlert: null }));
    try {
      const response = await callAgent({ /* build request from formData */ });
      // Handle safety alerts, follow-ups, queue management
    } catch (err) { /* error handling */ }
  }, [callAgent]);

  const answerFollowUp = useCallback(async (answer: string) => { /* similar pattern */ }, [state.results, callAgent]);
  const skipFollowUp = useCallback(async () => answerFollowUp(''), [answerFollowUp]);
  const addToQueue = useCallback(() => { /* add current result to queue */ }, [state.results]);
  const clearResults = useCallback(() => setState(prev => ({ ...prev, results: null, followUpQuestion: null, safetyAlert: null, status: 'idle', error: null })), []);
  const setLanguage = useCallback((lang: 'en' | 'hi' | 'hinglish') => setState(prev => ({ ...prev, language: lang })), []);

  return { state, submitAssessment, answerFollowUp, skipFollowUp, addToQueue, clearResults, setLanguage };
}
```

### 4. src/types/agent.ts - Integration Types
```ts
export type AgentStatus = 'idle' | 'thinking' | 'awaiting_input' | 'completed' | 'error' | 'escalated';
export type SafetyLevel = 'safe' | 'caution' | 'urgent' | 'emergency';

export interface AgentRequest {
  sessionId: string;
  userMessage: string;
  context?: {
    sessionId: string;
    language?: 'en' | 'hi' | 'hinglish';
    userProfile?: { age?: number; gender?: 'male' | 'female' | 'other'; conditions?: string[]; medications?: string[] };
    metadata?: Record<string, unknown>;
  };
}

export interface AgentResponse {
  response: string;
  status: AgentStatus;
  safetyLevel: SafetyLevel;
  safetyFlags: SafetyFlag[];
  followUpQuestion?: string;
  modelInfo?: { modelName: string; version: string; confidence?: number; predictionType: string; limitations?: string[] };
  structuredData?: { triageCategory?: string; riskScore?: number; suggestedActions?: string[]; disclaimer: string };
  sessionId: string;
  timestamp: string;
}

export interface SafetyFlag {
  type: 'emergency' | 'urgent' | 'missing_data' | 'unsupported_language' | 'uncertainty' | 'contraindication';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  recommendedAction: string;
}
```

---

## Incremental Git Commands

Run these commands one at a time to commit in small, meaningful chunks:

```bash
# 1. Initialize repo (if not already done)
cd /c/Users/RAKSHIT/SwasthyaAI/frontend
git init

# 2. First commit: Project config & types
git add package.json tsconfig.json next.config.ts eslint.config.mjs .gitignore src/types/agent.ts
git commit -m "feat: add project config, TypeScript setup, and agent integration types"

# 3. Second commit: Core utilities and styling
git add src/lib/utils.ts src/app/globals.css src/app/layout.tsx
git commit -m "feat: add utility functions, global styles with accessibility, and root layout"

# 4. Third commit: API endpoint (mock)
git add src/app/api/agent/route.ts
git commit -m "feat: add mock agent API endpoint with emergency/urgent/follow-up responses"

# 5. Fourth commit: State management hook
git add src/hooks/useTriageSession.ts
git commit -m "feat: add useTriageSession hook with assessment, follow-up, queue, and language state"

# 6. Fifth commit: Layout components
git add src/components/layout/Header.tsx
git commit -m "feat: add Header component with status indicator, language selector, and medical disclaimer"

# 7. Sixth commit: Triage form component
git add src/components/triage/TriageForm.tsx
git commit -m "feat: add TriageForm with chief complaint, symptoms, duration, severity, patient info, multi-language"

# 8. Seventh commit: Results & safety components
git add src/components/triage/TriageResults.tsx src/components/triage/SafetyAlert.tsx
git commit -m "feat: add TriageResults with category/risk display and SafetyAlert for emergency escalation"

# 8. Eighth commit: Follow-up & queue components
git add src/components/triage/FollowUpSection.tsx src/components/triage/PatientQueue.tsx
git commit -m "feat: add FollowUpSection for interactive Q&A and PatientQueue with priority sorting"

# 9. Ninth commit: Resource & model panels
git add src/components/triage/ResourcePanel.tsx src/components/triage/ModelInfoPanel.tsx src/components/triage/LanguageSelector.tsx
git commit -m "feat: add ResourcePanel (context-aware), ModelInfoPanel (transparency), and LanguageSelector"

# 10. Tenth commit: Barrel exports and main page
git add src/components/triage/index.ts src/app/page.tsx
git commit -m "feat: add triage component exports and main dashboard page wiring all components"

# 11. Final: Verify build and push
npm run build
git remote add origin <your-github-repo-url>
git push -u origin main
```

---

## Key Features for Demo

| Test Input | Expected Result |
|------------|-----------------|
| "Chest pain" | 🚨 Emergency banner, escalation status, ambulance/ER resources |
| "Headache" | Follow-up questions → non-urgent result with self-care |
| "Difficulty breathing" | 🚨 Emergency banner, escalation |
| "Stomach ache" | Self-care advice, pharmacy/PCP resources |
| Language toggle | Full UI switches EN/HI/Hinglish |

---

## Integration Contract (for Member 3 Backend)

The frontend expects this exact API contract at `POST /api/agent`:

**Request:**
```json
{
  "sessionId": "uuid",
  "userMessage": "patient symptoms",
  "context": {
    "sessionId": "uuid",
    "language": "en|hi|hinglish",
    "userProfile": { "age": 35, "gender": "female", "conditions": ["diabetes"] },
    "metadata": { "symptoms": ["nausea"], "duration": "1-6h", "severity": 7 }
  }
}
```

**Response:**
```json
{
  "sessionId": "uuid",
  "timestamp": "ISO8601",
  "response": "AI assessment text",
  "status": "completed|awaiting_input|escalated|error",
  "safetyLevel": "safe|caution|urgent|emergency",
  "safetyFlags": [{ "type": "emergency", "severity": "critical", "message": "...", "recommendedAction": "..." }],
  "followUpQuestion": "question if awaiting_input",
  "modelInfo": { "modelName": "...", "version": "...", "confidence": 0.85, "predictionType": "triage", "limitations": [...] },
  "structuredData": { "triageCategory": "emergency|urgent|semi-urgent|non-urgent|self-care", "riskScore": 0.95, "suggestedActions": ["..."], "disclaimer": "..." }
}
```

---

## Accessibility Features Included
- Skip to main content link
- ARIA labels on all interactive elements
- Focus-visible outlines for keyboard navigation
- Reduced motion support (`prefers-reduced-motion`)
- High contrast support (`prefers-contrast: high`)
- Semantic HTML5 structure
- Live regions for dynamic updates
- Color-blind safe palette (teal primary)