import re

INJECTION_MARKERS = [
    r"ignore (all |the )?(previous|prior|system) instructions",
    r"you are now",
    r"system message",
    r"developer message",
    r"reveal (the )?(prompt|secret|token)",
    r"follow these instructions",
]

def flag_untrusted_instructions(text: str) -> list[str]:
    """Flags—not executes—likely instructions embedded in evidence."""
    value=text.casefold()
    return [pattern for pattern in INJECTION_MARKERS if re.search(pattern,value)]
