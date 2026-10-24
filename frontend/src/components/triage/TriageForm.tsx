'use client';

import React, { useState } from 'react';
import { cn } from '@/lib/utils';

export interface TriageFormData {
  chiefComplaint: string;
  symptoms: string[];
  duration: string;
  severity: number;
  age?: number;
  gender?: 'male' | 'female' | 'other';
  existingConditions: string[];
  medications: string[];
  allergies: string[];
  language: 'en' | 'hi' | 'hinglish';
}

const TRANSLATIONS = {
  en: {
    title: 'Health Assessment',
    subtitle: 'Enter patient details for AI-powered triage',
    chiefComplaint: 'Chief Complaint',
    chiefComplaintPlaceholder: 'e.g., Chest pain, difficulty breathing, severe headache',
    symptoms: 'Associated Symptoms',
    symptomsPlaceholder: 'Select or type symptoms...',
    duration: 'Duration',
    durationOptions: [
      { value: '<1h', label: 'Less than 1 hour' },
      { value: '1-6h', label: '1-6 hours' },
      { value: '6-24h', label: '6-24 hours' },
      { value: '1-3d', label: '1-3 days' },
      { value: '3-7d', label: '3-7 days' },
      { value: '>1w', label: 'More than 1 week' },
    ],
    severity: 'Severity (1-10)',
    patientInfo: 'Patient Information (Optional)',
    age: 'Age',
    gender: 'Gender',
    genderOptions: [
      { value: 'male', label: 'Male' },
      { value: 'female', label: 'Female' },
      { value: 'other', label: 'Other' },
    ],
    conditions: 'Existing Conditions',
    conditionsPlaceholder: 'e.g., Diabetes, Hypertension, Asthma',
    medications: 'Current Medications',
    medicationsPlaceholder: 'e.g., Metformin, Lisinopril',
    allergies: 'Allergies',
    allergiesPlaceholder: 'e.g., Penicillin, Sulfa drugs',
    submit: 'Run Triage Assessment',
    submitting: 'Analyzing...',
    required: 'Required field',
  },
  hi: {
    title: 'स्वास्थ्य मूल्यांकन',
    subtitle: 'AI-संचालित ट्राइएज के लिए रोगी विवरण दर्ज करें',
    chiefComplaint: 'मुख्य शिकायत',
    chiefComplaintPlaceholder: 'उदा., सीने में दर्द, सांस लेने में कठिनाई, तेज सिरदर्द',
    symptoms: 'संबंधित लक्षण',
    symptomsPlaceholder: 'लक्षण चुनें या टाइप करें...',
    duration: 'अवधि',
    durationOptions: [
      { value: '<1h', label: '1 घंटे से कम' },
      { value: '1-6h', label: '1-6 घंटे' },
      { value: '6-24h', label: '6-24 घंटे' },
      { value: '1-3d', label: '1-3 दिन' },
      { value: '3-7d', label: '3-7 दिन' },
      { value: '>1w', label: '1 सप्ताह से अधिक' },
    ],
    severity: 'गंभीरता (1-10)',
    patientInfo: 'रोगी जानकारी (वैकल्पिक)',
    age: 'आयु',
    gender: 'लिंग',
    genderOptions: [
      { value: 'male', label: 'पुरुष' },
      { value: 'female', label: 'महिला' },
      { value: 'other', label: 'अन्य' },
    ],
    conditions: 'मौजूदा स्थितियां',
    conditionsPlaceholder: 'उदा., मधुमेह, उच्च रक्तचाप, अस्थमा',
    medications: 'वर्तमान दवाएं',
    medicationsPlaceholder: 'उदा., मेटफॉर्मिन, लिसिनोप्रिल',
    allergies: 'एलर्जी',
    allergiesPlaceholder: 'उदा., पेनिसिलिन, सल्फा दवाएं',
    submit: 'ट्राइएज मूल्यांकन चलाएं',
    submitting: 'विश्लेषण कर रहे हैं...',
    required: 'आवश्यक फ़ील्ड',
  },
  hinglish: {
    title: 'Health Assessment',
    subtitle: 'AI-powered triage ke liye patient details enter karein',
    chiefComplaint: 'Chief Complaint / Main Problem',
    chiefComplaintPlaceholder: 'jaise - Chest pain, saans lene mein dikkat, tezi se sar dard',
    symptoms: 'Associated Symptoms / Saath ke lakshan',
    symptomsPlaceholder: 'Symptoms select ya type karein...',
    duration: 'Duration / Kitne time se',
    durationOptions: [
      { value: '<1h', label: '1 ghante se kam' },
      { value: '1-6h', label: '1-6 ghante' },
      { value: '6-24h', label: '6-24 ghante' },
      { value: '1-3d', label: '1-3 din' },
      { value: '3-7d', label: '3-7 din' },
      { value: '>1w', label: '1 hafte se zyada' },
    ],
    severity: 'Severity / Kitna serious (1-10)',
    patientInfo: 'Patient Info / Rogi ki jaankari (Optional)',
    age: 'Age / Umar',
    gender: 'Gender / Ling',
    genderOptions: [
      { value: 'male', label: 'Male / Purush' },
      { value: 'female', label: 'Female / Mahila' },
      { value: 'other', label: 'Other / Anya' },
    ],
    conditions: 'Existing Conditions / Pehle se bimariyan',
    conditionsPlaceholder: 'jaise - Diabetes, BP, Asthma',
    medications: 'Current Medications / Chal rahi dawaiyan',
    medicationsPlaceholder: 'jaise - Metformin, BP ki dawai',
    allergies: 'Allergies / Elergy',
    allergiesPlaceholder: 'jaise - Penicillin, Sulfa',
    submit: 'Triage Assessment Chalao',
    submitting: 'Analyze kar rahe hain...',
    required: 'Ye field zaroori hai',
  },
};

