'use client';

import React from 'react';
import { ChatMessage, SafetyFlag, ModelInfo } from '@/types/agent';
import { formatTimestamp, getSafetyColor, getSafetyBgColor, cn } from '@/lib/utils';

interface ChatMessageProps {
  message: ChatMessage;
  onRetry?: () => void;
}

export function ChatMessageComponent({ message, onRetry }: ChatMessageProps) {
  const isUser = message.role === 'user';

  const safetyFlags = message.safetyFlags ?? [];
  const hasHighSeverityFlags = safetyFlags.some(f => f.severity === 'high' || f.severity === 'critical');

  return (
    <div
      className={cn(
        'flex gap-3 animate-fade-in',
        isUser ? 'flex-row-reverse' : 'flex-row'
      )}
      role="article"
      aria-label={isUser ? 'Your message' : 'Assistant response'}
    >
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-9 h-9 rounded-full flex items-center justify-center text-sm font-medium',
          isUser
            ? 'bg-primary text-white'
            : 'bg-primary-light text-primary dark:bg-primary/20 dark:text-primary'
        )}
        aria-hidden="true"
      >
        {isUser ? '👤' : '🏥'}
      </div>

      {/* Message Content */}
      <div
        className={cn(
          'max-w-[75%] relative',
          isUser ? 'text-right' : 'text-left'
        )}
      >
        {/* Message Bubble */}
        <div
          className={cn(
            'inline-block px-4 py-2.5 rounded-2xl',
            isUser
              ? 'bg-primary text-white rounded-tr-sm'
              : 'bg-card border border-border rounded-tl-sm shadow-sm'
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {/* Safety Flags Banner */}
        {hasHighSeverityFlags && (
          <div
            className={cn(
              'mt-2 px-3 py-2 rounded-lg text-sm border animate-fade-in',
              getSafetyBgColor(safetyFlags[0]?.severity ?? 'medium')
            )}
            role="alert"
            aria-live="polite"
          >
            <div className="flex items-start gap-2">
              <span className="flex-shrink-0 mt-0.5" aria-hidden="true">⚠️</span>
              <div className="flex-1">
                {safetyFlags
                  .filter(f => f.severity === 'high' || f.severity === 'critical')
                  .map((flag, idx) => (
                    <div key={idx} className={cn('font-medium', getSafetyColor(flag.severity))}>
                      {flag.message}
                      <p className="text-xs mt-0.5 opacity-80">{flag.recommendedAction}</p>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        )}

        {/* Structured Data Display */}
        {message.structuredData && !isUser && (
          <div className="mt-2 space-y-2" role="region" aria-label="Assessment details">
            {message.structuredData.triageCategory && (
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-primary-light text-primary dark:bg-primary/20">
                <span className="relative flex h-1.5 w-1.5 rounded-full bg-primary" aria-hidden="true" />
                Triage: {message.structuredData.triageCategory}
              </div>
            )}
            {message.structuredData.riskScore !== undefined && (
              <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300">
                Risk Score: {Math.round(message.structuredData.riskScore * 100)}%
              </div>
            )}
            {message.structuredData.suggestedActions && message.structuredData.suggestedActions.length > 0 && (
              <details className="group">
                <summary className="cursor-pointer text-xs text-secondary hover:text-foreground flex items-center gap-1">
                  <span>Suggested Actions</span>
                  <svg className="w-3 h-3 transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </summary>
                <ul className="mt-2 space-y-1 pl-4 text-sm text-secondary">
                  {message.structuredData.suggestedActions.map((action, idx) => (
                    <li key={idx} className="flex items-start gap-1">
                      <span className="flex-shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-secondary" aria-hidden="true" />
                      {action}
                    </li>
                  ))}
                </ul>
              </details>
            )}
            {message.structuredData.disclaimer && (
              <p className="text-xs text-muted-foreground italic">{message.structuredData.disclaimer}</p>
            )}
          </div>
        )}

        {/* Model Info */}
        {message.modelInfo && !isUser && (
          <details className="mt-2">
            <summary className="cursor-pointer text-xs text-muted-foreground hover:text-secondary flex items-center gap-1">
              <span>Model Details</span>
              <svg className="w-3 h-3 transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </summary>
            <div className="mt-1 p-2 bg-muted rounded text-xs text-muted-foreground space-y-1">
              <div>Model: {message.modelInfo.modelName} v{message.modelInfo.version}</div>
              <div>Type: {message.modelInfo.predictionType}</div>
              {message.modelInfo.confidence !== undefined && (
                <div>Confidence: {Math.round(message.modelInfo.confidence * 100)}%</div>
              )}
              {message.modelInfo.limitations && message.modelInfo.limitations.length > 0 && (
                <div>Limitations: {message.modelInfo.limitations.join(', ')}</div>
              )}
            </div>
          </details>
        )}

        {/* Timestamp & Status */}
        <div className={cn('mt-1 flex items-center gap-2 text-xs text-muted-foreground', isUser ? 'justify-end' : 'justify-start')}>
          <time dateTime={message.timestamp.toISOString()}>{formatTimestamp(message.timestamp)}</time>
          {message.status && message.status !== 'completed' && (
            <span className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-muted">
              {message.status === 'thinking' ? '⏳' : message.status === 'error' ? '❌' : '⏸️'}
            </span>
          )}
          {message.isStreaming && <span className="animate-pulse-soft text-primary" aria-hidden="true">▌</span>}
        </div>

        {/* Retry Button for Errors */}
        {message.status === 'error' && onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-xs text-primary hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
            aria-label="Retry sending message"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}