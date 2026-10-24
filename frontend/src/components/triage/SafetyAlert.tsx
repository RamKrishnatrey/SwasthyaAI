'use client';

import React from 'react';
import { SafetyFlag, SafetyLevel } from '@/types/agent';
import { cn, getSafetyColor, getSafetyBgColor } from '@/lib/utils';

const SEVERITY_CONFIG = {
  critical: { icon: '🚨', label: { en: 'EMERGENCY', hi: 'आपातकाल', hinglish: 'EMERGENCY' }, action: { en: 'Call 112/108 NOW', hi: '112/108 पर तुरंत कॉल करें', hinglish: '112/108 abhi call karein' } },
  high: { icon: '⚠️', label: { en: 'URGENT', hi: 'तत्काल', hinglish: 'URGENT' }, action: { en: 'Seek immediate care', hi: 'तुरंत देखभाल लें', hinglish: 'Turant care lein' } },
  medium: { icon: '⚡', label: { en: 'CAUTION', hi: 'सावधानी', hinglish: 'CAUTION' }, action: { en: 'Monitor closely', hi: 'करीब से निगरानी करें', hinglish: 'Kareeb se nigrani karein' } },
  low: { icon: 'ℹ️', label: { en: 'INFO', hi: 'जानकारी', hinglish: 'INFO' }, action: { en: 'Note for reference', hi: 'संदर्भ के लिए नोट करें', hinglish: 'Reference ke liye note karein' } },
};

interface SafetyAlertProps {
  alert: {
    level: SafetyLevel;
    flags: SafetyFlag[];
  };
  onDismiss: () => void;
  language?: 'en' | 'hi' | 'hinglish';
}

export function SafetyAlert({ alert, onDismiss, language = 'en' }: SafetyAlertProps) {
  const highestSeverity = alert.flags.reduce((max, flag) => {
    const order = { critical: 4, high: 3, medium: 2, low: 1 };
    return order[flag.severity] > order[max.severity] ? flag : max;
  }, alert.flags[0]);

  const config = SEVERITY_CONFIG[highestSeverity.severity];

  return (
    <div
      className={cn(
        'relative p-4 rounded-xl border animate-fade-in shadow-lg',
        getSafetyBgColor(highestSeverity.severity)
      )}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-white/30 dark:bg-slate-800/30 flex items-center justify-center text-xl" aria-hidden="true">
          {config.icon}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className={cn('text-sm font-bold', getSafetyColor(highestSeverity.severity))}>
              {config.label[language]}
            </span>
            {highestSeverity.severity === 'critical' && (
              <span className="px-2 py-0.5 text-xs font-bold bg-white/30 dark:bg-slate-800/30 rounded">
                {config.action[language]}
              </span>
            )}
          </div>

          <ul className="space-y-1" role="list">
            {alert.flags.map((flag, idx) => (
              <li key={idx} className={cn('flex items-start gap-2 text-sm', getSafetyColor(flag.severity))}>
                <span className="flex-shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full" aria-hidden="true" />
                <div>
                  <p className="font-medium">{flag.message}</p>
                  <p className="text-xs mt-0.5 opacity-80">{flag.recommendedAction}</p>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <button
          onClick={onDismiss}
          className="flex-shrink-0 p-1 rounded-lg hover:bg-white/20 dark:hover:bg-slate-700/20 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-current"
          aria-label="Dismiss alert"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}