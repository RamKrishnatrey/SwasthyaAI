import re


_PATTERNS = {
    "chest_pain": [r"chest pain", r"pain in (?:the )?chest", r"सीने में दर्द", r"chhati mein dard", r"chhati me dard"],
    "breathlessness": [r"not breathing", r"difficulty breathing", r"shortness of breath", r"can't breathe", r"cannot breathe", r"सांस नहीं आ रही", r"सांस लेने में दिक्कत", r"saans nahi aa rahi", r"saans lene mein dikkat", r"saans phool"],
    "unconsciousness": [r"unconscious", r"unresponsive", r"passed out", r"बेहोश", r"behosh", r"response nahi de rahe"],
    "severe_bleeding": [r"severe bleeding", r"bleeding (?:is )?not stopping", r"bleeding ruk nahi", r"खून नहीं रुक", r"बहुत खून बह"],
    "stroke_symptoms": [r"stroke", r"face droop", r"slurred speech", r"चेहरा टेढ़ा", r"बोलने में दिक्कत"],
    "seizure": [r"seizure", r"convulsion", r"दौरा", r"daura"],
    "high_fever_infant": [r"(?:newborn|infant|baby)\b.{0,30}\b(?:high fever|fever)", r"(?:high fever|fever).{0,30}\b(?:newborn|infant|baby)\b", r"शिशु.{0,30}बुखार"],
    "suicidal_ideation": [r"suicid(?:e|al)", r"kill myself", r"end my life", r"self[- ]harm", r"आत्महत्या", r"khudkushi"],
    "severe_dehydration": [r"severe dehydration", r"not urinating", r"बहुत कम पेशाब", r"peshab nahi ho raha"],
}
_NEGATION_BEFORE = re.compile(r"(?:\bno\b|\bnot having\b|\bdenies\b|\bwithout\b|नहीं|नही)\s*$", re.I)
_NEGATION_AFTER = re.compile(r"^\s*(?:is )?(?:absent|gone|resolved|नहीं है|नही है)", re.I)


def _negated(text: str, start: int, end: int) -> bool:
    before = text[max(0, start - 24):start]
    after = text[end:end + 24]
    return bool(_NEGATION_BEFORE.search(before) or _NEGATION_AFTER.search(after))


def detect_red_flags(text: str) -> list[str]:
    normalized = " ".join(text.casefold().split())
    flags = []
    for flag, patterns in _PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, normalized, re.I)
            if match and not _negated(normalized, match.start(), match.end()):
                flags.append(flag)
                break
    return flags


def detect_language(text: str, requested: str = "auto") -> str:
    if requested.casefold() != "auto":
        aliases = {"hindi": "Hindi", "english": "English", "hinglish": "Hinglish"}
        return aliases.get(requested.casefold(), requested)
    if re.search(r"[ऀ-ॿ]", text):
        return "Hindi"
    if re.search(r"\b(?:hai|ho|ko|chahiye|nahi|mujhe|mein|ka|ki|ke)\b", text, re.I):
        return "Hinglish"
    return "English"
