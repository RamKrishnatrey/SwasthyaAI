'use client';

import React from 'react';
import { cn } from '@/lib/utils';

const TRANSLATIONS = {
  en: { title: 'Patient Queue', empty: 'No patients in queue', priority: 'Priority', assessed: 'Assessed', waiting: 'Waiting', triage: 'Triage' },
  hi: { title: 'रोगी कतार', empty: 'कतार में कोई रोगी नहीं', priority: 'प्राथमिकता', assessed: 'मूल्यांकित', waiting: 'प्रतीक्षा', triage: 'ट्राइएज' },
  hinglish: { title: 'Patient Queue / Rogi Queue', empty: 'Queue mein koi rogi nahi', priority: 'Priority', assessed: 'Assessed / Mulyankit', waiting: 'Waiting / Intezaar', triage: 'Triage' },
};

const CATEGORY_COLORS = {
  emergency: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-300',
  urgent: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300',
  'semi-urgent': 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  'non-urgent': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  'self-care': 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-300',
};

interface Patient {
  id: string;
  name: string;
  age?: number;
  chiefComplaint: string;
  triageCategory: keyof typeof CATEGORY_COLORS;
  riskScore: number;
  timestamp: string;
  status: 'waiting' | 'assessed' | 'in-progress';
}

interface PatientQueueProps {
  queue: Patient[];
  currentPatientId?: string;
  onSelectPatient: (id: string) => void;
  language: 'en' | 'hi' | 'hinglish';
}

export function PatientQueue({ queue, currentPatientId, onSelectPatient, language }: PatientQueueProps) {
  const t = TRANSLATIONS[language];

  if (queue.length === 0) {
    return (
      <div className="bg-card border border-border rounded-2xl p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">{t.title}</h3>
        <div className="text-center py-8 text-muted-foreground">
          <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <p>{t.empty}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card border border-border rounded-2xl p-6">
      <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
        {t.title}
        <span className="ml-auto px-2 py-0.5 text-xs font-medium bg-primary-light text-primary dark:bg-primary/20 rounded-full">
          {queue.length}
        </span>
      </h3>

      <div className="space-y-3 max-h-96 overflow-y-auto" role="list" aria-label={t.title}>
        {queue.map((patient, idx) => (
          <button
            key={patient.id}
            onClick={() => onSelectPatient(patient.id)}
            className={cn(
              'w-full text-left p-4 rounded-xl border transition-all',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
              patient.id === currentPatientId
                ? 'bg-primary/5 border-primary ring-2 ring-primary/20'
                : 'bg-card border-border hover:bg-muted/50'
            )}
            role="listitem"
            aria-current={patient.id === currentPatientId ? 'true' : 'false'}
            aria-label={`${patient.name}, ${t.triage}: ${patient.triageCategory}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap mb-1">
                  <span className="font-medium text-foreground truncate">{patient.name}</span>
                  {patient.age && <span className="text-sm text-muted-foreground">{patient.age}y</span>}
                  {patient.id === currentPatientId && (
                    <span className="ml-auto px-1.5 py-0.5 text-[10px] font-bold bg-primary text-white rounded">
                      {t.assessed}
                    </span>
                  )}
                </div>
                <p className="text-sm text-muted-foreground truncate mb-2">{patient.chiefComplaint}</p>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className={cn('px-2 py-0.5 text-xs font-medium rounded', CATEGORY_COLORS[patient.triageCategory])}>
                    {t.triage}: {patient.triageCategory}
                  </span>
                  <span className="px-2 py-0.5 text-xs font-medium bg-muted text-muted-foreground rounded">
                    Risk: {Math.round(patient.riskScore * 100)}%
                  </span>
                  <span className="px-2 py-0.5 text-xs font-medium bg-muted text-muted-foreground rounded">
                    {patient.status === 'assessed' ? t.assessed : t.waiting}
                  </span>
                </div>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}