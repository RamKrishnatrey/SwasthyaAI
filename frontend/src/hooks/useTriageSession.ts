'use client';

import { useState, useCallback, useRef, useEffect } from 'react';
import { AgentRequest, AgentResponse, AgentStatus, SafetyLevel, SafetyFlag, ModelInfo } from '@/types/agent';
import { generateId } from '@/lib/utils';

const API_ENDPOINT = '/api/agent';

interface PatientQueueItem {
  id: string;
  name: string;
  age?: number;
  chiefComplaint: string;
  triageCategory: 'emergency' | 'urgent' | 'semi-urgent' | 'non-urgent' | 'self-care';
  riskScore: number;
  timestamp: string;
  status: 'waiting' | 'assessed' | 'in-progress';
}

interface TriageState {
  // Form & Assessment
  status: AgentStatus;
  language: 'en' | 'hi' | 'hinglish';
  prefillData?: Partial<{
    chiefComplaint: string;
    symptoms: string[];
    duration: string;
    severity: number;
    age?: number;
    gender?: 'male' | 'female' | 'other';
    existingConditions: string[];
    medications: string[];
    allergies: string[];
  }>;

  // Results
  results: AgentResponse | null;
  followUpQuestion: string | null;
  safetyAlert: { level: SafetyLevel; flags: SafetyFlag[] } | null;

  // Queue
  queue: PatientQueueItem[];
  currentPatientId: string | null;

  // Error
  error: string | null;
}

const INITIAL_STATE: TriageState = {
  status: 'idle',
  language: 'en',
  results: null,
  followUpQuestion: null,
  safetyAlert: null,
  queue: [],
  currentPatientId: null,
  error: null,
};

