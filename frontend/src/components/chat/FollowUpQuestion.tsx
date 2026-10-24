'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface FollowUpQuestionProps {
  question: string;
  onAnswer: (answer: string) => void;
  onSkip?: () => void;
  disabled?: boolean;
}

export function FollowUpQuestion({ question, onAnswer, onSkip, disabled = false }: FollowUpQuestionProps) {
  const [answer, setAnswer] = React.useState('');
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  React.useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (answer.trim() && !disabled) {
      onAnswer(answer.trim());
    }
  };

  const handleSkip = () => {
    onSkip?.();
  };

  return (
    <div
      className="relative mb-4 p-4 rounded-xl bg-primary-light/50 border border-primary/20 dark:bg-primary/10 dark:border-primary/30 animate-fade-in"
      role="region"
      aria-label="Follow-up question"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary" aria-hidden="true">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm text-foreground mb-3">{question}</p>

          <form onSubmit={handleSubmit} className="space-y-2">
            <textarea
              ref={textareaRef}
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Your response..."
              disabled={disabled}
              rows={2}
              className="w-full px-3 py-2 bg-white dark:bg-slate-800 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 resize-none min-h-[60px]"
              aria-label="Your answer to the follow-up question"
            />

            <div className="flex items-center gap-2">
              <button
                type="submit"
                disabled={disabled || !answer.trim()}
                className="px-4 py-1.5 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary-hover focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Submit Answer
              </button>

              {onSkip && (
                <button
                  type="button"
                  onClick={handleSkip}
                  disabled={disabled}
                  className="px-4 py-1.5 text-sm font-medium text-primary bg-transparent border border-primary rounded-lg hover:bg-primary/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Skip for now
                </button>
              )}
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}