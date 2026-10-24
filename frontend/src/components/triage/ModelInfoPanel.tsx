'use client';

import React from 'react';
import { ModelInfo } from '@/types/agent';
import { cn } from '@/lib/utils';

const TRANSLATIONS = {
  en: {
    title: 'Model Information',
    model: 'Model',
    version: 'Version',
    taskType: 'Task Type',
    confidence: 'Confidence',
    limitations: 'Known Limitations',
    noLimitations: 'No known limitations reported',
  },
  hi: {
    title: 'मॉडल जानकारी',
    model: 'मॉडल',
    version: 'संस्करण',
    taskType: 'कार्य प्रकार',
    confidence: 'आत्मविश्वास',
    limitations: 'ज्ञात सीमाएं',
    noLimitations: 'कोई ज्ञात सीमा नहीं बताई गई',
  },
  hinglish: {
    title: 'Model Information / Model ki jankari',
    model: 'Model',
    version: 'Version',
    taskType: 'Task Type / Kaam ka prakar',
    confidence: 'Confidence / Vishwas',
    limitations: 'Known Limitations / Known hadden',
    noLimitations: 'Koi known limitations nahi batayi gayi',
  },
};

interface ModelInfoPanelProps {
  modelInfo: ModelInfo;
  language?: 'en' | 'hi' | 'hinglish';
}

export function ModelInfoPanel({ modelInfo, language = 'en' }: ModelInfoPanelProps) {
  const t = TRANSLATIONS[language];

  return (
    <details className="bg-card border border-border rounded-2xl p-5 animate-fade-in">
      <summary className="cursor-pointer flex items-center gap-2 text-sm font-medium text-foreground hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded">
        <svg className="w-5 h-5 text-primary flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <span>{t.title}</span>
      </summary>
      <div className="mt-4 space-y-3 text-sm">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-muted-foreground">{t.model}</p>
            <p className="font-mono font-medium">{modelInfo.modelName}</p>
          </div>
          <div>
            <p className="text-muted-foreground">{t.version}</p>
            <p className="font-mono font-medium">{modelInfo.version}</p>
          </div>
          <div>
            <p className="text-muted-foreground">{t.taskType}</p>
            <p className="font-medium capitalize">{modelInfo.predictionType.replace('_', ' ')}</p>
          </div>
          <div>
            <p className="text-muted-foreground">{t.confidence}</p>
            <p className="font-medium">{modelInfo.confidence !== undefined ? Math.round(modelInfo.confidence * 100) + '%' : 'N/A'}</p>
          </div>
        </div>

        {modelInfo.limitations && modelInfo.limitations.length > 0 ? (
          <div className="pt-3 border-t border-border">
            <p className="text-muted-foreground mb-2">{t.limitations}</p>
            <ul className="space-y-1.5 pl-4" role="list">
              {modelInfo.limitations.map((limitation, idx) => (
                <li key={idx} className="flex items-start gap-2 text-muted-foreground">
                  <span className="flex-shrink-0 mt-0.5 w-1.5 h-1.5 rounded-full bg-muted-foreground" aria-hidden="true" />
                  <span className="text-sm">{limitation}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <div className="pt-3 border-t border-border text-muted-foreground text-sm">
            {t.noLimitations}
          </div>
        )}
      </div>
    </details>
  );
}