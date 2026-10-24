'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Header } from '@/components/layout/Header';
import { TriageForm } from '@/components/triage/TriageForm';
import { TriageResults } from '@/components/triage/TriageResults';
import { SafetyAlert } from '@/components/triage/SafetyAlert';
import { FollowUpSection } from '@/components/triage/FollowUpSection';
import { PatientQueue } from '@/components/triage/PatientQueue';
import { ResourcePanel } from '@/components/triage/ResourcePanel';
import { LanguageSelector } from '@/components/triage/LanguageSelector';
import { ModelInfoPanel } from '@/components/triage/ModelInfoPanel';
import { useTriageSession } from '@/hooks/useTriageSession';
import { cn } from '@/lib/utils';

export default function TriageDashboard() {
  const {
    state,
    submitAssessment,
    answerFollowUp,
    skipFollowUp,
    addToQueue,
    clearResults,
    setLanguage,
  } = useTriageSession();

  return (
    <div className="flex flex-col h-screen bg-background">
      <a href="#main-content" className="skip-link">Skip to main content</a>

      <Header
        sessionStatus={state.status}
        currentLanguage={state.language}
        onLanguageChange={setLanguage}
      />

      <main id="main-content" className="flex-1 overflow-auto" role="main">
        <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
          {/* Language Selector */}
          <LanguageSelector
            currentLanguage={state.language}
            onChange={setLanguage}
            disabled={state.status === 'processing'}
          />

          {/* Safety Alert Banner */}
          {state.safetyAlert && (
            <SafetyAlert
              alert={state.safetyAlert}
              onDismiss={() => {}}
            />
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column: Input Form & Follow-up */}
            <div className="lg:col-span-2 space-y-6">
              {/* Assessment Form */}
              {!state.results && (
                <TriageForm
                  onSubmit={submitAssessment}
                  disabled={state.status === 'processing'}
                  language={state.language}
                  prefillData={state.prefillData}
                />
              )}

              {/* Follow-up Questions */}
              {state.followUpQuestion && (
                <FollowUpSection
                  question={state.followUpQuestion}
                  onAnswer={answerFollowUp}
                  onSkip={skipFollowUp}
                  disabled={state.status === 'processing'}
                  language={state.language}
                />
              )}

              {/* Results Display */}
              {state.results && (
                <TriageResults
                  results={state.results}
                  onNewAssessment={clearResults}
                  onAddToQueue={addToQueue}
                  language={state.language}
                />
              )}

              {/* Model Info Panel */}
              {state.results?.modelInfo && (
                <ModelInfoPanel modelInfo={state.results.modelInfo} />
              )}
            </div>

            {/* Right Column: Queue & Resources */}
            <div className="lg:col-span-1 space-y-6">
              <PatientQueue
                queue={state.queue}
                currentPatientId={state.currentPatientId}
                onSelectPatient={(id) => {}}
                language={state.language}
              />

              <ResourcePanel
                triageCategory={state.results?.structuredData?.triageCategory}
                resources={state.results?.structuredData?.suggestedActions}
                language={state.language}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}