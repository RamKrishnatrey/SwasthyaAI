# SwasthyaAI Triage Service
# Mock ML integration with predict(text, lang) contract
# Returns care_type, urgency, confidence, model_source

from typing import Optional
from app.schemas import (
    TriageRequest, TriageResponse, CareType, Urgency, ModelSource,
    EditableSummary, Language, SafetyResult, SafetyFlag, SafetyFlagType, RedFlagSeverity
)


# ===== Mock ML Model =====
# In production, this will be replaced by Member 1's trained model
# Contract: predict(text: str, lang: str) -> dict with keys:
#   care_type: CareType enum value
#   urgency: Urgency enum value
#   confidence: float 0-1
#   model_source: ModelSource enum value
#   suggested_specialty: Optional[str]
#   reasoning: str

MOCK_MODEL_VERSION = ModelSource.MOCK

# Keywords for rule-based mock triage
EMERGENCY_KEYWORDS = [
    'chest pain', 'heart attack', 'difficulty breathing', 'unconscious', 'stroke',
    'seizure', 'suicidal', 'severe bleeding', 'pregnancy emergency',
    'face drooping', 'arm weakness', 'slurred speech', 'cannot speak',
    'want to die', 'kill myself', 'end my life', 'self harm',
    'pregnant and bleeding', 'pregnancy bleeding', 'water broke',
    'छाती में दर्द', 'सांस नहीं', 'बेहोश', 'लकवा', 'दौरा', 'आत्महत्या',
    'खून बह रहा', 'गर्भवती', 'dam ghut', 'behosh', 'lakwa', 'atmahatya',
    'muh tedha', 'munh tedha', 'haath kamzor', 'bolne mein dikkat',
    'mar jana chahta', 'khudkushi', 'khudkushi karna',
    'garbhwati', 'paani nikal gaya'
]

URGENT_KEYWORDS = [
    'high fever', 'severe pain', 'vomiting blood', 'blood in stool',
    'sudden vision loss', 'allergic reaction', 'anaphylaxis',
    'तेज बुखार', 'तेज दर्द', 'खून की उल्टी', 'एलर्जी', 'एनाफिलैक्सिस',
    'high bukhar', 'tezi dard', 'khun ki ulti'
]

SPECIALIST_KEYWORDS = {
    'cardiology': ['chest pain', 'heart', 'palpitations', 'bp', 'blood pressure', 'हृदय', 'दिल', 'धड़कन'],
    'neurology': ['migraine', 'dizziness', 'numbness', 'memory', 'माइग्रेन', 'चक्कर', 'सुन्न'],
    'pulmonology': ['cough', 'breathing', 'asthma', 'wheezing', 'खांसी', 'सांस', 'अस्थमा'],
    'gastroenterology': ['stomach pain', 'abdominal', 'diarrhea', 'constipation', 'vomiting', 'पेट दर्द', 'दस्त', 'कब्ज', 'उल्टी'],
    'orthopedics': ['joint pain', 'back pain', 'fracture', 'sprain', 'arthritis', 'जोड़ों का दर्द', 'कमर दर्द', 'फ्रैक्चर'],
    'dermatology': ['rash', 'skin', 'itching', 'acne', 'चकत्ते', 'त्वचा', 'खुजली', 'मुंहासे'],
    'gynecology': ['periods', 'menstrual', 'pregnancy', 'vaginal', 'मासिक', 'गर्भावस्था', 'योनि'],
    'pediatrics': ['child', 'baby', 'infant', 'vaccination', 'बच्चा', 'शिशु', 'टीका'],
    'psychiatry': ['anxiety', 'depression', 'stress', 'insomnia', 'चिंता', 'अवसाद', 'तनाव', 'नींद नहीं'],
    'ent': ['ear pain', 'throat', 'sinus', 'hearing', 'कान दर्द', 'गला', 'साइनस', 'सुनाई नहीं'],
    'ophthalmology': ['eye', 'vision', 'blurred', 'eye pain', 'आंख', 'दृष्टि', 'धुंधला', 'आंख दर्द'],
    'urology': ['urine', 'kidney', 'burning urination', 'पेशाब', 'गुर्दा', 'जलन'],
}


