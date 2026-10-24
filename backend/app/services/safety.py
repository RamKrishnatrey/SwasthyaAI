# SwasthyaAI SafetyShield
# Deterministic red-flag rules (bilingual EN/HI/Hinglish)
# Runs FIRST, bypasses matching if any red flag found
# Conservative: when in doubt, escalate

import re
from typing import Optional
from app.schemas import SafetyResult, SafetyFlag, SafetyFlagType, RedFlagSeverity


# ===== Red-Flag Rules =====
# Each rule: (pattern, flag_type, severity, instruction, rule_id)
# Patterns are case-insensitive, match word boundaries where appropriate

RED_FLAG_RULES = [
    # Chest pain / heart attack
    (
        r"\b(chest\s+pain|heart\s+attack|angina|cardiac\s+pain|chest\s+tightness|chest\s+pressure|छाती\s+में\s+दर्द|सीने\s+में\s+दर्द|चेस्ट\s+पेन|सीना\s+दर्द|दिल\s+का\s+दर्द|chest\s+pan|चेस्ट\s+दर्द)\b",
        SafetyFlagType.CHEST_PAIN,
        RedFlagSeverity.CRITICAL,
        "Call 112/108 immediately. Do not drive. Chew aspirin (300mg) if not allergic. Sit upright.",
        "sf001",
    ),
    # Difficulty breathing
    (
        r"\b(difficulty\s+breathing|shortness\s+of\s+breath|can't\s+breathe|cannot\s+breathe|breathless|gasping|wheezing\s+severely|साँस\s+लेने\s+में\s+दिक्कत|सांस\s+फूलना|दम\s+घुटना|साँस\s+नहीं\s+आ\s+रही|breathing\s+problem|saans\s+lene\s+mein\s+dikkat|saans\s+ful\s+rahi|saans\s+nahi\s+aa\s+rahi|saans\s+mein\s+dikkat|saans\s+na\s+aa\s+raha|dam\s+ghut\s+raha|dam\s+ghutna|दम\s+घुट\s+रहा)\b",
        SafetyFlagType.DIFFICULTY_BREATHING,
        RedFlagSeverity.CRITICAL,
        "Call 112/108 immediately. Sit upright. Loosen tight clothing. Do not lie flat.",
        "sf002",
    ),
    # Unconsciousness / altered consciousness
    (
        r"\b(unconscious|unresponsive|won't\s+wake|won't\s+wake\s+up|fainted|passed\s+out|blacked\s+out|बेहोश|होश\s+नहीं|उत्तर\s+नहीं\s+दे\s+रहा|unconsciousness|better\s+not\s+responding|behosh|behoshi|behos\s+hona|hosh\s+nahi|होश\s+नहीं\s+है)\b",
        SafetyFlagType.UNCONSCIOUSNESS,
        RedFlagSeverity.CRITICAL,
        "Call 112/108 immediately. Place in recovery position if breathing. Do not give anything by mouth.",
        "sf003",
    ),
    # Severe bleeding
    (
        r"\b(severe\s+bleeding|heavy\s+bleeding|bleeding\s+heavily|spurting\s+blood|blood\s+gushing|खून\s+बह\s+रहा|बहुत\s+खून|रक्तस्राव|bleeding\s+won't\s+stop|खून\s+नहीं\s+रुक\s+रहा|khun\s+bah\s+raha|khoon\s+bah\s+raha|bleeding\s+bahut|rakt\s+strav|bleeding\s+not\s+stopping)\b",
        SafetyFlagType.SEVERE_BLEEDING,
        RedFlagSeverity.CRITICAL,
        "Call 112/108 immediately. Apply firm direct pressure with clean cloth. Do not remove soaked cloth - add more on top.",
        "sf004",
    ),
    # Stroke signs (FAST)
    (
        r"\b(face\s+drooping|facial\s+droop|arm\s+weakness|speech\s+difficulty|slurred\s+speech|can't\s+speak|cannot\s+speak|sudden\s+numbness|sudden\s+weakness|one\s+side\s+weak|facial\s+asymmetry|मुँह\s+टेढ़ा|हाथ\s+कमजोर|बोलने\s+में\s+दिक्कत|आवाज\s+नहीं\s+निकल\s+रही|stroke|लकवा|पैरालिसिस|muh\s+tedha|munh\s+tedha|haath\s+kamzor|bolne\s+mein\s+dikkat|aawaz\s+nahi\s+nikal|lakwa|lakva)\b",
        SafetyFlagType.STROKE_SIGNS,
        RedFlagSeverity.CRITICAL,
        "Call 112/108 immediately. Note time symptoms started. Do not give food/water/medication.",
        "sf005",
    ),
    # Seizure
    (
        r"\b(seizure|convulsion|fitting|shaking\s+uncontrollably|झटका|दौरा|मिर्गी|fit|epilepsy|jhatka|daura|mirgi|fits)\b",
        SafetyFlagType.SEIZURE,
        RedFlagSeverity.HIGH,
        "Call 112/108 if seizure lasts >5 min, repeats, or person doesn't wake. Protect from injury. Do not restrain or put anything in mouth.",
        "sf006",
    ),
    # Suicidal thoughts
    (
        r"\b(suicidal|want\s+to\s+die|want\s+to\s+kill\s+myself|end\s+my\s+life|self\s+harm|suicide|आत्महत्या|खुदकुशी|मर\s+जाना\s+चाहता|जीने\s+का\s+मन\s+नहीं|suicide\s+thoughts|atmahatya|khudkushi|mar\s+jana\s+chahta|jine\s+ka\s+man\s+nahi)\b",
        SafetyFlagType.SUICIDAL_THOUGHTS,
        RedFlagSeverity.CRITICAL,
        "Call 112/108 or suicide helpline 9152987821 (iCall) / 1800-599-0019 (Vandrevala) immediately. Stay with the person. Remove means of harm.",
        "sf007",
    ),
    # Pregnancy emergencies
    (
        r"\b(pregnant\s+and\s+(bleeding|pain|cramping)|pregnancy\s+bleeding|vaginal\s+bleeding\s+pregnant|water\s+broke|contractions\s+before\s+37\s+weeks|preterm\s+labor|गर्भवती\s+और\s+खून|गर्भावस्था\s+में\s+रक्तस्राव|प्रसव\s+पीड़ा|पानी\s+निकल\s+गया|garbhwati\s+aur\s+khoon|garbhwati\s+aur\s+khoon|pregnancy\s+mein\s+bleeding|paani\s+nikal\s+gaya|paani\s+nikla)\b",
        SafetyFlagType.PREGNANCY_EMERGENCY,
        RedFlagSeverity.CRITICAL,
        "Call 112/108 immediately or go to nearest maternity hospital. Do not delay.",
        "sf008",
    ),
]


