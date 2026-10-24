import type { AgentRequest, AgentResponse, Caregiver } from '../types/agent';

export const demoCaregivers: Caregiver[] = [
  {
    id: 'DEMO-C014', name: 'Meera S.', role: 'Home-care nurse', skills: ['Post-visit support', 'Vitals monitoring'],
    distanceKm: 3.2, languages: ['Hindi', 'English'], rating: 4.8, reviewCount: 34,
    availability: 'Today · 6:00 PM', verified: false, slotSuitability: 0.95, skillFit: 0.92, languageFit: 1, ratingScore: 0.96,
  },
  {
    id: 'DEMO-C021', name: 'Arjun K.', role: 'Care assistant', skills: ['Daily living support', 'Elder support'],
    distanceKm: 2.4, languages: ['Hindi', 'Hinglish'], rating: 4.6, reviewCount: 21,
    availability: 'Tomorrow · 10:30 AM', verified: false, slotSuitability: 0.78, skillFit: 0.80, languageFit: 0.9, ratingScore: 0.92,
  },
  {
    id: 'DEMO-C008', name: 'Nisha R.', role: 'Home-care nurse', skills: ['Medication schedule support', 'Post-visit support'],
    distanceKm: 6.1, languages: ['English', 'Hindi'], rating: 4.9, reviewCount: 12,
    availability: 'Today · 8:00 PM', verified: false, slotSuitability: 0.88, skillFit: 0.86, languageFit: 1, ratingScore: 0.98,
  },
];

const isPotentialEmergencyDemo = (message: string) => {
  const normalized = message.toLowerCase();
  const phrases = [
    'chest pain', 'severe chest', 'difficulty breathing', "can't breathe", 'cannot breathe',
    'not breathing', 'unconscious', 'stroke', 'face drooping', 'severe bleeding',
    'बेहोश', 'सांस नहीं', 'साँस नहीं', 'सीने में तेज दर्द', 'बहुत तेज सीने में दर्द',
    'saans nahi', 'behosh', 'seene mein dard',
  ];
  return phrases.some((phrase) => normalized.includes(phrase));
};

export async function createDemoResponse(request: AgentRequest, turnCount: number): Promise<AgentResponse> {
  await new Promise((resolve) => window.setTimeout(resolve, 450));
  const message = request.message.trim();

  if (isPotentialEmergencyDemo(message)) {
    return {
      status: 'possible_emergency',
      response: 'A possible emergency warning phrase was detected in this demo. Please contact local emergency services now if someone may be in immediate danger. Do not wait for this app or continue ordinary caregiver matching.',
      safety: {
        flagged: true,
        level: 'possible_emergency',
        rule_id: 'DEMO_KEYWORD_GUARD',
        message: 'Demonstration keyword rule only; not a clinically validated triage assessment.',
      },
      triage: null,
      caregiver_matches: [],
      explanation: ['Demo-only deterministic phrase check', 'Normal matching bypassed'],
      session_id: request.session_id,
      source: 'demo',
    };
  }

  if (turnCount === 0) {
    return {
      status: 'needs_followup',
      response: 'I have captured your message in the demo. Before showing a care-navigation example, let’s clarify one detail. This prototype cannot assess your health or confirm that an emergency is absent.',
      follow_up_question: {
        id: 'duration_or_change',
        text: 'When did this start, and is it getting worse?',
        options: ['Started today', '1–3 days ago', 'More than 3 days ago', 'Not sure'],
      },
      safety: { flagged: false, level: 'unknown', message: 'No emergency status can be inferred from this demo result.' },
      triage: null,
      caregiver_matches: [],
      explanation: ['A follow-up was requested because more context may be needed.'],
      session_id: request.session_id,
      source: 'demo',
    };
  }

  return {
    status: 'routed',
    response: 'Demo pathway generated. This is illustrative output, not a medical assessment. In the integrated system, the trained model and reviewed routing policy must supply this result.',
    safety: { flagged: false, level: 'unknown', message: 'The demo does not certify that the case is non-emergency.' },
    triage: {
      care_type: 'General care navigation',
      urgency: 'unknown',
      explanation: 'No clinical urgency has been determined by this demo adapter. Connect the reviewed agent and triage model for actual routing.',
      next_steps: ['Review your information with a qualified healthcare professional.', 'If you believe this is an emergency, contact local emergency services immediately.'],
      model_name: 'Demo adapter — no trained model connected',
    },
    caregiver_matches: demoCaregivers,
    explanation: ['Illustrative demo result', 'Caregiver profiles are synthetic', 'No provider credentials or live availability are verified'],
    session_id: request.session_id,
    source: 'demo',
  };
}
