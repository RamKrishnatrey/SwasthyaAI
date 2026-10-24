'use client';

import React from 'react';
import { ModelInfo } from '@/types/agent';
import { cn } from '@/lib/utils';

interface ModelInfoProps {
  modelInfo: ModelInfo | undefined;
}

export function ModelInfoComponent({ modelInfo }: ModelInfoProps) {
  if (!modelInfo) return null;

  return (
    <details className="mt-3" role="region" aria-label="Model information">
      <summary className="cursor-pointer flex items-center gap-2 text-xs text-muted-foreground hover:text-secondary transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 rounded">
        <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <span>Model Details</span>
        <svg className="w-3 h-3 ml-auto transition-transform group-open:rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </summary>
      <div className="mt-2 p-3 bg-muted rounded-lg text-xs space-y-1.5">
        <div className="flex justify-between">
          <span className="text-muted-foreground">Model</span>
          <span className="font-mono">{modelInfo.modelName}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Version</span>
          <span className="font-mono">{modelInfo.version}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Task Type</span>
          <span>{modelInfo.predictionType}</span>
        </div>
        {modelInfo.confidence !== undefined && (
          <div className="flex justify-between">
            <span className="text-muted-foreground">Confidence</span>
            <span>{Math.round(modelInfo.confidence * 100)}%</span>
          </div>
        )}
        {modelInfo.limitations && modelInfo.limitations.length > 0 && (
          <div className="pt-1 border-t border-border">
            <div className="text-muted-foreground mb-1">Limitations:</div>
            <ul className="space-y-0.5 pl-4">
              {modelInfo.limitations.map((limitation, idx) => (
                <li key={idx} className="flex items-start gap-1">
                  <span className="flex-shrink-0 mt-0.5 w-1 h-1 rounded-full bg-muted-foreground" aria-hidden="true" />
                  <span>{limitation}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </details>
  );
}