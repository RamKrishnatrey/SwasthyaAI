'use client';

import React from 'react';
import { cn } from '@/lib/utils';

const TRANSLATIONS = {
  en: {
    title: 'Recommended Resources',
    emergency: 'Emergency Services',
    urgentCare: 'Urgent Care',
    selfCare: 'Self-Care Guidance',
    specialist: 'Specialist Referral',
    callNow: 'Call Now',
    findNearby: 'Find Nearby',
    learnMore: 'Learn More',
    disclaimer: 'These are general recommendations. Always follow your healthcare provider\'s advice.',
  },
  hi: {
    title: 'अनुशंसित संसाधन',
    emergency: 'आपातकालीन सेवाएं',
    urgentCare: 'तत्काल देखभाल',
    selfCare: 'स्वयं-देखभाल मार्गदर्शन',
    specialist: 'विशेषज्ञ रेफरल',
    callNow: 'अभी कॉल करें',
    findNearby: 'पास में खोजें',
    learnMore: 'और जानें',
    disclaimer: 'ये सामान्य सिफारिशें हैं। हमेशा अपने स्वास्थ्य सेवा प्रदाता की सलाह का पालन करें।',
  },
  hinglish: {
    title: 'Recommended Resources / Sujhav',
    emergency: 'Emergency Services / Emergency seva',
    urgentCare: 'Urgent Care / Turant care',
    selfCare: 'Self-Care Guidance / Apni dekhbhal',
    specialist: 'Specialist Referral / Specialist ke paas jane ka sujhav',
    callNow: 'Call Now / Abhi call karein',
    findNearby: 'Find Nearby / Paas dhoondhein',
    learnMore: 'Learn More / Aur jaanein',
    disclaimer: 'Ye general recommendations hain. Hamesha apne doctor ki salah follow karein.',
  },
};

const RESOURCES_BY_CATEGORY = {
  emergency: [
    { label: 'Ambulance (108)', action: 'tel:108', type: 'call' as const, icon: '🚑' },
    { label: 'Emergency (112)', action: 'tel:112', type: 'call' as const, icon: '📞' },
    { label: 'Poison Control', action: 'tel:1800116117', type: 'call' as const, icon: '☠️' },
    { label: 'Nearest ER', action: '/nearest-er', type: 'link' as const, icon: '🏥' },
  ],
  urgent: [
    { label: 'Urgent Care Centers', action: '/urgent-care', type: 'link' as const, icon: '🏥' },
    { label: 'Telemedicine Consult', action: '/telemedicine', type: 'link' as const, icon: '💻' },
    { label: 'Pharmacy Locator', action: '/pharmacy', type: 'link' as const, icon: '💊' },
  ],
  'semi-urgent': [
    { label: 'Same-Day Appointment', action: '/appointment', type: 'link' as const, icon: '📅' },
    { label: 'Symptom Checker', action: '/symptom-checker', type: 'link' as const, icon: '🔍' },
    { label: 'Health Hotline', action: 'tel:1800112345', type: 'call' as const, icon: '📞' },
  ],
  'non-urgent': [
    { label: 'Primary Care Booking', action: '/primary-care', type: 'link' as const, icon: '👨‍⚕️' },
    { label: 'Health Education', action: '/health-education', type: 'link' as const, icon: '📚' },
    { label: 'Wellness Tips', action: '/wellness', type: 'link' as const, icon: '💚' },
  ],
  'self-care': [
    { label: 'Self-Care Guide', action: '/self-care', type: 'link' as const, icon: '🏠' },
    { label: 'OTC Medication Guide', action: '/otc-guide', type: 'link' as const, icon: '💊' },
    { label: 'Follow-up Reminder', action: '/reminder', type: 'link' as const, icon: '⏰' },
  ],
};

interface ResourcePanelProps {
  triageCategory?: string;
  resources?: string[];
  language: 'en' | 'hi' | 'hinglish';
}

export function ResourcePanel({ triageCategory, resources, language }: ResourcePanelProps) {
  const t = TRANSLATIONS[language];
  const category = triageCategory ?? 'self-care';
  const categoryResources = RESOURCES_BY_CATEGORY[category as keyof typeof RESOURCES_BY_CATEGORY] ?? RESOURCES_BY_CATEGORY['self-care'];

  return (
    <div className="bg-card border border-border rounded-2xl p-5">
      <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
        <svg className="w-5 h-5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        {t.title}
      </h3>

      <div className="space-y-3" role="list" aria-label={t.title}>
        {categoryResources.map((resource, idx) => (
          <button
            key={idx}
            onClick={() => {
              if (resource.type === 'call' && resource.action.startsWith('tel:')) {
                window.location.href = resource.action;
              } else if (resource.type === 'link') {
                // In real app, navigate to internal route
                alert(`Navigate to: ${resource.action}`);
              }
            }}
            className={cn(
              'w-full p-4 rounded-xl border transition-all text-left',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
              resource.type === 'call'
                ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 hover:bg-red-100 dark:hover:bg-red-900/30'
                : 'bg-muted/50 border-border hover:bg-muted'
            )}
            role="listitem"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl" aria-hidden="true">{resource.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-foreground">{resource.label}</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  {resource.type === 'call' ? t.callNow : t.findNearby}
                </p>
              </div>
              <svg className="w-5 h-5 text-muted-foreground flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </div>
          </button>
        ))}

        {/* Custom resources from assessment */}
        {resources && resources.length > 0 && (
          <>
            <div className="pt-2 border-t border-border" />
            {resources.map((resource, idx) => (
              <div key={idx} className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                <span className="text-xl" aria-hidden="true">📋</span>
                <p className="text-sm text-foreground flex-1">{resource}</p>
              </div>
            ))}
          </>
        )}

        {/* Disclaimer */}
        <div className="pt-3 border-t border-border">
          <p className="text-xs text-muted-foreground">{t.disclaimer}</p>
        </div>
      </div>
    </div>
  );
}