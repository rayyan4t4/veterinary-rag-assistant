import re
from apps.api.app.schemas import TriageResult

EMERGENCY_PATTERNS = {
    "severe breathing difficulty": [r"can't breathe", r"cannot breathe", r"gasping", r"blue (gums|tongue)", r"cyanosis", r"سانس نہیں"],
    "collapse or unconsciousness": [r"collapsed", r"unconscious", r"not responding", r"بے ہوش"],
    "uncontrolled bleeding": [r"won't stop bleeding", r"uncontrolled bleeding", r"خون نہیں رک"],
    "seizure": [r"seizure", r"convuls", r"fits? lasting", r"دور[ہ|ے]"],
    "suspected poisoning": [r"poison", r"toxin", r"antifreeze", r"rat bait", r"زہر"],
    "inability to urinate": [r"cannot urinate", r"can't pee", r"straining.*no urine", r"پیشاب نہیں"],
    "abdominal distension or bloat": [r"bloated", r"swollen abdomen", r"distended belly", r"پیٹ پھول"],
    "heatstroke": [r"heatstroke", r"overheated", r"very hot.*panting", r"ہیٹ اسٹروک"],
    "severe allergic reaction": [r"face swelling.*breath", r"anaphyla", r"allergic.*collapse"],
}

URGENT_PATTERNS = {
    "persistent vomiting": [r"vomit(ing|ed)?.*(many|repeated|all day)", r"persistent vomiting"],
    "significant trauma": [r"hit by (a )?car", r"fell from", r"deep wound"],
    "prolonged labor": [r"labor.*hours", r"unable to give birth", r"stuck puppy", r"stuck kitten"],
}


def assess_triage(text: str, language: str = "en") -> TriageResult:
    normalized = text.casefold()
    red_flags = [name for name, patterns in EMERGENCY_PATTERNS.items() if any(re.search(p, normalized) for p in patterns)]
    if red_flags:
        action = "فوری طور پر قریبی ویٹرنری ایمرجنسی سے رابطہ کریں۔" if language == "ur" else "Seek immediate veterinary emergency care now. Call ahead if possible and transport the animal safely."
        return TriageResult(urgency="emergency", red_flags=red_flags, reason_summary="Potentially life-threatening signs were described.", recommended_action=action)
    urgent = [name for name, patterns in URGENT_PATTERNS.items() if any(re.search(p, normalized) for p in patterns)]
    if urgent:
        return TriageResult(urgency="urgent", red_flags=urgent, reason_summary="The description includes signs that warrant prompt assessment.", recommended_action="Contact a veterinarian today; seek emergency care if the animal worsens.")
    return TriageResult(urgency="monitor", red_flags=[], reason_summary="No explicit emergency phrase was detected; this does not rule out serious illness.", recommended_action="Monitor closely and contact a veterinarian if signs persist, worsen, or concern you.")
