import re
from dataclasses import dataclass, asdict

@dataclass
class LabValue:
    test: str
    result: str
    unit: str | None
    reference_range: str | None
    flag: str | None
    raw_line: str

LINE=re.compile(r"^(?P<test>[A-Za-z][A-Za-z0-9 ()/%.-]{1,50}?)\s+(?P<result>[<>]?\d+(?:\.\d+)?)\s*(?P<unit>[A-Za-z%/^0-9µμ.-]+)?(?:\s+(?P<range>\d+(?:\.\d+)?\s*[-–]\s*\d+(?:\.\d+)?))?(?:\s+(?P<flag>H|L|HIGH|LOW))?$",re.I)

def parse_lab_text(text: str) -> list[dict]:
    """Conservative parser: missing units/ranges stay null and are never inferred."""
    values=[]
    for raw in text.splitlines():
        match=LINE.match(" ".join(raw.split()))
        if match:
            g=match.groupdict(); values.append(asdict(LabValue(g["test"],g["result"],g["unit"],g["range"],g["flag"].upper() if g["flag"] else None,raw.strip())))
    return values
