# SwasthyaAI Intake Service
# Language detection, field extraction, follow-up question selection
# Returns editable summary for user confirmation

import re
import uuid
from typing import Optional
from app.schemas import (
    IntakeRequest, IntakeResponse, ExtractedFields, FollowUpQuestion,
    EditableSummary, Language
)

# ===== Language Detection =====
DEVANAGARI_PATTERN = re.compile(r'[ऀ-ॿ]')
HINGLISH_INDICATORS = [
    'hai', 'hoon', 'hain', 'tha', 'thi', 'the', 'raha', 'rahi', 'rahe',
    'kya', 'kaise', 'kahan', 'kab', 'kyun', 'kyunki', 'lekin', 'par',
    'aur', 'ya', 'toh', 'to', 'bhi', 'nahi', 'nahin', 'nahiin',
    'mujhe', 'mujhko', 'mere', 'meri', 'mera', 'tumhe', 'tumko',
    'uske', 'unki', 'unka', 'hamare', 'hamari', 'hamara',
    'din', 'dinse', 'ghante', 'minute', 'maheene', 'sal',
    'bukhar', 'khansi', 'dard', 'pet', 'sir', 'paet', 'kam', 'kamar',
    'ult', 'ulti', 'chakkar', 'behosh', 'behosh', 'khun', 'khoon',
    'saans', 'lene', 'mein', 'dikkat', 'ful', 'nahi', 'aa', 'rahi',
    'ghut', 'raha', 'ghutna',
]

def detect_language(text: str) -> Language:
    """
    Detect language from text.
    Returns: en, hi, or hinglish
    """
    if not text:
        return Language.EN

    # Check for Devanagari script (Hindi)
    if DEVANAGARI_PATTERN.search(text):
        return Language.HI

    # Check for Hinglish indicators (romanized Hindi words)
    text_lower = text.lower()
    words = text_lower.split()
    hinglish_count = sum(1 for w in words if w in HINGLISH_INDICATORS)

    if hinglish_count >= 2 or (hinglish_count >= 1 and len(words) < 10):
        return Language.HINGLISH

    # Default to English
    return Language.EN


# ===== Field Extraction =====
# Patterns for extracting structured fields from free text

WHO_PATTERNS = {
    'self': [r'\b(i|me|myself|main|mujhe|mujhko|meri|mera|mere)\b'],
    'mother': [r'\b(mother|mom|mummy|maa|ma|ammi|motherji)\b'],
    'father': [r'\b(father|dad|daddy|papa|pita|abbu|fatherji)\b'],
    'child': [r'\b(child|baby|infant|son|daughter|baccha|bacchi|bete|beti|bacche)\b'],
    'elderly': [r'\b(elderly|senior|old\s+person|budhe|buzurg|dadi|nani|nana|dada)\b'],
    'spouse': [r'\b(wife|husband|spouse|partner|biwi|shohar|patni|pati)\b'],
    'other': [r'\b(patient|person|someone|anyone|kisi|koi)\b'],
}