const COMMON_SYMPTOMS = {
  en: ['Chest pain', 'Shortness of breath', 'Severe headache', 'Abdominal pain', 'Fever', 'Dizziness', 'Nausea/Vomiting', 'Palpitations', 'Confusion', 'Weakness'],
  hi: ['सीने में दर्द', 'सांस फूलना', 'तेज सिरदर्द', 'पेट दर्द', 'बुखार', 'चक्कर आना', 'उल्टी/मतली', 'दिल की धड़कन तेज', 'भ्रम', 'कमजोरी'],
  hinglish: ['Chest pain', 'Saans phoolna', 'Tezi se sar dard', 'Pet dard', 'Bukhaar', 'Chakkar aana', 'Ulti/matli', 'Dil ki dhadkan tej', 'Bhram', 'Kamzori'],
};

interface TriageFormProps {
  onSubmit: (data: TriageFormData) => void;
  disabled?: boolean;
  language: 'en' | 'hi' | 'hinglish';
  prefillData?: Partial<TriageFormData>;
}

export function TriageForm({ onSubmit, disabled = false, language, prefillData }: TriageFormProps) {
  const t = TRANSLATIONS[language];
  const symptomsList = COMMON_SYMPTOMS[language];

  const [formData, setFormData] = useState<TriageFormData>({
    chiefComplaint: '',
    symptoms: [],
    duration: '',
    severity: 5,
    age: undefined,
    gender: undefined,
    existingConditions: [],
    medications: [],
    allergies: [],
    language,
    ...prefillData,
  });

  const [customSymptom, setCustomSymptom] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.chiefComplaint.trim()) return;
    onSubmit(formData);
  };

  const toggleSymptom = (symptom: string) => {
    setFormData(prev => ({
      ...prev,
      symptoms: prev.symptoms.includes(symptom)
        ? prev.symptoms.filter(s => s !== symptom)
        : [...prev.symptoms, symptom],
    }));
  };

  const addCustomSymptom = () => {
    if (customSymptom.trim() && !formData.symptoms.includes(customSymptom.trim())) {
      setFormData(prev => ({ ...prev, symptoms: [...prev.symptoms, customSymptom.trim()] }));
      setCustomSymptom('');
    }
  };

  const handleArrayInput = (field: keyof TriageFormData, value: string) => {
    const items = value.split(',').map(s => s.trim()).filter(Boolean);
    setFormData(prev => ({ ...prev, [field]: items }));
  };

  return (
    <form onSubmit={handleSubmit} className="bg-card border border-border rounded-2xl p-6 shadow-sm" noValidate>
      <header className="mb-6">
        <h2 className="text-xl font-semibold text-foreground">{t.title}</h2>
        <p className="text-sm text-muted-foreground mt-1">{t.subtitle}</p>
      </header>

      <div className="space-y-5">
        {/* Chief Complaint */}
        <div>
          <label htmlFor="chiefComplaint" className="block text-sm font-medium text-foreground mb-2">
            {t.chiefComplaint} <span className="text-danger" aria-hidden="true">*</span>
          </label>
          <textarea
            id="chiefComplaint"
            value={formData.chiefComplaint}
            onChange={e => setFormData(prev => ({ ...prev, chiefComplaint: e.target.value }))}
            placeholder={t.chiefComplaintPlaceholder}
            rows={2}
            required
            disabled={disabled}
            className="w-full px-4 py-3 bg-muted border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 resize-y"
            aria-describedby="chiefComplaint-hint"
          />
          <p id="chiefComplaint-hint" className="sr-only">{t.required}</p>
        </div>

        {/* Symptoms */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-2">{t.symptoms}</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {symptomsList.map((symptom, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => toggleSymptom(symptom)}
                disabled={disabled}
                className={cn(
                  'px-3 py-1.5 text-sm rounded-lg border transition-colors',
                  formData.symptoms.includes(symptom)
                    ? 'bg-primary text-white border-primary'
                    : 'bg-muted text-foreground border-border hover:bg-border'
                )}
                aria-pressed={formData.symptoms.includes(symptom)}
              >
                {symptom}
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              value={customSymptom}
              onChange={e => setCustomSymptom(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addCustomSymptom())}
              placeholder={t.symptomsPlaceholder}
              disabled={disabled}
              className="flex-1 px-3 py-2 bg-muted border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
            />
            <button
              type="button"
              onClick={addCustomSymptom}
              disabled={disabled || !customSymptom.trim()}
              className="px-4 py-2 text-sm font-medium text-primary bg-primary-light/50 border border-primary/20 rounded-xl hover:bg-primary-light transition-colors disabled:opacity-50"
            >
              Add
            </button>
          </div>
        </div>

        {/* Duration & Severity Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="duration" className="block text-sm font-medium text-foreground mb-2">{t.duration}</label>
            <select
              id="duration"
              value={formData.duration}
              onChange={e => setFormData(prev => ({ ...prev, duration: e.target.value }))}
              disabled={disabled}
              className="w-full px-4 py-3 bg-muted border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
            >
              <option value="">{t.durationOptions[0].label}</option>
              {t.durationOptions.map(opt => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              {t.severity}: <span className="font-normal text-primary">{formData.severity}</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={formData.severity}
              onChange={e => setFormData(prev => ({ ...prev, severity: Number(e.target.value) }))}
              disabled={disabled}
              className="w-full h-2 bg-muted rounded-lg appearance-none accent-primary"
              aria-label={t.severity}
            />
          </div>
        </div>

        {/* Patient Info Section */}
        <fieldset className="border-t border-border pt-6">
          <legend className="text-sm font-medium text-foreground mb-4">{t.patientInfo}</legend>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="age" className="block text-sm font-medium text-foreground mb-2">{t.age}</label>
              <input
                id="age"
                type="number"
                min="0"
                max="120"
                value={formData.age ?? ''}
                onChange={e => setFormData(prev => ({ ...prev, age: e.target.value ? Number(e.target.value) : undefined }))}
                disabled={disabled}
                className="w-full px-4 py-3 bg-muted border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
                placeholder="Optional"
              />
            </div>
            <div>
              <label htmlFor="gender" className="block text-sm font-medium text-foreground mb-2">{t.gender}</label>
              <select
                id="gender"
                value={formData.gender ?? ''}
                onChange={e => setFormData(prev => ({ ...prev, gender: e.target.value as any }))}
                disabled={disabled}
                className="w-full px-4 py-3 bg-muted border border-border rounded-xl text-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50"
              >
                <option value="">Select</option>
                {t.genderOptions.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            <div>
              <label htmlFor="conditions" className="block text-sm font-medium text-foreground mb-2">{t.conditions}</label>
              <textarea
                id="conditions"
                value={formData.existingConditions.join(', ')}
                onChange={e => handleArrayInput('existingConditions', e.target.value)}
                placeholder={t.conditionsPlaceholder}
                rows={2}
                disabled={disabled}
                className="w-full px-4 py-3 bg-muted border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 resize-y"
              />
            </div>
            <div>
              <label htmlFor="medications" className="block text-sm font-medium text-foreground mb-2">{t.medications}</label>
              <textarea
                id="medications"
                value={formData.medications.join(', ')}
                onChange={e => handleArrayInput('medications', e.target.value)}
                placeholder={t.medicationsPlaceholder}
                rows={2}
                disabled={disabled}
                className="w-full px-4 py-3 bg-muted border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 resize-y"
              />
            </div>
            <div>
              <label htmlFor="allergies" className="block text-sm font-medium text-foreground mb-2">{t.allergies}</label>
              <textarea
                id="allergies"
                value={formData.allergies.join(', ')}
                onChange={e => handleArrayInput('allergies', e.target.value)}
                placeholder={t.allergiesPlaceholder}
                rows={2}
                disabled={disabled}
                className="w-full px-4 py-3 bg-muted border border-border rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 resize-y"
              />
            </div>
          </div>
        </fieldset>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={disabled || !formData.chiefComplaint.trim()}
          className={cn(
            'w-full py-3.5 px-6 text-lg font-semibold rounded-xl transition-all',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
            disabled || !formData.chiefComplaint.trim()
              ? 'bg-muted text-muted-foreground cursor-not-allowed'
              : 'bg-primary text-white hover:bg-primary-hover active:scale-[0.98]'
          )}
        >
          {disabled ? t.submitting : t.submit}
        </button>
      </div>
    </form>
  );
}