def predict_mock(text: str, lang: str) -> dict:
    """
    Mock ML prediction function.
    In production, replace with actual model call.
    Returns dict with care_type, urgency, confidence, model_source, suggested_specialty, reasoning
    """
    text_lower = text.lower()

    # Check for emergency keywords first
    for kw in EMERGENCY_KEYWORDS:
        if kw in text_lower:
            return {
                "care_type": CareType.EMERGENCY,
                "urgency": Urgency.CRITICAL,
                "confidence": 0.95,
                "model_source": MOCK_MODEL_VERSION,
                "suggested_specialty": None,
                "reasoning": "Emergency symptoms detected requiring immediate medical attention. Call 112/108 immediately.",
            }

    # Check for urgent keywords
    for kw in URGENT_KEYWORDS:
        if kw in text_lower:
            return {
                "care_type": CareType.URGENT_CARE,
                "urgency": Urgency.HIGH,
                "confidence": 0.85,
                "model_source": MOCK_MODEL_VERSION,
                "suggested_specialty": None,
                "reasoning": "Urgent symptoms detected. Seek urgent care within 24 hours.",
            }

    # Check for specialist keywords
    matched_specialties = []
    for specialty, keywords in SPECIALIST_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                matched_specialties.append(specialty)
                break

    if matched_specialties:
        # Return first matched specialty with urgency based on symptom count
        care_type = CareType.PRIMARY_CARE  # Primary care referral to specialist
        urgency = Urgency.MODERATE if len(matched_specialties) > 1 else Urgency.LOW
        confidence = 0.75 + (0.1 * min(len(matched_specialties), 2))
        specialty = matched_specialties[0]
        return {
            "care_type": care_type,
            "urgency": urgency,
            "confidence": min(confidence, 0.95),
            "model_source": MOCK_MODEL_VERSION,
            "suggested_specialty": specialty,
            "reasoning": f"Symptoms suggest {specialty} specialist consultation. Key symptoms match {specialty} domain.",
        }

    # Default: self-care or primary care routine
    return {
        "care_type": CareType.SELF_CARE,
        "urgency": Urgency.LOW,
        "confidence": 0.70,
        "model_source": MOCK_MODEL_VERSION,
        "suggested_specialty": None,
        "reasoning": "Symptoms suggest self-care or routine primary care consultation. Monitor symptoms.",
    }


# Default safe safety result for triage (safety already checked before triage)
DEFAULT_SAFE_SAFETY = SafetyResult(
    red_flag=False,
    matched_rules=[],
    instructions=None,
    bypass_matching=False,
)


def triage_request(request: TriageRequest) -> TriageResponse:
    """
    Main triage processing function.
    Takes confirmed summary from intake, runs mock ML model, returns triage result.
    """
    # Combine text from confirmed summary
    combined_text = request.confirmed_summary.original_text
    if request.confirmed_summary.symptoms:
        combined_text += " " + " ".join(request.confirmed_summary.symptoms)

    # Run mock ML model
    prediction = predict_mock(combined_text, request.language.value)

    return TriageResponse(
        session_id=request.session_id,
        safety=DEFAULT_SAFE_SAFETY,
        care_type=prediction["care_type"],
        urgency=prediction["urgency"],
        reason=prediction["reasoning"],
        confidence=prediction["confidence"],
        model_source=prediction["model_source"],
    )


# Export for testing
__all__ = ["predict_mock", "triage_request", "EMERGENCY_KEYWORDS", "URGENT_KEYWORDS", "SPECIALIST_KEYWORDS", "DEFAULT_SAFE_SAFETY"]