SYMPTOM_KEYWORDS = {
    'fever': ['fever', 'bukhar', 'temperature', 'tap', 'jor', 'bukhaar', 'बुखार', 'बुखार', 'ज्वर', 'ताप'],
    'cough': ['cough', 'khansi', 'coughing', 'khaansi', 'खांसी', 'कफ'],
    'headache': ['headache', 'head ache', 'sir dard', 'sar dard', 'migraine', 'migren', 'सिर दर्द', 'सर दर्द', 'शिरोवेदना'],
    'stomach_pain': ['stomach pain', 'stomach ache', 'abdominal pain', 'pet dard', 'pet me dard', 'petdard', 'पेट दर्द', 'पेट में दर्द', 'उदरशूल'],
    'chest_pain': ['chest pain', 'chest ache', 'chest tightness', 'chest pressure', 'seene me dard', 'chati me dard', 'dil ka dard', 'छाती में दर्द', 'सीने में दर्द', 'चेस्ट पेन', 'वक्षदर्द'],
    'difficulty_breathing': ['difficulty breathing', 'shortness of breath', 'breathless', 'saans lene mein dikkat', 'saans fulna', 'dam ghutna', 'साँस लेने में दिक्कत', 'सांस फूलना', 'दम घुटना', 'श्वास कष्ट'],
    'nausea': ['nausea', 'nauseous', 'ult', 'ulti', 'vomiting', 'vomitting', 'ulti hona', 'उल्टी', 'उलटी', 'मतली', 'वमन'],
    'dizziness': ['dizziness', 'dizzy', 'chakkar', 'chakkar aana', 'vertigo', 'चक्कर', 'चक्कर आना', 'भ्रम'],
    'weakness': ['weakness', 'weak', 'kamzori', 'thakawat', 'fatigue', 'tired', 'कमजोरी', 'थकावट', 'थकान'],
    'pain': ['pain', 'ache', 'dard', 'dard hona', 'दर्द', 'पीड़ा'],
    'bleeding': ['bleeding', 'blood', 'khun', 'khoon', 'rakt', 'खून', 'रक्त', 'रक्तस्राव'],
    'unconscious': ['unconscious', 'unresponsive', 'fainted', 'behosh', 'behosh ho gaya', 'बेहोश', 'बेहोशी', 'मूर्छा'],
    'diarrhea': ['diarrhea', 'loose motion', 'loose motions', 'dast', 'dast lagna', 'दस्त', 'दस्त लगना', 'अतिसार'],
    'constipation': ['constipation', 'kabz', 'kabaz', 'कब्ज', 'कब्ज़'],
    'rash': ['rash', 'skin rash', 'chakatte', 'daane', 'चकत्ते', 'दाने', 'त्वचा पर चकत्ते'],
    'swelling': ['swelling', 'swollen', 'sujan', 'sujan aana', 'सूजन', 'सूजन आना', 'शोथ'],
    'numbness': ['numbness', 'numb', 'sunn', 'sunn ho jana', 'सुन्न', 'सुन्न हो जाना', 'सुन्नता'],
    'palpitations': ['palpitations', 'heart racing', 'dil dhadakna', 'tezi se dhadkan', 'दिल धड़कना', 'तेजी से धड़कन', 'हृदय स्पंदन'],
}

# Hindi/English number words mapping
HINDI_NUMBERS = {
    'ek': 1, 'do': 2, 'teen': 3, 'char': 4, 'paanch': 5, 'panch': 5,
    'chhah': 6, 'chha': 6, 'saat': 7, 'aath': 8, 'nau': 9, 'das': 10,
    'gyarah': 11, 'barah': 12, 'terah': 13, 'chaudah': 14, 'pandrah': 15,
    'solah': 16, 'satrah': 17, 'atharah': 18, 'unnis': 19, 'bees': 20,
}

def _normalize_number(text: str) -> Optional[str]:
    """Convert Hindi number words to digits."""
    text_lower = text.lower().strip()
    # Check for digit first
    if text_lower.isdigit():
        return text_lower
    # Check for Hindi number words
    for hindi, num in HINDI_NUMBERS.items():
        if text_lower == hindi or text_lower.startswith(hindi + ' '):
            return str(num)
    return None

