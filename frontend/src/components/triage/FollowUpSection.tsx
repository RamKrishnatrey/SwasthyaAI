'use client';

import React, { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

const TRANSLATIONS = {
  en: {
    followUp: 'Follow-up Question',
    placeholder: 'Your response...',
    submit: 'Submit Answer',
    skip: 'Skip for now',
    required: 'Please provide an answer or skip',
  },
  hi: {
    followUp: 'अनुवर्ती प्रश्न',
    placeholder: 'आपका जवाब...',
    submit: 'जवाब दें',
    skip: 'अभी छोड़ें',
    required: 'कृपया जवाब दें या छोड़ें',
  },
  hinglish: {
    followUp: 'Follow-up Question / Agla Sawal',
    placeholder: 'Aapka jawab...',
    submit: 'Jawab Dein / Submit',
    skip: 'Abhi Chhod Do / Skip',
    required: 'Kripya jawab dein ya skip karein',
  },
};

interface FollowUpSectionProps {
  question: string;
  onAnswer: (answer: string) => void;
  onSkip: () => void;
  disabled?: boolean;
  language: 'en' | 'hi' | 'hinglish';
}

export function FollowUpSection({ question, onAnswer, onSkip, disabled = false, language }: FollowUpSectionProps) {
  const t = TRANSLATIONS[language];
  const [answer, setAnswer] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (answer.trim() && !disabled) {
      onAnswer(answer.trim());
    }
  };

  return (
    <div
      className="relative p-5 rounded-xl bg-primary-light/30 border border-primary/20 dark:bg-primary/10 dark:border-primary/30 animate-fade-in"
      role="region"
      aria-label={t.followUp}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-primary" aria-hidden="true">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm font-medium text-primary">{t.followUp}</span>
            <span className="px-2 py-0.5 text-xs font-medium bg-primary/20 text-primary rounded-full">Required</span>
          </div>

          <p className="text-foreground mb-4">{question}</p>

          <form onSubmit={handleSubmit} className="space-y-3">
            <textarea
              ref={textareaRef}
              value={answer}
              onChange={e => setAnswer(e.target.value)}
              placeholder={t.placeholder}
              disabled={disabled}
              rows={3}
              className="w-full px-4 py-3 bg-white dark:bg-slate-800 border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 resize-none"
              aria-label={t.followUp}
              aria-required="true"
            />

            <div className="flex items-center gap-2">
              <button
                type="submit"
                disabled={disabled || !answer.trim()}
                className={cn(
                  'px-5 py-2 text-sm font-medium rounded-xl transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
                  disabled || !answer.trim()
                    ? 'bg-muted text-muted-foreground cursor-not-allowed'
                    : 'bg-primary text-white hover:bg-primary-hover'
                )}
              >
                {t.submit}
              </button>

              <button
                type="button"
                onClick={onSkip}
                disabled={disabled}
                className={cn(
                  'px-5 py-2 text-sm font-medium rounded-xl border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
                  disabled
                    ? 'bg-muted text-muted-foreground border-transparent cursor-not-allowed'
                    : 'bg-transparent text-primary border-primary hover:bg-primary/5'
                )}
              >
                {t.skip}
              </button>
            </div>

            <p className="text-xs text-muted-foreground" aria-live="polite">
              {answer.trim() ? '' : t.required}
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}