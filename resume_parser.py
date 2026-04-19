"""
resume_parser.py — Extracts structured info from raw resume text.
"""
import re
from semantic_matcher import extract_keywords


def parse_resume(text: str) -> dict:
    return {
        "name":             _extract_name(text),
        "email":            _extract_email(text),
        "phone":            _extract_phone(text),
        "skills":           list(extract_keywords(text)),
        "education":        _extract_education(text),
        "experience_years": _extract_experience_years(text),
    }


def _extract_email(text):
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else None


def _extract_phone(text):
    m = re.search(r"(\+?\d[\d\s\-().]{8,}\d)", text)
    return m.group(0).strip() if m else None


def _extract_name(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines[:5]:
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() and w.isalpha() for w in words):
            return line
    return None


DEGREE_KEYWORDS = ["bachelor","b.sc","b.e","b.tech","b.s.","master","m.sc","m.e","m.tech","m.s.","phd","ph.d","mba","diploma"]

def _extract_education(text):
    found = []
    for line in text.split("\n"):
        if any(kw in line.lower() for kw in DEGREE_KEYWORDS):
            c = line.strip()
            if c and len(c) < 200:
                found.append(c)
    return found[:5]


def _extract_experience_years(text):
    patterns = [
        r"(\d+\.?\d*)\+?\s*years?\s+(?:of\s+)?experience",
        r"experience\s+of\s+(\d+\.?\d*)\+?\s*years?",
        r"(\d+\.?\d*)\+?\s*yrs?\s+(?:of\s+)?experience",
    ]
    numbers = []
    for p in patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            try: numbers.append(float(m.group(1)))
            except: pass
    return max(numbers) if numbers else None
