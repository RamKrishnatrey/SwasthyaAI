// SwasthyaAI Mobile Symptoms Screen
// Symptom checker with intake form, follow-up questions, triage results, safety alerts

import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, KeyboardAvoidingView, Platform, Alert, ActivityIndicator, Keyboard } from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons, MaterialCommunityIcons, FontAwesome5 } from '@expo/vector-icons';
import { useAuth } from '../../src/context/AuthContext';
import { theme } from '../../src/utils/theme';
import api from '../../src/services/api';
import { SymptomAssessment, TriageResult } from '../../src/types';

interface SymptomFormData {
  chiefComplaint: string;
  age: string;
  gender: 'male' | 'female' | 'other' | '';
  duration: string;
  severity: 'mild' | 'moderate' | 'severe' | '';
  additionalInfo: string;
}

export default function SymptomsScreen() {
  const router = useRouter();
  const { patientProfile } = useAuth();
  const [step, setStep] = useState<'intake' | 'followup' | 'results'>('intake');
  const [formData, setFormData] = useState<SymptomFormData>({
    chiefComplaint: '',
    age: patientProfile?.date_of_birth ? calculateAge(patientProfile.date_of_birth).toString() : '',
    gender: patientProfile?.gender || '',
    duration: '',
    severity: '',
    additionalInfo: '',
  });
  const [followUpQuestions, setFollowUpQuestions] = useState<Array<{id: string; question: string; type: string; options?: string[]}>>([]);
  const [followUpAnswers, setFollowUpAnswers] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [assessment, setAssessment] = useState<SymptomAssessment | null>(null);
  const [triageResult, setTriageResult] = useState<TriageResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const calculateAge = (dob: string) => {
    const today = new Date();
    const birth = new Date(dob);
    let age = today.getFullYear() - birth.getFullYear();
    const m = today.getMonth() - birth.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
    return age;
  };

  const handleIntakeSubmit = async () => {
    if (!formData.chiefComplaint.trim() || !formData.age || !formData.gender || !formData.duration || !formData.severity) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await api.startSymptomAssessment({
        text: formData.chiefComplaint,
        language: 'en',
        age_group: getAgeGroup(parseInt(formData.age)),
        sex: formData.gender,
      });

      setAssessment(res.assessment);

      if (res.follow_up_questions && res.follow_up_questions.length > 0) {
        setFollowUpQuestions(res.follow_up_questions.map((q: any, i: number) => ({
          id: q.id || `q${i}`,
          question: q.question,
          type: q.type || 'text',
          options: q.options,
        })));
        setStep('followup');
      } else {
        await completeAssessment();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getAgeGroup = (age: number) => {
    if (age < 18) return 'pediatric';
    if (age < 65) return 'adult';
    return 'geriatric';
  };

  const handleFollowUpSubmit = async () => {
    setLoading(true);
    try {
      if (!assessment) return;

      const res = await api.submitFollowUpAnswers(assessment.id, followUpAnswers);
      setAssessment(res.assessment);
      await completeAssessment();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit answers. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const completeAssessment = async () => {
    if (!assessment) return;

    try {
      const res = await api.getTriageResult(assessment.id);
      setTriageResult(res);
      setStep('results');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to get results. Please try again.');
    }
  };

  const handleRestart = () => {
    setStep('intake');
    setFormData({ chiefComplaint: '', age: formData.age, gender: formData.gender, duration: '', severity: '', additionalInfo: '' });
    setFollowUpQuestions([]);
    setFollowUpAnswers({});
    setAssessment(null);
    setTriageResult(null);
  };

  if (step === 'intake') return <IntakeForm formData={formData} setFormData={setFormData} onSubmit={handleIntakeSubmit} loading={loading} error={error} />;
  if (step === 'followup') return <FollowUpForm questions={followUpQuestions} answers={followUpAnswers} setAnswers={setFollowUpAnswers} onSubmit={handleFollowUpSubmit} loading={loading} error={error} />;
  return <ResultsScreen triageResult={triageResult} assessment={assessment} onRestart={handleRestart} />;
}

function IntakeForm({ formData, setFormData, onSubmit, loading, error }: { formData: SymptomFormData; setFormData: React.Dispatch<React.SetStateAction<SymptomFormData>>; onSubmit: () => void; loading: boolean; error: string | null }) {
  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <ScrollView contentContainerStyle={{ padding: theme.spacing.xl, paddingBottom: theme.spacing.xxl }}>
        <Text style={{ ...theme.typography.h2, color: theme.colors.text, marginBottom: theme.spacing.xs }}>Symptom Checker</Text>
        <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary, marginBottom: theme.spacing.xl }}>Describe your symptoms for AI-powered triage</Text>

        {error && (
          <View style={{ backgroundColor: theme.colors.errorLight, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, marginBottom: theme.spacing.lg, borderLeftWidth: 4, borderLeftColor: theme.colors.error }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.error }}>{error}</Text>
          </View>
        )}

        <View style={{ marginBottom: theme.spacing.lg }}>
          <Label>What's your main symptom?</Label>
          <TextInput
            style={inputStyle}
            placeholder="e.g., chest pain, fever, headache..."
            value={formData.chiefComplaint}
            onChangeText={(v) => setFormData(prev => ({ ...prev, chiefComplaint: v }))}
            multiline
            numberOfLines={3}
            placeholderTextColor={theme.colors.textMuted}
          />
        </View>

        <View style={{ flexDirection: 'row', gap: theme.spacing.md, marginBottom: theme.spacing.lg }}>
          <View style={{ flex: 1 }}>
            <Label>Age</Label>
            <TextInput
              style={inputStyle}
              placeholder="Age"
              value={formData.age}
              onChangeText={(v) => setFormData(prev => ({ ...prev, age: v }))}
              keyboardType="numeric"
              placeholderTextColor={theme.colors.textMuted}
            />
          </View>
          <View style={{ flex: 1 }}>
            <Label>Gender</Label>
            <SelectInput
              value={formData.gender}
              onChange={(v) => setFormData(prev => ({ ...prev, gender: v as any }))}
              options={[
                { value: 'male', label: 'Male' },
                { value: 'female', label: 'Female' },
                { value: 'other', label: 'Other' },
              ]}
            />
          </View>
        </View>

        <View style={{ flexDirection: 'row', gap: theme.spacing.md, marginBottom: theme.spacing.lg }}>
          <View style={{ flex: 1 }}>
            <Label>Duration</Label>
            <SelectInput
              value={formData.duration}
              onChange={(v) => setFormData(prev => ({ ...prev, duration: v }))}
              options={[
                { value: 'hours', label: 'Hours' },
                { value: 'days', label: 'Days' },
                { value: 'weeks', label: 'Weeks' },
                { value: 'months', label: 'Months' },
              ]}
            />
          </View>
          <View style={{ flex: 1 }}>
            <Label>Severity</Label>
            <SelectInput
              value={formData.severity}
              onChange={(v) => setFormData(prev => ({ ...prev, severity: v as any }))}
              options={[
                { value: 'mild', label: 'Mild' },
                { value: 'moderate', label: 'Moderate' },
                { value: 'severe', label: 'Severe' },
              ]}
            />
          </View>
        </View>

        <View style={{ marginBottom: theme.spacing.xl }}>
          <Label>Additional Information (optional)</Label>
          <TextInput
            style={inputStyle}
            placeholder="Other symptoms, medical history, medications..."
            value={formData.additionalInfo}
            onChangeText={(v) => setFormData(prev => ({ ...prev, additionalInfo: v }))}
            multiline
            numberOfLines={4}
            placeholderTextColor={theme.colors.textMuted}
          />
        </View>

        <TouchableOpacity style={[primaryButtonStyle, loading && { opacity: 0.7 }]} onPress={onSubmit} disabled={loading}>
          {loading ? (
            <ActivityIndicator color={theme.colors.textOnPrimary} size="small" />
          ) : (
            <Text style={{ ...theme.typography.button, color: theme.colors.textOnPrimary }}>Analyze Symptoms</Text>
          )}
        </TouchableOpacity>

        <DisclaimerText />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

function FollowUpForm({ questions, answers, setAnswers, onSubmit, loading, error }: { questions: Array<{id: string; question: string; type: string; options?: string[]}>; answers: Record<string, string>; setAnswers: React.Dispatch<React.SetStateAction<Record<string, string>>>; onSubmit: () => void; loading: boolean; error: string | null }) {
  return (
    <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1, backgroundColor: theme.colors.background }}>
      <ScrollView contentContainerStyle={{ padding: theme.spacing.xl, paddingBottom: theme.spacing.xxl }}>
        <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: theme.spacing.lg }}>
          <View style={{ flexDirection: 'row' }}>
            {questions.map((_, i) => (
              <View key={i} style={{ width: 8, height: 8, borderRadius: 4, marginRight: 4, backgroundColor: i < questions.length - 1 ? theme.colors.primary : theme.colors.border }} />
            ))}
          </View>
        </View>

        <Text style={{ ...theme.typography.h2, color: theme.colors.text, marginBottom: theme.spacing.xs }}>Follow-up Questions</Text>
        <Text style={{ ...theme.typography.body, color: theme.colors.textSecondary, marginBottom: theme.spacing.xl }}>Answer a few more questions for better accuracy</Text>

        {error && (
          <View style={{ backgroundColor: theme.colors.errorLight, padding: theme.spacing.md, borderRadius: theme.borderRadius.md, marginBottom: theme.spacing.lg, borderLeftWidth: 4, borderLeftColor: theme.colors.error }}>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.error }}>{error}</Text>
          </View>
        )}

        {questions.map((q, index) => (
          <View key={q.id} style={{ marginBottom: theme.spacing.xl }}>
            <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginBottom: theme.spacing.md }}>
              {index + 1}. {q.question}
            </Text>
            {q.type === 'select' && q.options ? (
              <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: theme.spacing.sm }}>
                {q.options.map((opt) => (
                  <TouchableOpacity
                    key={opt}
                    style={{
                      paddingHorizontal: theme.spacing.md,
                      paddingVertical: theme.spacing.sm,
                      borderRadius: theme.borderRadius.full,
                      backgroundColor: answers[q.id] === opt ? theme.colors.primary : theme.colors.surfaceVariant,
                      borderWidth: 1,
                      borderColor: answers[q.id] === opt ? theme.colors.primary : theme.colors.border,
                    }}
                    onPress={() => setAnswers(prev => ({ ...prev, [q.id]: opt }))}
                  >
                    <Text style={{ ...theme.typography.bodySmall, color: answers[q.id] === opt ? theme.colors.textOnPrimary : theme.colors.text }}>
                      {opt}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            ) : (
              <TextInput
                style={inputStyle}
                placeholder="Type your answer..."
                value={answers[q.id] || ''}
                onChangeText={(v) => setAnswers(prev => ({ ...prev, [q.id]: v }))}
                placeholderTextColor={theme.colors.textMuted}
              />
            )}
          </View>
        ))}

        <TouchableOpacity style={[primaryButtonStyle, loading && { opacity: 0.7 }]} onPress={onSubmit} disabled={loading}>
          {loading ? (
            <ActivityIndicator color={theme.colors.textOnPrimary} size="small" />
          ) : (
            <Text style={{ ...theme.typography.button, color: theme.colors.textOnPrimary }}>Get Results</Text>
          )}
        </TouchableOpacity>

        <DisclaimerText />
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

