"""
resume_parser.py  –  Extracts structured info from raw resume text.
Uses regex for contact info and keyword matching for skills.
"""

import re
from matcher import extract_keywords


def parse_resume(text: str) -> dict:
    """
    Extract structured fields from raw resume text.
    Returns dict with: name, email, phone, skills, education, experience_years
    """
    return {
        "name":             _extract_name(text),
        "email":            _extract_email(text),
        "phone":            _extract_phone(text),
        "skills":           list(extract_keywords(text)),
        "education":        _extract_education(text),
        "experience_years": _extract_experience_years(text),
    }


# ─── Field Extractors ─────────────────────────────────────────────────────────

def _extract_email(text: str) -> str | None:
    pattern = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def _extract_phone(text: str) -> str | None:
    pattern = r"(\+?\d[\d\s\-().]{8,}\d)"
    match = re.search(pattern, text)
    return match.group(0).strip() if match else None


def _extract_name(text: str) -> str | None:
    """
    Heuristic: the candidate's name is usually on the first 1-2 lines.
    Try to grab the first line that looks like a proper name.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        # Name-like: 2-4 words, each capitalised, no digits
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() and w.isalpha() for w in words):
            return line
    return None


DEGREE_KEYWORDS = [
    "bachelor", "b.sc", "b.e", "b.tech", "b.s.", "master", "m.sc", "m.e",
    "m.tech", "m.s.", "phd", "ph.d", "mba", "diploma", "associate",
]

def _extract_education(text: str) -> list[str]:
    """Return lines that mention a degree."""
    found = []
    for line in text.split("\n"):
        line_low = line.lower()
        if any(kw in line_low for kw in DEGREE_KEYWORDS):
            cleaned = line.strip()
            if cleaned and len(cleaned) < 200:
                found.append(cleaned)
    return found[:5]


def _extract_experience_years(text: str) -> float | None:
    """
    Look for patterns like "5 years of experience", "3+ years", etc.
    Returns the highest number found or None.
    """
    patterns = [
        r"(\d+\.?\d*)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+\.?\d*)\+?\s*years?",
        r"(\d+\.?\d*)\+?\s*yrs?\s+(?:of\s+)?experience",
    ]
    numbers = []
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            try:
                numbers.append(float(m.group(1)))
            except ValueError:
                pass
    return max(numbers) if numbers else None
