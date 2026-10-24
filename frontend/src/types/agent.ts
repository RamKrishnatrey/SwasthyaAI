export type Language = 'en' | 'hi' | 'hinglish';
export type ViewId = 'overview' | 'care' | 'caregivers' | 'future' | 'privacy';
export type AgentStatus = 'needs_followup' | 'routed' | 'possible_emergency' | 'unavailable' | 'error';
export type Urgency = 'unknown' | 'routine' | 'same_day' | 'urgent' | 'emergency';

export interface SafetyState {
  flagged: boolean;
  level: 'unknown' | 'none' | 'possible_emergency';
  rule_id?: string;
  message?: string;
}

export interface Caregiver {
  id: string;
  name: string;
  role: string;
  skills: string[];
  distanceKm: number;
  languages: string[];
  rating: number;
  reviewCount: number;
  availability: string;
  verified: boolean;
  slotSuitability: number;
  skillFit: number;
  languageFit: number;
  ratingScore: number;
}

export interface TriageResult {
  care_type: string;
  urgency: Urgency;
  explanation: string;
  next_steps: string[];
  model_name?: string;
  model_version?: string;
  confidence?: number;
}

export interface FollowUpQuestion {
  id: string;
  text: string;
  options?: string[];
}

export interface AgentResponse {
  status: AgentStatus;
  response: string;
  follow_up_question?: FollowUpQuestion | null;
  safety: SafetyState;
  triage?: TriageResult | null;
  caregiver_matches?: Caregiver[];
  explanation?: string[];
  session_id?: string;
  source: 'api' | 'demo';
  error?: string | null;
}

export interface AgentRequest {
  session_id: string;
  message: string;
  language: Language;
  history?: Array<{ role: 'user' | 'assistant'; content: string }>;
}
