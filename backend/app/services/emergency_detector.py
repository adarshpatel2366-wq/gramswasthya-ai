"""
Rule-based first pass for emergency detection, run BEFORE the AI reply is generated
so we can show instant emergency guidance without waiting on a model round-trip.
This is deliberately keyword-based (fast, deterministic, offline) and is
supplemented by the AI's own judgement in the system prompt for subtler cases.
"""

EMERGENCY_PATTERNS = {
    "chest_pain": ["chest pain", "seene me dard", "seene mein dard", "chest me dard"],
    "breathing": ["can't breathe", "cannot breathe", "difficulty breathing", "saans nahi",
                  "saans lene me takleef", "breathless"],
    "stroke": ["face drooping", "slurred speech", "one side weakness", "stroke",
               "muh tedha", "ek taraf kamzori"],
    "bleeding": ["heavy bleeding", "bleeding a lot", "bahut khoon", "khoon nahi ruk raha",
                 "excessive bleeding"],
    "poisoning": ["poisoning", "swallowed poison", "zeher", "poison khaya"],
    "snake_bite": ["snake bite", "saanp ne kata", "snakebite"],
    "burns": ["severe burn", "badly burnt", "jal gaya", "severe burns"],
    "pregnancy": ["pregnancy emergency", "labor pain", "pregnant bleeding",
                  "garbhavastha me khoon", "prasav"],
    "infant": ["baby not breathing", "infant unconscious", "newborn emergency",
               "baby is blue", "bachcha saans nahi le raha"],
    "unconscious": ["unconscious", "not responding", "behosh", "faint and not waking"],
    "suicidal": ["suicidal", "want to die", "end my life", "khud ko marna",
                 "aatmahatya", "kill myself"],
}

EMERGENCY_ADVICE = {
    "chest_pain": "This may be a heart-related emergency. Call an ambulance (108) or go to "
                   "the nearest hospital immediately. Keep the person calm, seated, and loosen "
                   "tight clothing. Do not let them exert themselves.",
    "breathing": "Difficulty breathing can be life-threatening. Call 108 immediately. Keep the "
                 "person upright, ensure fresh air, and do not leave them alone.",
    "stroke": "Possible stroke. Note the time symptoms started and get to a hospital "
              "immediately — call 108. Do not give food or water.",
    "bleeding": "Apply firm, direct pressure on the wound with a clean cloth. Keep the "
                "injured area raised if possible. Call 108 or go to the nearest hospital now.",
    "poisoning": "Do not induce vomiting unless a doctor/poison control tells you to. Call 108 "
                 "and keep the packaging/substance to show medical staff.",
    "snake_bite": "Keep the person still and calm, keep the bitten limb below heart level, "
                  "remove tight items near the bite. Do NOT cut, suck, or apply ice. Get to a "
                  "hospital immediately — call 108.",
    "burns": "Cool the burn with clean running water for 10-20 minutes. Do not apply ice, "
             "toothpaste, or oil. Cover loosely with a clean cloth and go to a hospital.",
    "pregnancy": "This needs urgent medical attention. Call 108 and go to the nearest hospital "
                 "or PHC immediately. Keep the person lying on her left side if possible.",
    "infant": "This is a medical emergency. Call 108 immediately and get to the nearest "
              "hospital. If trained, begin infant CPR while waiting for help.",
    "unconscious": "Check breathing. If breathing, place in recovery position (on their side). "
                   "If not breathing, begin CPR if trained. Call 108 immediately.",
    "suicidal": "You matter, and help is available right now. Please call the KIRAN mental "
                "health helpline at 1800-599-0019 (toll-free, 24/7) or 108 for emergency "
                "support. If possible, stay with someone you trust and avoid being alone.",
}


def detect_emergency(text: str):
    """Returns (is_emergency: bool, category: str|None, advice: str|None)."""
    lowered = text.lower()
    for category, patterns in EMERGENCY_PATTERNS.items():
        for p in patterns:
            if p in lowered:
                return True, category, EMERGENCY_ADVICE[category]
    return False, None, None
