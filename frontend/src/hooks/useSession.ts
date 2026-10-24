'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { ChatMessage, AgentRequest, AgentResponse, AgentStatus, SafetyLevel } from '@/types/agent';
import { generateId, formatTimestamp } from '@/lib/utils';

const API_ENDPOINT = '/api/agent';

interface UseSessionReturn {
  messages: ChatMessage[];
  status: AgentStatus;
  safetyLevel: SafetyLevel;
  isLoading: boolean;
  error: string | null;
  sessionId: string;
  sendMessage: (text: string) => Promise<void>;
  answerFollowUp: (answer: string) => Promise<void>;
  skipFollowUp: () => Promise<void>;
  clearError: () => void;
  newSession: () => void;
}

export function useSession(): UseSessionReturn {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [status, setStatus] = useState<AgentStatus>('idle');
  const [safetyLevel, setSafetyLevel] = useState<SafetyLevel>('safe');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId] = useState(() => generateId());
  const [pendingFollowUp, setPendingFollowUp] = useState<{ question: string; resolve: (answer: string) => void; reject: (err: Error) => void } | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const convertToChatMessage = useCallback((response: AgentResponse, userMessage?: string): ChatMessage => {
    return {
      id: generateId(),
      role: 'assistant',
      content: response.response,
      timestamp: new Date(response.timestamp),
      status: response.status,
      safetyLevel: response.safetyLevel,
      safetyFlags: response.safetyFlags,
      followUpQuestion: response.followUpQuestion,
      modelInfo: response.modelInfo,
      structuredData: response.structuredData,
    };
  }, []);

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

  const sendMessage = useCallback(async (text: string) => {
    if (isLoading) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: text,
      timestamp: new Date(),
      status: 'idle',
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setStatus('thinking');
    setError(null);

    try {
      const request: AgentRequest = {
        sessionId,
        userMessage: text,
        context: {
          sessionId,
          conversationHistory: messages.map(m => ({
            role: m.role,
            content: m.content,
            timestamp: m.timestamp.toISOString(),
            metadata: m.safetyFlags ? { safetyFlags: m.safetyFlags } : undefined,
          })),
        },
      };

      const response = await callAgent(request);
      const assistantMessage = convertToChatMessage(response);

      setMessages(prev => [...prev, assistantMessage]);
      setStatus(response.status);
      setSafetyLevel(response.safetyLevel);

      // Handle follow-up question
      if (response.followUpQuestion && response.status === 'awaiting_input') {
        await new Promise<void>((resolve, reject) => {
          setPendingFollowUp({ question: response.followUpQuestion!, resolve, reject });
        });
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') return;

      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);
      setStatus('error');

      const errorMsg: ChatMessage = {
        id: generateId(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${errorMessage}. Please try again.`,
        timestamp: new Date(),
        status: 'error',
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  }, [sessionId, messages, isLoading, callAgent, convertToChatMessage]);

  const answerFollowUp = useCallback(async (answer: string) => {
    if (!pendingFollowUp || isLoading) return;

    const userMessage: ChatMessage = {
      id: generateId(),
      role: 'user',
      content: answer,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setStatus('thinking');

    const { resolve, reject } = pendingFollowUp;
    setPendingFollowUp(null);

    try {
      const request: AgentRequest = {
        sessionId,
        userMessage: answer,
        context: {
          sessionId,
          conversationHistory: messages.map(m => ({
            role: m.role,
            content: m.content,
            timestamp: m.timestamp.toISOString(),
          })),
        },
      };

      const response = await callAgent(request);
      const assistantMessage = convertToChatMessage(response);

      setMessages(prev => [...prev, assistantMessage]);
      setStatus(response.status);
      setSafetyLevel(response.safetyLevel);
      resolve();
    } catch (err) {
      reject(err instanceof Error ? err : new Error('Follow-up failed'));
      setStatus('error');
      const errorMessage = err instanceof Error ? err.message : 'Follow-up failed';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [pendingFollowUp, sessionId, messages, isLoading, callAgent, convertToChatMessage]);

  const skipFollowUp = useCallback(async () => {
    if (!pendingFollowUp) return;

    const { resolve } = pendingFollowUp;
    setPendingFollowUp(null);
    resolve(''); // Empty answer to signal skip
  }, [pendingFollowUp]);

  const clearError = useCallback(() => setError(null), []);

  const newSession = useCallback(() => {
    // This will trigger a re-render with new sessionId via key change
    window.location.reload();
  }, []);

  return {
    messages,
    status,
    safetyLevel,
    isLoading,
    error,
    sessionId,
    sendMessage,
    answerFollowUp,
    skipFollowUp,
    clearError,
    newSession,
  };
}