def check_red_flags(text: str) -> list[SafetyFlag]:
    """
    Check text against all red-flag rules.
    Returns list of matched SafetyFlag objects.
    """
    if not text:
        return []

    text_lower = text.lower()
    matched = []

    for pattern, flag_type, severity, instruction, rule_id in RED_FLAG_RULES:
        if re.search(pattern, text_lower, re.IGNORECASE):
            # Find the actual matched text for reference
            match = re.search(pattern, text_lower, re.IGNORECASE)
            matched_text = match.group(0) if match else ""
            matched.append(
                SafetyFlag(
                    type=flag_type,
                    severity=severity,
                    matched_text=matched_text,
                    rule_id=rule_id,
                )
            )

    return matched


def evaluate_safety(text: str) -> SafetyResult:
    """
    Main safety evaluation function.
    Returns SafetyResult with red_flag boolean, matched rules, and instructions.
    """
    flags = check_red_flags(text)

    if not flags:
        return SafetyResult(
            red_flag=False,
            matched_rules=[],
            instructions=None,
            bypass_matching=False,
        )

    # Conservative: highest severity determines instructions
    critical_flags = [f for f in flags if f.severity == RedFlagSeverity.CRITICAL]
    if critical_flags:
        # Use first critical flag's instruction (they all say call 112/108)
        instruction = critical_flags[0].rule_id  # We'll look up instruction
        # Find the instruction from rules
        for _, _, sev, instr, rid in RED_FLAG_RULES:
            if rid == critical_flags[0].rule_id:
                instruction = instr
                break
        return SafetyResult(
            red_flag=True,
            matched_rules=flags,
            instructions=instruction,
            bypass_matching=True,
        )

    # High severity but not critical
    high_flags = [f for f in flags if f.severity == RedFlagSeverity.HIGH]
    if high_flags:
        for _, _, sev, instr, rid in RED_FLAG_RULES:
            if rid == high_flags[0].rule_id:
                instruction = instr
                break
        return SafetyResult(
            red_flag=True,
            matched_rules=flags,
            instructions=instruction,
            bypass_matching=True,
        )

    # Should not reach here with current rules, but fallback
    return SafetyResult(
        red_flag=True,
        matched_rules=flags,
        instructions="Seek immediate medical attention.",
        bypass_matching=True,
    )


# ===== Helper for negation detection (to avoid false positives) =====
# This is a simple check - in production you'd use NLP
NEGATION_PATTERNS = [
    r"\b(no|not|without|absence\s+of|denies|denied|ruled\s+out|don't|doesn't|didn't|haven't|hasn't|hadn't)\b",
    r"\b(नहीं|नहीं\s+है|नहीं\s+था|कोई\s+नहीं|इंकार|नहीं\s+होगा|नहीं\s+है|नहीं\s+था)\b",
    r"\b(nahi|nahin|nahiin|nahi\s+hai|nahin\s+hai|nahiin\s+hai|koi\s+nahi|koi\s+nahin|nahi\s+hoga)\b",
]


def has_negation_near(text: str, keyword: str, window: int = 50) -> bool:
    """
    Check if a negation word appears near a keyword (before OR after).
    For Hindi/Hinglish, negation often comes AFTER the keyword (e.g., "chest pain nahi hai").
    """
    if not text or not keyword:
        return False

    text_lower = text.lower()
    keyword_lower = keyword.lower()

    idx = text_lower.find(keyword_lower)
    if idx == -1:
        return False

    # Check before keyword
    start = max(0, idx - window)
    before_context = text_lower[start:idx]

    # Check after keyword (for Hindi/Hinglish where negation follows)
    end = min(len(text_lower), idx + len(keyword_lower) + window)
    after_context = text_lower[idx + len(keyword_lower):end]

    full_context = before_context + " " + after_context

    for pattern in NEGATION_PATTERNS:
        if re.search(pattern, full_context):
            return True

    return False


# Keep old function name for backwards compatibility
def has_negation_before(text: str, keyword: str, window: int = 50) -> bool:
    """Deprecated: use has_negation_near instead."""
    return has_negation_near(text, keyword, window)