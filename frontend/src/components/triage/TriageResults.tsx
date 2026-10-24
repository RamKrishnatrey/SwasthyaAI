'use client';

import React from 'react';
import { AgentResponse, SafetyLevel } from '@/types/agent';
import { cn, getSafetyColor, getSafetyBgColor, formatTimestamp } from '@/lib/utils';

const TRANSLATIONS = {
  en: {
    triageResult: 'Triage Assessment Result',
    triageCategory: 'Triage Category',
    riskScore: 'Risk Score',
    suggestedActions: 'Recommended Actions',
    disclaimer: 'Disclaimer',
    newAssessment: 'New Assessment',
    addToQueue: 'Add to Patient Queue',
    modelDetails: 'Model Details',
    timestamp: 'Assessed at',
    confidence: 'Model Confidence',
    limitations: 'Known Limitations',
  },
  hi: {
    triageResult: 'ट्राइएज मूल्यांकन परिणाम',
    triageCategory: 'ट्राइएज श्रेणी',
    riskScore: 'जोखिम स्कोर',
    suggestedActions: 'अनुशंसित कार्रवाई',
    disclaimer: 'अस्वीकरण',
    newAssessment: 'नया मूल्यांकन',
    addToQueue: 'रोगी कतार में जोड़ें',
    modelDetails: 'मॉडल विवरण',
    timestamp: 'मूल्यांकन समय',
    confidence: 'मॉडल आत्मविश्वास',
    limitations: 'ज्ञात सीमाएं',
  },
  hinglish: {
    triageResult: 'Triage Assessment Result',
    triageCategory: 'Triage Category / Shreni',
    riskScore: 'Risk Score / Jokhim score',
    suggestedActions: 'Recommended Actions / Sujhav',
    disclaimer: 'Disclaimer / Sawdhani',
    newAssessment: 'New Assessment / Naya mulyankan',
    addToQueue: 'Add to Patient Queue / Queue mein jodo',
    modelDetails: 'Model Details / Model ki jankari',
    timestamp: 'Assessed at / Samay',
    confidence: 'Model Confidence / Vishwas',
    limitations: 'Known Limitations / Known hadden',
  },
};

const CATEGORY_COLORS = {
  emergency: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  urgent: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  'semi-urgent': 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  'non-urgent': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  'self-care': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
};

const CATEGORY_LABELS = {
  emergency: { en: '🔴 Emergency', hi: '🔴 आपातकाल', hinglish: '🔴 Emergency' },
  urgent: { en: '🟠 Urgent', hi: '🟠 तत्काल', hinglish: '🟠 Urgent' },
  'semi-urgent': { en: '🟡 Semi-Urgent', hi: '🟡 अर्ध-तत्काल', hinglish: '🟡 Semi-Urgent' },
  'non-urgent': { en: '🔵 Non-Urgent', hi: '🔵 गैर-तत्काल', hinglish: '🔵 Non-Urgent' },
  'self-care': { en: '🟢 Self-Care', hi: '🟢 स्वयं-देखभाल', hinglish: '🟢 Self-Care' },
};

interface TriageResultsProps {
  results: AgentResponse;
  onNewAssessment: () => void;
  onAddToQueue: () => void;
  language: 'en' | 'hi' | 'hinglish';
}