function ResultsScreen({ triageResult, assessment, onRestart }: { triageResult: TriageResult | null; assessment: SymptomAssessment | null; onRestart: () => void }) {
  if (!triageResult) return null;

  const urgencyColors = {
    emergency: theme.colors.emergency,
    urgent: theme.colors.error,
    semi_urgent: theme.colors.warning,
    non_urgent: theme.colors.info,
    self_care: theme.colors.success,
  };

  const urgencyLabels = {
    emergency: 'EMERGENCY',
    urgent: 'URGENT',
    semi_urgent: 'SEMI-URGENT',
    non_urgent: 'NON-URGENT',
    self_care: 'SELF CARE',
  };

  const urgencyColor = urgencyColors[triageResult.urgency as keyof typeof urgencyColors] || theme.colors.textMuted;

  return (
    <ScrollView contentContainerStyle={{ padding: theme.spacing.xl, paddingBottom: theme.spacing.xxl }} style={{ backgroundColor: theme.colors.background }}>
      {/* Safety Alert */}
      {triageResult.safety.red_flag && (
        <View style={{ marginBottom: theme.spacing.lg, padding: theme.spacing.lg, borderRadius: theme.borderRadius.lg, backgroundColor: theme.colors.emergencyLight, borderWidth: 2, borderColor: theme.colors.emergency }}>
          <View style={{ flexDirection: 'row', alignItems: 'flex-start' }}>
            <View style={{ width: 40, height: 40, borderRadius: theme.borderRadius.full, backgroundColor: theme.colors.emergency, justifyContent: 'center', alignItems: 'center', marginRight: theme.spacing.md }}>
              <Ionicons name="alert-circle" size={24} color={theme.colors.textOnPrimary} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ ...theme.typography.h3, color: theme.colors.emergency }}>⚠️ Safety Alert</Text>
              <Text style={{ ...theme.typography.body, color: theme.colors.text, marginTop: theme.spacing.sm }}>
                {triageResult.safety.instructions || 'This may require immediate medical attention. Please call emergency services (112/108) or go to the nearest emergency department.'}
              </Text>
              <TouchableOpacity style={{ marginTop: theme.spacing.md, paddingHorizontal: theme.spacing.lg, paddingVertical: theme.spacing.sm, backgroundColor: theme.colors.emergency, borderRadius: theme.borderRadius.full }} onPress={() => alert('Calling 112...')}>
                <Text style={{ ...theme.typography.button, color: theme.colors.textOnPrimary }}>Call Emergency</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      )}

      {/* Urgency Banner */}
      <View style={{ marginBottom: theme.spacing.lg, padding: theme.spacing.lg, borderRadius: theme.borderRadius.lg, backgroundColor: urgencyColor + '15', borderWidth: 2, borderColor: urgencyColor }}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <View>
            <Text style={{ ...theme.typography.caption, color: urgencyColor, textTransform: 'uppercase', letterSpacing: 1 }}>Triage Level</Text>
            <Text style={{ ...theme.typography.h2, color: urgencyColor, marginTop: theme.spacing.xs }}>{urgencyLabels[triageResult.urgency as keyof typeof urgencyLabels] || triageResult.urgency?.toUpperCase()}</Text>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textSecondary, marginTop: theme.spacing.xs }}>{triageResult.reason}</Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>Confidence</Text>
            <Text style={{ ...theme.typography.h3, color: urgencyColor }}>{Math.round((triageResult.confidence || 0) * 100)}%</Text>
          </View>
        </View>
      </View>

      {/* Care Type */}
      <View style={{ marginBottom: theme.spacing.lg, padding: theme.spacing.lg, borderRadius: theme.borderRadius.lg, backgroundColor: theme.colors.surface, ...theme.shadows.sm }}>
        <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginBottom: theme.spacing.md }}>Recommended Care</Text>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md }}>
          <View style={{ width: 48, height: 48, borderRadius: theme.borderRadius.full, backgroundColor: theme.colors.primary + '15', justifyContent: 'center', alignItems: 'center' }}>
            <MaterialCommunityIcons name="hospital" size={24} color={theme.colors.primary} />
          </View>
          <View>
            <Text style={{ ...theme.typography.body, color: theme.colors.text, fontWeight: '600' }}>{triageResult.care_type?.replace('_', ' ') || 'Consult a doctor'}</Text>
            <Text style={{ ...theme.typography.bodySmall, color: theme.colors.textSecondary }}>{triageResult.urgency === 'emergency' ? 'Immediate' : triageResult.urgency === 'urgent' ? 'Within 24 hours' : 'Schedule soon'}</Text>
          </View>
        </View>
      </View>

      {/* Suggested Specialty */}
      {assessment?.suggested_specialty && (
        <View style={{ marginBottom: theme.spacing.lg, padding: theme.spacing.lg, borderRadius: theme.borderRadius.lg, backgroundColor: theme.colors.surface, ...theme.shadows.sm }}>
          <Text style={{ ...theme.typography.h4, color: theme.colors.text, marginBottom: theme.spacing.md }}>Suggested Specialty</Text>
          <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md }}>
            <View style={{ width: 48, height: 48, borderRadius: theme.borderRadius.full, backgroundColor: theme.colors.secondary + '15', justifyContent: 'center', alignItems: 'center' }}>
              <MaterialCommunityIcons name="stethoscope" size={24} color={theme.colors.secondary} />
            </View>
            <Text style={{ ...theme.typography.body, color: theme.colors.text, fontWeight: '600' }}>{assessment.suggested_specialty}</Text>
          </View>
        </View>
      )}

      {/* Matched Caregivers */}
      {assessment?.matched_caregivers && assessment.matched_caregivers.length > 0 && (
        <View style={{ marginBottom: theme.spacing.lg }}>
          <Text style={{ ...theme.typography.h3, color: theme.colors.text, marginBottom: theme.spacing.md }}>Available Providers</Text>
          {assessment.matched_caregivers.slice(0, 3).map((caregiver: any) => (
            <View key={caregiver.id} style={{ marginBottom: theme.spacing.md, padding: theme.spacing.md, borderRadius: theme.borderRadius.lg, backgroundColor: theme.colors.surface, ...theme.shadows.sm }}>
              <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
                <View style={{ flexDirection: 'row', alignItems: 'center', gap: theme.spacing.md }}>
                  <View style={{ width: 48, height: 48, borderRadius: theme.borderRadius.full, backgroundColor: theme.colors.primary + '15', justifyContent: 'center', alignItems: 'center' }}>
                    <MaterialCommunityIcons name="account" size={24} color={theme.colors.primary} />
                  </View>
                  <View>
                    <Text style={{ ...theme.typography.body, color: theme.colors.text, fontWeight: '600' }}>{caregiver.name}</Text>
                    <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>{caregiver.skills?.join(', ')}</Text>
                  </View>
                </View>
                <View style={{ alignItems: 'flex-end' }}>
                  <Text style={{ ...theme.typography.h4, color: theme.colors.primary, fontWeight: '700' }}>{caregiver.score?.total || 0}%</Text>
                  <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted }}>Match Score</Text>
                </View>
              </View>
            </View>
          ))}
        </View>
      )}

      {/* Disclaimer */}
      <View style={{ padding: theme.spacing.md, backgroundColor: theme.colors.surfaceVariant, borderRadius: theme.borderRadius.md }}>
        <Text style={{ ...theme.typography.caption, color: theme.colors.textMuted, textAlign: 'center' }}>
          {triageResult.disclaimer || 'This is an AI-powered assessment for informational purposes only. It does not replace professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.'}
        </Text>
      </View>

      {/* Actions */}
      <View style={{ marginTop: theme.spacing.xl, gap: theme.spacing.md }}>
        <TouchableOpacity style={primaryButtonStyle} onPress={() => alert('Booking feature coming soon')}>
          <Text style={{ ...theme.typography.button, color: theme.colors.textOnPrimary }}>Book Appointment</Text>
        </TouchableOpacity>
        <TouchableOpacity style={secondaryButtonStyle} onPress={onRestart}>
          <Text style={{ ...theme.typography.button, color: theme.colors.primary }}>Check Another Symptom</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

