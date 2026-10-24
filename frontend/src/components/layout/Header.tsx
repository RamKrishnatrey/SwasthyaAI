'use client';

import React from 'react';
import { cn } from '@/lib/utils';

interface HeaderProps {
  sessionStatus: 'idle' | 'processing' | 'completed' | 'error';
  currentLanguage: 'en' | 'hi' | 'hinglish';
  onLanguageChange: (lang: 'en' | 'hi' | 'hinglish') => void;
  onNewAssessment?: () => void;
}

export function Header({ sessionStatus, currentLanguage, onLanguageChange, onNewAssessment }: HeaderProps) {
  const statusConfig = {
    idle: { label: 'Ready', className: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300', icon: '🟢' },
    processing: { label: 'Processing…', className: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300', icon: '🔄' },
    completed: { label: 'Complete', className: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300', icon: '✅' },
    error: { label: 'Error', className: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300', icon: '❌' },
  };

  const config = statusConfig[sessionStatus];

  const LANGUAGES = [
    { code: 'en', name: 'English', native: 'English', flag: '🇮🇳' },
    { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
    { code: 'hinglish', name: 'Hinglish', native: 'Hinglish', flag: '🇮🇳' },
  ] as const;

  return (
    <header className="sticky top-0 z-40 bg-card/80 backdrop-blur-md border-b border-border" role="banner">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16 gap-4 flex-wrap">
          {/* Logo & Title */}
          <div className="flex items-center gap-3 flex-shrink-0" aria-label="SwasthyaAI Home">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary-hover flex items-center justify-center" aria-hidden="true">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">SwasthyaAI</h1>
              <p className="text-xs text-muted-foreground">AI-Powered Healthcare Triage System</p>
            </div>
          </div>

          {/* Center: Status & Language */}
          <div className="flex items-center gap-4 flex-1 justify-center md:justify-between">
            {/* Connection Status */}
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium" role="status" aria-live="polite">
              <span aria-hidden="true">{config.icon}</span>
              <span className={cn(config.className)}>{config.label}</span>
            </div>

            {/* Language Selector */}
            <div className="flex items-center gap-2">
              <label htmlFor="header-language" className="hidden sm:block text-sm font-medium text-foreground">Language</label>
              <select
                id="header-language"
                value={currentLanguage}
                onChange={e => onLanguageChange(e.target.value as any)}
                disabled={sessionStatus === 'processing'}
                className="px-3 py-1.5 bg-muted border border-border rounded-lg text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 cursor-pointer"
                aria-label="Select language"
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.flag} {lang.native}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-2">
            {onNewAssessment && (
              <button
                onClick={onNewAssessment}
                disabled={sessionStatus === 'processing'}
                className="hidden sm:flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-primary bg-primary-light/50 border border-primary/20 rounded-lg hover:bg-primary-light transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:opacity-50"
                aria-label="Start new assessment"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                New Assessment
              </button>
            )}

            {/* Version Badge */}
            <span className="hidden lg:inline-flex items-center gap-1 px-2 py-1 text-xs font-mono text-muted-foreground bg-muted rounded">
              v1.0.0-beta
            </span>
          </div>
        </div>

        {/* Disclaimer Banner */}
        <div className="border-t border-border px-4 py-2 bg-muted/50" role="contentinfo">
          <p className="text-xs text-muted-foreground text-center max-w-7xl mx-auto">
            ⚠️ <strong>Medical Disclaimer:</strong> This AI system provides health triage guidance only, not medical diagnosis or treatment advice.
            It cannot replace professional medical evaluation. For life-threatening emergencies, call <strong>112</strong> or <strong>108</strong> immediately.
          </p>
        </div>
      </div>
    </header>
  );
}