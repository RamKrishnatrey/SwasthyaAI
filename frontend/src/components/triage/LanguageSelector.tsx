'use client';

import React from 'react';
import { cn } from '@/lib/utils';

const LANGUAGES = [
  { code: 'en', name: 'English', native: 'English', flag: '🇮🇳' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', flag: '🇮🇳' },
  { code: 'hinglish', name: 'Hinglish', native: 'Hinglish', flag: '🇮🇳' },
] as const;

const TRANSLATIONS = {
  en: { label: 'Language', ariaLabel: 'Select language' },
  hi: { label: 'भाषा', ariaLabel: 'भाषा चुनें' },
  hinglish: { label: 'Language / Bhasha', ariaLabel: 'Bhasha chunein' },
};

interface LanguageSelectorProps {
  currentLanguage: 'en' | 'hi' | 'hinglish';
  onChange: (lang: 'en' | 'hi' | 'hinglish') => void;
  disabled?: boolean;
}

export function LanguageSelector({ currentLanguage, onChange, disabled = false }: LanguageSelectorProps) {
  const t = TRANSLATIONS[currentLanguage];

  return (
    <div className="flex items-center gap-2" role="group" aria-label={t.ariaLabel}>
      <label htmlFor="language-select" className="text-sm font-medium text-foreground whitespace-nowrap">
        {t.label}
      </label>
      <select
        id="language-select"
        value={currentLanguage}
        onChange={e => onChange(e.target.value as any)}
        disabled={disabled}
        className="px-3 py-2 bg-muted border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 cursor-pointer"
        aria-label={t.ariaLabel}
      >
        {LANGUAGES.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.native}
          </option>
        ))}
      </select>
    </div>
  );
}