DURATION_PATTERNS = [
    # English/Hinglish numbers
    (r'(\d+)\s*(day|days|din|dinse)', lambda m: f"{m.group(1)} days"),
    (r'(\d+)\s*(hour|hours|hr|hrs|ghante|ghanta)', lambda m: f"{m.group(1)} hours"),
    (r'(\d+)\s*(minute|minutes|min|mins)', lambda m: f"{m.group(1)} minutes"),
    (r'(\d+)\s*(week|weeks|hafte|hafta)', lambda m: f"{m.group(1)} weeks"),
    (r'(\d+)\s*(month|months|maheene|mahina)', lambda m: f"{m.group(1)} months"),
    # Hindi number words
    (r'(ek|do|teen|char|paanch|panch|chhah|chha|saat|aath|nau|das|gyarah|barah|terah|chaudah|pandrah|solah|satrah|atharah|unnis|bees)\s*(day|days|din|dinse)', lambda m: f"{HINDI_NUMBERS.get(m.group(1), m.group(1))} days"),
    (r'(ek|do|teen|char|paanch|panch|chhah|chha|saat|aath|nau|das|gyarah|barah|terah|chaudah|pandrah|solah|satrah|atharah|unnis|bees)\s*(hour|hours|hr|hrs|ghante|ghanta)', lambda m: f"{HINDI_NUMBERS.get(m.group(1), m.group(1))} hours"),
    (r'(ek|do|teen|char|paanch|panch|chhah|chha|saat|aath|nau|das|gyarah|barah|terah|chaudah|pandrah|solah|satrah|atharah|unnis|bees)\s*(minute|minutes|min|mins)', lambda m: f"{HINDI_NUMBERS.get(m.group(1), m.group(1))} minutes"),
    (r'(ek|do|teen|char|paanch|panch|chhah|chha|saat|aath|nau|das|gyarah|barah|terah|chaudah|pandrah|solah|satrah|atharah|unnis|bees)\s*(week|weeks|hafte|hafta)', lambda m: f"{HINDI_NUMBERS.get(m.group(1), m.group(1))} weeks"),
    # Relative time
    (r'(since|from)\s+(yesterday|kal|kal\s+se)', lambda m: "1 day"),
    (r'(since|from)\s+(today|aaj|aaj\s+se)', lambda m: "today"),
    (r'(since|from)\s+(last\s+night|raat\s+se)', lambda m: "since last night"),
    (r'\b(last\s+night)\b', lambda m: "since last night"),
    (r'\b(kal\s+se)\b', lambda m: "1 day"),
    (r'\b(parso|parso\s+se)\b', lambda m: "2 days"),
    # Vague
    (r'(a\s+few\s+days|few\s+days| kuch\s+din| kuch\s+din\s+se)', lambda m: "a few days"),
    (r'(a\s+few\s+hours|few\s+hours| kuch\s+ghante)', lambda m: "a few hours"),
    (r'(sudden|suddenly|achanak|achanak\s+se)', lambda m: "sudden onset"),
]

AGE_GROUP_PATTERNS = [
    # Order matters: more specific first
    ('infant', [
        r'\b(infant|newborn|baby|bacha|bachi|shishu|bachche)\b',
        r'\b(0|1|2)\s*(month|months|mahine|maheene)\b',
    ]),
    ('child', [
        r'\b(child|kid|baccha|bachi|bete|beti|bachche)\b',
        r'\b(3|4|5|6|7|8|9|10|11|12)\s*(year|years|sal)\b',
    ]),
    ('adolescent', [
        r'\b(teen|teenager|adolescent|kishor|kishori)\b',
        r'\b(13|14|15|16|17|18)\s*(year|years|sal)\b',
    ]),
    ('adult', [
        r'\b(adult|person|vyakti|admi|aurat|man|woman)\b',
        r'\b(19|2[0-9]|3[0-9]|4[0-9]|5[0-9]|6[0-4])\s*(year|years|sal)\b',
    ]),
    ('elderly', [
        r'\b(elderly|senior|old|budhe|buzurg|senior\s+citizen)\b',
        r'\b(6[5-9]|[7-9][0-9]|100)\s*(year|years|sal)\b',
    ]),
]


def extract_who(text: str) -> Optional[str]:
    """Extract who the patient is from text."""
    text_lower = text.lower()
    for who, patterns in WHO_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return who
    return None


def extract_symptoms(text: str) -> list[str]:
    """Extract symptoms from text."""
    text_lower = text.lower()
    found = []
    for symptom, keywords in SYMPTOM_KEYWORDS.items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                found.append(symptom)
                break
    return found


def extract_duration(text: str) -> Optional[str]:
    """Extract duration from text."""
    text_lower = text.lower()
    for pattern, formatter in DURATION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return formatter(match)
    return None


def extract_age_group(text: str) -> Optional[str]:
    """Extract age group from text."""
    text_lower = text.lower()
    for age_group, patterns in AGE_GROUP_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return age_group
    return None


def extract_fields(text: str, language: Language) -> ExtractedFields:
    """Extract all structured fields from free text."""
    return ExtractedFields(
        who=extract_who(text),
        symptoms=extract_symptoms(text),
        duration=extract_duration(text),
        age_group=extract_age_group(text),
        language=language,
    )