export function useTriageSession() {
  const [state, setState] = useState<TriageState>(INITIAL_STATE);
  const abortControllerRef = useRef<AbortController | null>(null);
  const patientCounter = useRef(0);

  // Generate patient name for queue
  const generatePatientName = () => {
    patientCounter.current += 1;
    return `Patient ${patientCounter.current}`;
  };

  const callAgent = useCallback(async (request: AgentRequest): Promise<AgentResponse> => {
    abortControllerRef.current = new AbortController();

    const res = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
      signal: abortControllerRef.current.signal,
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.error || `Request failed: ${res.status}`);
    }

    return res.json();
  }, []);

  const submitAssessment = useCallback(async (formData: any) => {
    setState(prev => ({ ...prev, status: 'processing', error: null, followUpQuestion: null, safetyAlert: null }));

    try {
      const request: AgentRequest = {
        sessionId: generateId(),
        userMessage: formData.chiefComplaint,
        context: {
          sessionId: generateId(),
          language: formData.language,
          userProfile: {
            age: formData.age,
            gender: formData.gender,
            conditions: formData.existingConditions,
            medications: formData.medications,
          },
          metadata: {
            symptoms: formData.symptoms,
            duration: formData.duration,
            severity: formData.severity,
            allergies: formData.allergies,
          },
        },
      };

      const response = await callAgent(request);

      // Handle safety alerts
      if (response.safetyFlags && response.safetyFlags.length > 0) {
        const highestSeverity = response.safetyFlags.reduce((max, flag) => {
          const order = { critical: 4, high: 3, medium: 2, low: 1 };
          return order[flag.severity] > order[max.severity] ? flag : max;
        }, response.safetyFlags[0]);

        setState(prev => ({
          ...prev,
          safetyAlert: {
            level: response.safetyLevel,
            flags: response.safetyFlags,
          },
        }));
      }

      // Handle follow-up questions
      if (response.followUpQuestion && response.status === 'awaiting_input') {
        setState(prev => ({
          ...prev,
          results: response,
          followUpQuestion: response.followUpQuestion!,
          status: 'awaiting_input',
        }));
        return;
      }

      // Complete result
      setState(prev => ({
        ...prev,
        results: response,
        status: response.status === 'error' ? 'error' : 'completed',
        followUpQuestion: null,
      }));

      // Auto-add to queue if not emergency (emergencies go straight to ER)
      if (response.structuredData?.triageCategory !== 'emergency') {
        const patient: PatientQueueItem = {
          id: generateId(),
          name: generatePatientName(),
          age: formData.age,
          chiefComplaint: formData.chiefComplaint,
          triageCategory: response.structuredData?.triageCategory ?? 'non-urgent',
          riskScore: response.structuredData?.riskScore ?? 0,
          timestamp: response.timestamp,
          status: 'assessed',
        };

        setState(prev => ({
          ...prev,
          queue: [patient, ...prev.queue].slice(0, 50), // Keep last 50
          currentPatientId: patient.id,
        }));
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;

      const errorMessage = err instanceof Error ? err.message : 'Assessment failed';
      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMessage,
      }));
    }
  }, [callAgent]);

  const answerFollowUp = useCallback(async (answer: string) => {
    if (!state.results || state.status === 'processing') return;

    setState(prev => ({ ...prev, status: 'processing', followUpQuestion: null }));

    try {
      const request: AgentRequest = {
        sessionId: state.results.sessionId,
        userMessage: answer,
        context: {
          sessionId: state.results.sessionId,
          language: state.language,
        },
      };

      const response = await callAgent(request);

      setState(prev => ({
        ...prev,
        results: response,
        status: response.status === 'error' ? 'error' : 'completed',
        followUpQuestion: response.followUpQuestion ?? null,
        safetyAlert: response.safetyFlags && response.safetyFlags.length > 0
          ? { level: response.safetyLevel, flags: response.safetyFlags }
          : null,
      }));

      // Add to queue on completion
      if (response.status !== 'error' && response.status !== 'awaiting_input') {
        const patient: PatientQueueItem = {
          id: generateId(),
          name: generatePatientName(),
          chiefComplaint: state.results.structuredData?.triageCategory ?? 'Follow-up',
          triageCategory: response.structuredData?.triageCategory ?? 'non-urgent',
          riskScore: response.structuredData?.riskScore ?? 0,
          timestamp: response.timestamp,
          status: 'assessed',
        };

        setState(prev => ({
          ...prev,
          queue: [patient, ...prev.queue].slice(0, 50),
          currentPatientId: patient.id,
        }));
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;

      const errorMessage = err instanceof Error ? err.message : 'Follow-up failed';
      setState(prev => ({
        ...prev,
        status: 'error',
        error: errorMessage,
      }));
    }
  }, [state.results, state.language, callAgent]);

  const skipFollowUp = useCallback(async () => {
    if (!state.results) return;
    await answerFollowUp(''); // Empty answer signals skip
  }, [state.results, answerFollowUp]);

  const addToQueue = useCallback(() => {
    if (!state.results) return;

    const patient: PatientQueueItem = {
      id: generateId(),
      name: generatePatientName(),
      chiefComplaint: state.results.structuredData?.triageCategory ?? 'Assessment',
      triageCategory: state.results.structuredData?.triageCategory ?? 'non-urgent',
      riskScore: state.results.structuredData?.riskScore ?? 0,
      timestamp: state.results.timestamp,
      status: 'assessed',
    };

    setState(prev => ({
      ...prev,
      queue: [patient, ...prev.queue].slice(0, 50),
      currentPatientId: patient.id,
    }));
  }, [state.results]);

  const clearResults = useCallback(() => {
    setState(prev => ({
      ...prev,
      results: null,
      followUpQuestion: null,
      safetyAlert: null,
      status: 'idle',
      error: null,
      prefillData: undefined,
    }));
  }, []);

  const setLanguage = useCallback((lang: 'en' | 'hi' | 'hinglish') => {
    setState(prev => ({ ...prev, language: lang }));
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  return {
    state,
    submitAssessment,
    answerFollowUp,
    skipFollowUp,
    addToQueue,
    clearResults,
    setLanguage,
    clearError,
  };
}