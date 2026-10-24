'use client';

import React from 'react';
import { SafetyFlag, SafetyLevel } from '@/types/agent';
import { getSafetyColor, getSafetyBgColor, cn } from '@/lib/utils';

interface SafetyBannerProps {
  safetyLevel: SafetyLevel;
  safetyFlags: SafetyFlag[];
  onDismiss?: () => void;
}

const SEVERITY_ICONS = {
  critical: '🚨',
  high: '⚠️',
  medium: '⚡',
  low: 'ℹ️',
};

const SEVERITY_LABELS = {
  critical: 'Emergency',
  high: 'Urgent Attention',
  medium: 'Caution Advised',
  low: 'Information',
};

export function SafetyBanner({ safetyLevel, safetyFlags, onDismiss }: SafetyBannerProps) {
  if (safetyLevel === 'safe' && safetyFlags.length === 0) {
    return null;
  }

  const highestSeverity = safetyFlags.reduce((max, flag) => {
    const order = { critical: 4, high: 3, medium: 2, low: 1 };
    return order[flag.severity] > order[max.severity] ? flag : max;
  }, safetyFlags[0] ?? { severity: 'low' as const });

  return (
    <div
      className={cn(
        'relative mb-4 p-4 rounded-xl border animate-fade-in',
        getSafetyBgColor(highestSeverity.severity)
      )}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/50 dark:bg-slate-800/50 flex items-center justify-center text-lg" aria-hidden="true">
          {SEVERITY_ICONS[highestSeverity.severity]}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className={cn('font-semibold text-sm', getSafetyColor(highestSeverity.severity))}>
              {SEVERITY_LABELS[highestSeverity.severity]}
            </span>
            {safetyLevel === 'emergency' && (
              <span className="px-1.5 py-0.5 text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300 rounded">
                CALL 112 / 108
              </span>
            )}
          </div>

          <p className="text-sm text-foreground">
            {safetyFlags.map((flag, idx) => (
              <React.Fragment key={idx}>
                {flag.message}
                {idx < safetyFlags.length - 1 && ' '}
              </React.Fragment>
            ))}
          </p>

          {safetyFlags.some(f => f.recommendedAction) && (
            <ul className="mt-2 space-y-1 text-sm" role="list">
              {safetyFlags
                .filter(f => f.recommendedAction)
                .map((flag, idx) => (
                  <li key={idx} className={cn('flex items-start gap-2', getSafetyColor(flag.severity))}>
                    <span className="flex-shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full" aria-hidden="true" />
                    <span>{flag.recommendedAction}</span>
                  </li>
                ))}
            </ul>
          )}
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 p-1 rounded-lg hover:bg-white/30 dark:hover:bg-slate-700/30 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-current"
            aria-label="Dismiss safety notice"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}