export function TriageResults({ results, onNewAssessment, onAddToQueue, language }: TriageResultsProps) {
  const t = TRANSLATIONS[language];
  const category = results.structuredData?.triageCategory ?? 'non-urgent';
  const riskScore = results.structuredData?.riskScore ?? 0;

  return (
    <div className="bg-card border border-border rounded-2xl p-6 shadow-sm animate-fade-in" role="region" aria-labelledby="results-heading">
      <header className="flex items-center justify-between mb-6">
        <h2 id="results-heading" className="text-xl font-semibold text-foreground">{t.triageResult}</h2>
        <time className="text-sm text-muted-foreground" dateTime={results.timestamp}>
          {formatTimestamp(new Date(results.timestamp))}
        </time>
      </header>

      {/* Primary Result Card */}
      <div className={cn('rounded-xl p-5 mb-6', CATEGORY_COLORS[category])}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium opacity-80">{t.triageCategory}</p>
            <p className="text-2xl font-bold mt-1">
              {CATEGORY_LABELS[category]?.[language] ?? CATEGORY_LABELS[category]?.en}
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium opacity-80">{t.riskScore}</p>
            <p className="text-3xl font-bold mt-1">{Math.round(riskScore * 100)}%</p>
          </div>
        </div>
      </div>

      {/* AI Response */}
      <div className="mb-6 p-4 bg-muted/50 rounded-xl">
        <h3 className="text-sm font-medium text-foreground mb-2">AI Assessment</h3>
        <p className="text-foreground whitespace-pre-wrap">{results.response}</p>
      </div>

      {/* Safety Flags */}
      {results.safetyFlags && results.safetyFlags.length > 0 && (
        <div className="mb-6 space-y-3" role="alert" aria-label="Safety flags">
          <h3 className="text-sm font-medium text-foreground">Safety Alerts</h3>
          {results.safetyFlags.map((flag, idx) => (
            <div
              key={idx}
              className={cn('p-3 rounded-lg border', getSafetyBgColor(flag.severity))}
            >
              <div className="flex items-start gap-2">
                <span className="flex-shrink-0" aria-hidden="true">
                  {flag.severity === 'critical' ? '🚨' : flag.severity === 'high' ? '⚠️' : '⚡'}
                </span>
                <div className="flex-1">
                  <p className={cn('font-medium', getSafetyColor(flag.severity))}>{flag.message}</p>
                  <p className="text-sm mt-1 opacity-80">{flag.recommendedAction}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Structured Data */}
      {results.structuredData && (
        <div className="mb-6 space-y-4">
          {results.structuredData.suggestedActions && results.structuredData.suggestedActions.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-foreground mb-3">{t.suggestedActions}</h3>
              <ul className="space-y-2" role="list">
                {results.structuredData.suggestedActions.map((action, idx) => (
                  <li key={idx} className="flex items-start gap-2 p-3 bg-muted rounded-lg">
                    <span className="flex-shrink-0 mt-0.5 w-2 h-2 rounded-full bg-primary" aria-hidden="true" />
                    <span className="text-sm text-foreground">{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {results.structuredData.disclaimer && (
            <div className="p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <h4 className="text-sm font-medium text-amber-800 dark:text-amber-200 mb-1">{t.disclaimer}</h4>
              <p className="text-sm text-amber-700 dark:text-amber-300">{results.structuredData.disclaimer}</p>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-border">
        <button
          onClick={onNewAssessment}
          className="flex-1 py-2.5 px-4 text-sm font-medium text-primary bg-primary-light/50 border border-primary/20 rounded-xl hover:bg-primary-light transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary"
        >
          {t.newAssessment}
        </button>
        <button
          onClick={onAddToQueue}
          className="flex-1 py-2.5 px-4 text-sm font-medium text-white bg-primary rounded-xl hover:bg-primary-hover transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
        >
          {t.addToQueue}
        </button>
      </div>

      {/* Model Info Summary */}
      {results.modelInfo && (
        <details className="mt-4">
          <summary className="cursor-pointer flex items-center gap-2 text-sm text-muted-foreground hover:text-secondary">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>{t.modelDetails}</span>
          </summary>
          <div className="mt-3 p-3 bg-muted rounded-lg text-xs space-y-2">
            <div className="flex justify-between"><span className="text-muted-foreground">{t.confidence}</span><span>{results.modelInfo.confidence ? Math.round(results.modelInfo.confidence * 100) + '%' : 'N/A'}</span></div>
            <div className="flex justify-between"><span className="text-muted-foreground">Model</span><span className="font-mono">{results.modelInfo.modelName} v{results.modelInfo.version}</span></div>
            {results.modelInfo.limitations && results.modelInfo.limitations.length > 0 && (
              <div>
                <div className="text-muted-foreground mb-1">{t.limitations}</div>
                <ul className="space-y-0.5 pl-4">
                  {results.modelInfo.limitations.map((lim, idx) => (
                    <li key={idx} className="flex items-start gap-1 text-muted-foreground">
                      <span className="flex-shrink-0 mt-0.5 w-1 h-1 rounded-full" aria-hidden="true" />
                      {lim}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  );
}