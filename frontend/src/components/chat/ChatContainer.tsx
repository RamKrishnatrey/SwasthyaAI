'use client';

import React, { useRef, useEffect, useCallback } from 'react';
import { ChatMessage } from '@/types/agent';
import { ChatMessageComponent } from './ChatMessage';
import { cn } from '@/lib/utils';

interface ChatContainerProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  onRetry?: (messageId: string) => void;
  scrollToBottomRef?: React.RefObject<HTMLDivElement>;
}

export function ChatContainer({ messages, isLoading, onRetry, scrollToBottomRef }: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  // Expose scrollToBottom function to parent
  useEffect(() => {
    if (scrollToBottomRef) {
      scrollToBottomRef.current = messagesEndRef.current;
    }
  }, [scrollToBottomRef]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'End') {
      e.preventDefault();
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    } else if (e.key === 'Home') {
      e.preventDefault();
      containerRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  if (messages.length === 0) {
    return (
      <div
        ref={containerRef}
        className="flex-1 flex flex-col items-center justify-center p-8 text-center"
        role="region"
        aria-label="Empty chat"
        onKeyDown={handleKeyDown}
      >
        <div className="w-16 h-16 rounded-2xl bg-primary-light flex items-center justify-center mb-4" aria-hidden="true">
          <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-foreground mb-2">Welcome to SwasthyaAI</h2>
        <p className="text-muted-foreground max-w-xs mb-6">
          I'm your AI health assistant. Describe your symptoms or health concerns, and I'll help you understand what might be going on and what steps to take next.
        </p>
        <div className="flex flex-wrap gap-2 justify-center" role="list" aria-label="Example questions">
          {[
            'I have a headache and fever since yesterday',
            'Chest pain when breathing deeply',
            'Stomach ache after eating spicy food',
            'Difficulty sleeping for a week',
          ].map((example, idx) => (
            <button
              key={idx}
              className="px-3 py-1.5 text-sm bg-muted border border-border rounded-lg hover:bg-border transition-colors"
              aria-label={`Try: ${example}`}
            >
              {example}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto p-4 space-y-6"
      role="log"
      aria-live="polite"
      aria-label="Conversation history"
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      {messages.map((message, idx) => (
        <ChatMessageComponent
          key={message.id}
          message={message}
          onRetry={() => onRetry?.(message.id)}
        />
      ))}

      {isLoading && (
        <div className="flex gap-3 animate-fade-in" aria-live="polite" aria-label="Assistant is typing">
          <div className="flex-shrink-0 w-9 h-9 rounded-full bg-primary-light flex items-center justify-center" aria-hidden="true">
            <svg className="w-5 h-5 text-primary animate-spin" fill="none" viewBox="0 0 24 24" aria-hidden="true">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <div className="bg-card border border-border rounded-2xl px-4 py-3 max-w-[75%] shadow-sm">
            <div className="flex gap-1.5 items-center" role="status" aria-label="Analyzing your symptoms">
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0ms' }} aria-hidden="true" />
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '150ms' }} aria-hidden="true" />
              <span className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '300ms' }} aria-hidden="true" />
              <span className="text-sm text-muted-foreground ml-2">Analyzing your symptoms...</span>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} aria-hidden="true" />
    </div>
  );
}