function Label({ children }: { children: React.ReactNode }) {
  return <Text style={{ ...theme.typography.bodySmall, color: theme.colors.text, fontWeight: '600', marginBottom: theme.spacing.xs }}>{children}</Text>;
}

function SelectInput({ value, onChange, options }: { value: string; onChange: (v: string) => void; options: Array<{value: string; label: string}> }) {
  return (
    <TouchableOpacity style={inputStyle} onPress={() => {
      Alert.alert(
        'Select',
        '',
        options.map(opt => ({
          text: opt.label,
          onPress: () => onChange(opt.value),
        }))
      );
    }}>
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text style={{ ...theme.typography.body, color: value ? theme.colors.text : theme.colors.textMuted }}>{value ? options.find(o => o.value === value)?.label || value : 'Select'}</Text>
        <Ionicons name="chevron-down" size={20} color={theme.colors.textMuted} />
      </View>
    </TouchableOpacity>
  );
}

function DisclaimerText() {
  return (
    <View style={{ marginTop: theme.spacing.xl, padding: theme.spacing.md, backgroundColor: theme.colors.infoLight, borderRadius: theme.borderRadius.md }}>
      <Text style={{ ...theme.typography.caption, color: theme.colors.info, textAlign: 'center' }}>
        This AI assessment is for informational purposes only and does not replace professional medical advice. In emergency, call 112/108.
      </Text>
    </View>
  );
}

const inputStyle = {
  padding: theme.spacing.md,
  borderRadius: theme.borderRadius.md,
  backgroundColor: theme.colors.surface,
  borderWidth: 1,
  borderColor: theme.colors.border,
  ...theme.typography.body,
  color: theme.colors.text,
};

const primaryButtonStyle = {
  padding: theme.spacing.md,
  borderRadius: theme.borderRadius.full,
  backgroundColor: theme.colors.primary,
  alignItems: 'center',
  ...theme.shadows.sm,
};

const secondaryButtonStyle = {
  padding: theme.spacing.md,
  borderRadius: theme.borderRadius.full,
  backgroundColor: theme.colors.surface,
  borderWidth: 2,
  borderColor: theme.colors.primary,
  alignItems: 'center',
};