# ===== Follow-up Question Selection =====
FOLLOW_UP_QUESTIONS = {
    'who': [
        FollowUpQuestion(
            id="fu_who",
            question="Who is experiencing these symptoms?",
            field="who",
            required=True,
        ),
    ],
    'symptoms': [
        FollowUpQuestion(
            id="fu_symptoms",
            question="What are the main symptoms? (e.g., fever, cough, pain, nausea)",
            field="symptoms",
            required=True,
        ),
    ],
    'duration': [
        FollowUpQuestion(
            id="fu_duration",
            question="How long have these symptoms been present? (e.g., 2 days, 3 hours, 1 week)",
            field="duration",
            required=True,
        ),
    ],
    'age_group': [
        FollowUpQuestion(
            id="fu_age",
            question="What is the age group? (infant, child, adult, elderly) or exact age if known",
            field="age_group",
            required=True,
        ),
    ],
}

REQUIRED_FIELDS = ['who', 'symptoms', 'duration', 'age_group']


def select_follow_ups(extracted: ExtractedFields) -> list[FollowUpQuestion]:
    """Select 2-4 targeted follow-up questions for missing required fields."""
    missing = []
    for field in REQUIRED_FIELDS:
        value = getattr(extracted, field)
        if not value or (isinstance(value, list) and len(value) == 0):
            missing.append(field)

    # Select up to 4 follow-ups for missing fields
    follow_ups = []
    for field in missing[:4]:
        if field in FOLLOW_UP_QUESTIONS:
            follow_ups.extend(FOLLOW_UP_QUESTIONS[field])

    return follow_ups


def build_editable_summary(extracted: ExtractedFields, original_text: str) -> EditableSummary:
    """Build editable summary for user confirmation."""
    return EditableSummary(
        who=extracted.who or "",
        symptoms=extracted.symptoms,
        duration=extracted.duration or "",
        age_group=extracted.age_group or "",
        language=extracted.language,
        original_text=original_text,
    )


def process_intake(request: IntakeRequest) -> IntakeResponse:
    """
    Main intake processing function.
    Detects language, extracts fields, selects follow-ups, builds editable summary.
    """
    session_id = request.session_id or str(uuid.uuid4())[:8]
    language = request.language_hint or detect_language(request.text)

    extracted = extract_fields(request.text, language)
    follow_ups = select_follow_ups(extracted)
    editable_summary = build_editable_summary(extracted, request.text)

    # Complete if no missing required fields
    is_complete = len(follow_ups) == 0

    return IntakeResponse(
        session_id=session_id,
        extracted=extracted,
        follow_up_questions=follow_ups,
        editable_summary=editable_summary,
        language=language,
        is_complete=is_complete,
    )


def process_follow_up(session_id: str, answers: dict[str, str], previous: ExtractedFields) -> IntakeResponse:
    """
    Process follow-up answers and update extracted fields.
    Returns updated IntakeResponse with new follow-ups if needed.
    """
    # Merge answers into extracted fields
    updated_fields = {}
    for field, value in answers.items():
        if field == 'who' and value:
            updated_fields['who'] = value
        elif field == 'symptoms' and value:
            updated_fields['symptoms'] = [s.strip() for s in value.split(',') if s.strip()]
        elif field == 'duration' and value:
            updated_fields['duration'] = value
        elif field == 'age_group' and value:
            updated_fields['age_group'] = value

    # Create updated extracted fields
    extracted = ExtractedFields(
        who=updated_fields.get('who', previous.who),
        symptoms=updated_fields.get('symptoms', previous.symptoms),
        duration=updated_fields.get('duration', previous.duration),
        age_group=updated_fields.get('age_group', previous.age_group),
        language=previous.language,
    )

    follow_ups = select_follow_ups(extracted)
    editable_summary = build_editable_summary(extracted, "")  # original text not needed
    is_complete = len(follow_ups) == 0

    return IntakeResponse(
        session_id=session_id,
        extracted=extracted,
        follow_up_questions=follow_ups,
        editable_summary=editable_summary,
        language=previous.language,
        is_complete=is_complete,
    )