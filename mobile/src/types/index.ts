// SwasthyaAI Mobile Types
// Shared TypeScript types for the mobile application

export type Language = 'en' | 'hi' | 'hinglish';

export interface User {
  id: string;
  email: string;
  phone?: string;
  full_name: string;
  role: 'patient' | 'clinician' | 'admin';
  status: 'active' | 'inactive' | 'suspended' | 'pending_verification';
  language: Language;
  email_verified: boolean;
  phone_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface PatientProfile {
  id: string;
  user_id: string;
  date_of_birth?: string;
  gender?: 'male' | 'female' | 'other';
  blood_group?: string;
  height_cm?: number;
  weight_kg?: number;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  latitude?: number;
  longitude?: number;
  allergies?: string;
  chronic_conditions?: string;
  current_medications?: string;
  family_history?: string;
  insurance_provider?: string;
  insurance_policy_number?: string;
  preferred_language: Language;
  notification_preferences?: string;
}

export interface ClinicianProfile {
  id: string;
  user_id: string;
  license_number: string;
  license_state?: string;
  specialization: string;
  qualifications?: string;
  experience_years?: number;
  clinic_name?: string;
  clinic_address?: string;
  clinic_city?: string;
  clinic_state?: string;
  clinic_pincode?: string;
  clinic_latitude?: number;
  clinic_longitude?: number;
  consultation_fee?: number;
  available_for_teleconsult: boolean;
  available_for_home_visit: boolean;
  verification_status: 'pending' | 'verified' | 'rejected';
  verification_documents?: string;
  rating: number;
  total_reviews: number;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface Conversation {
  id: string;
  patient_id: string;
  type: 'symptom_assessment' | 'general_chat' | 'follow_up' | 'emergency' | 'medical_report_analysis' | 'appointment_booking' | 'medication_reminder' | 'health_education';
  status: 'active' | 'completed' | 'archived' | 'escalated';
  language: Language;
  title?: string;
  summary?: string;
  metadata?: Record<string, any>;
  started_at: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  content_type: 'text' | 'audio' | 'image' | 'file';
  metadata?: Record<string, any>;
  tokens_used?: number;
  model_name?: string;
  model_version?: string;
  confidence?: number;
  processing_time_ms?: number;
  created_at: string;
}

export interface SymptomAssessment {
  id: string;
  conversation_id: string;
  patient_id: string;
  session_id: string;
  original_text: string;
  extracted_who?: string;
  extracted_symptoms?: string[];
  extracted_duration?: string;
  extracted_age_group?: string;
  detected_language: Language;
  follow_up_answers?: Record<string, any>;
  safety_red_flag: boolean;
  safety_flags?: any[];
  safety_instructions?: string;
  bypass_matching: boolean;
  care_type?: string;
  urgency?: string;
  triage_reason?: string;
  triage_confidence?: number;
  model_source: string;
  suggested_specialty?: string;
  matched_caregivers?: any[];
  selected_caregiver_id?: string;
  is_complete: boolean;
  created_at: string;
  updated_at: string;
}

export interface Appointment {
  id: string;
  patient_id: string;
  clinician_id: string;
  status: 'pending' | 'confirmed' | 'in_progress' | 'completed' | 'cancelled' | 'no_show' | 'rescheduled';
  type: 'in_person' | 'teleconsult' | 'home_visit' | 'emergency';
  scheduled_at: string;
  duration_minutes: number;
  timezone: string;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  latitude?: number;
  longitude?: number;
  meeting_link?: string;
  meeting_id?: string;
  meeting_password?: string;
  chief_complaint?: string;
  symptoms?: string[];
  patient_notes?: string;
  clinician_notes?: string;
  prescription?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  follow_up_notes?: string;
  cancelled_at?: string;
  cancelled_by?: string;
  cancellation_reason?: string;
  source: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface MedicalRecord {
  id: string;
  patient_id: string;
  appointment_id?: string;
  clinician_id?: string;
  type: 'prescription' | 'lab_report' | 'imaging' | 'discharge_summary' | 'vaccination' | 'allergy' | 'chronic_condition' | 'surgery' | 'consultation_note' | 'referral' | 'insurance_claim' | 'other';
  title: string;
  description?: string;
  file_path?: string;
  file_name?: string;
  file_size?: number;
  file_type?: string;
  file_hash?: string;
  structured_data?: Record<string, any>;
  extracted_text?: string;
  ai_analysis?: string;
  ai_model?: string;
  ai_confidence?: number;
  ai_processed_at?: string;
  record_date: string;
  valid_from?: string;
  valid_until?: string;
  tags?: string[];
  body_system?: string;
  icd_codes?: string[];
  is_sensitive: boolean;
  share_with_clinicians: boolean;
  share_with_family: boolean;
  created_at: string;
  updated_at: string;
}

export interface Reminder {
  id: string;
  patient_id: string;
  appointment_id?: string;
  medical_record_id?: string;
  type: 'medication' | 'appointment' | 'follow_up' | 'vaccination' | 'checkup' | 'lab_test' | 'prescription_refill' | 'health_goal' | 'custom';
  title: string;
  description?: string;
  frequency: 'once' | 'daily' | 'weekly' | 'monthly' | 'custom';
  scheduled_at: string;
  end_date?: string;
  timezone: string;
  days_of_week?: number[];
  day_of_month?: number;
  time_of_day?: string;
  medication_name?: string;
  dosage?: string;
  instructions?: string;
  is_active: boolean;
  is_completed: boolean;
  completed_at?: string;
  snoozed_until?: string;
  skipped_count: number;
  notify_via_push: boolean;
  notify_via_sms: boolean;
  notify_via_email: boolean;
  last_notified_at?: string;
  next_notification_at?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Caregiver {
  id: string;
  name: string;
  qualification_verified: boolean;
  skills: string[];
  service_areas: string[];
  languages: Language[];
  rating: number;
  availability: Array<{
    day_of_week: number;
    start_hour: number;
    end_hour: number;
    is_24h?: boolean;
    emergency_available?: boolean;
  }>;
  lat: number;
  lng: number;
}

export interface MatchResult {
  caregiver: Caregiver;
  score: {
    skill_fit: number;
    distance: number;
    availability: number;
    language: number;
    rating: number;
    total: number;
  };
  explanation: {
    caregiver_id: string;
    caregiver_name: string;
    score: any;
    why: string;
    passed_filters: boolean;
  };
}

export interface TriageResult {
  session_id: string;
  safety: {
    red_flag: boolean;
    matched_rules: any[];
    instructions?: string;
    bypass_matching: boolean;
  };
  care_type?: string;
  urgency?: string;
  reason?: string;
  confidence?: number;
  model_source: string;
  disclaimer: string;
}

export interface TinyFishSearchResult {
  query: string;
  results: Array<{
    title: string;
    url: string;
    snippet: string;
    source: string;
    published_date?: string;
  }>;
  total_results: number;
  search_time_ms: number;
}

export interface TinyFishResearchResult {
  topic: string;
  summary: string;
  sources: Array<{
    title: string;
    url: string;
    relevance: number;
  }>;
  key_findings: string[];
  confidence: number;
}

export interface ApiError {
  message: string;
  status_code: number;
  details?: Record<string, any>;
}

// Navigation Types
export type RootStackParamList = {
  '(auth)': undefined;
  '(tabs)': undefined;
  'onboarding': undefined;
  'login': undefined;
  'register': undefined;
  'forgot-password': undefined;
  'symptom-checker': undefined;
  'symptom-results': { assessmentId?: string };
  'chat': { conversationId?: string };
  'appointments': undefined;
  'appointment-detail': { appointmentId: string };
  'book-appointment': { clinicianId?: string };
  'medical-records': undefined;
  'medical-record-detail': { recordId: string };
  'reminders': undefined;
  'reminder-detail': { reminderId: string };
  'profile': undefined;
  'settings': undefined;
  'language': undefined;
  'doctors': undefined;
  'doctor-detail': { doctorId: string };
  'emergency': undefined;
  'health-insights': undefined;
};

export type TabParamList = {
  'dashboard': undefined;
  'symptoms': undefined;
  'chat': undefined;
  'appointments': undefined;
  'profile': undefined;
};

// Theme Types
export interface ThemeColors {
  primary: string;
  primaryLight: string;
  primaryDark: string;
  secondary: string;
  secondaryLight: string;
  accent: string;
  accentLight: string;
  background: string;
  surface: string;
  surfaceVariant: string;
  card: string;
  border: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  success: string;
  warning: string;
  error: string;
  info: string;
  emergency: string;
}

export interface ThemeSpacing {
  xs: number;
  sm: number;
  md: number;
  lg: number;
  xl: number;
  xxl: number;
}

export interface ThemeTypography {
  h1: { fontSize: number; fontWeight: string; lineHeight: number };
  h2: { fontSize: number; fontWeight: string; lineHeight: number };
  h3: { fontSize: number; fontWeight: string; lineHeight: number };
  h4: { fontSize: number; fontWeight: string; lineHeight: number };
  body: { fontSize: number; fontWeight: string; lineHeight: number };
  bodySmall: { fontSize: number; fontWeight: string; lineHeight: number };
  caption: { fontSize: number; fontWeight: string; lineHeight: number };
  button: { fontSize: number; fontWeight: string; lineHeight: number };
}

export interface Theme {
  colors: ThemeColors;
  spacing: ThemeSpacing;
  typography: ThemeTypography;
  borderRadius: {
    sm: number;
    md: number;
    lg: number;
    xl: number;
    full: number;
  };
  shadows: {
    sm: any;
    md: any;
    lg: any;
    xl: any;
  };
}