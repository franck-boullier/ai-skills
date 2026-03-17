#!/usr/bin/env python3
"""
ATS Resume Data Extractor

Extracts structured, machine-readable findings from a resume PDF and a job
description for use by the ats-score-simulator skill. Produces a raw findings
JSON covering keyword matches, section headings, contact info, date patterns,
and formatting signals — WITHOUT applying any scores.

Scoring is performed by the AI using the ats-score-simulator methodology
(see references/SCORING-METHODOLOGY.md). Two dimensions of that methodology
CANNOT be evaluated by this script and always require AI analysis:
  - Experience Tenure (27%)  — requires semantic reasoning about career history
  - Education & Qualifications (18%) — requires semantic reasoning about degrees
                                        and certifications vs. job requirements

Usage:
    pip install -r scripts/requirements.txt --break-system-packages -q
    python extract_resume_data.py --resume resume.pdf --jd job_description.txt --output findings.json
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Stopwords — common English words that carry no ATS keyword signal
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "shall", "can", "need", "dare", "ought", "used", "that", "this",
    "these", "those", "it", "its", "we", "you", "he", "she", "they", "them",
    "our", "your", "their", "my", "his", "her", "who", "which", "what",
    "when", "where", "why", "how", "all", "each", "every", "both", "few",
    "more", "most", "other", "some", "such", "no", "not", "only", "same",
    "so", "than", "too", "very", "just", "as", "if", "then", "also",
    "strong", "excellent", "good", "great", "well", "including",
    "experience", "work", "working", "role", "position", "responsibilities",
    "requirements", "qualifications", "preferred", "required", "ability",
    "skills", "knowledge", "understanding", "background", "year", "years",
    "minimum", "proven", "plus", "etc", "e.g", "i.e", "new", "key", "help",
    "ensure", "support", "manage", "maintain", "provide", "develop", "create",
    "build", "design", "implement", "use", "using", "within", "across",
    "multiple", "various", "related", "based", "high", "large", "complex",
    "effective", "efficient", "successful", "responsible", "s",
}

# Generic job-description filler words that carry no ATS signal
GENERIC_JD_WORDS = {
    "responsibilities", "requirements", "preferred", "qualifications", "required",
    "experience", "years", "strong", "proven", "excellent", "good", "great",
    "looking", "seeking", "join", "team", "role", "position", "company",
    "ability", "skills", "knowledge", "background", "minimum", "plus",
    "including", "ensure", "support", "manage", "maintain", "provide", "develop",
    "create", "build", "design", "implement", "work", "working", "help",
    "drive", "lead", "leading", "partner", "track", "record", "owner",
    "communicate", "collaboration", "communication", "culture", "values",
    "opportunity", "impact", "growth", "environment", "world", "level",
    "related", "field", "degree", "bachelor", "b.s", "b.a", "master",
    "similar", "equivalent", "relevant", "appropriate", "applicable",
    "demonstrated", "effective", "efficient", "successful", "independently",
    "proactively", "detail", "oriented", "fast", "paced", "dynamic",
    "startup", "mission", "vision", "passion", "passionate", "excited",
    "diverse", "inclusive", "equal", "opportunity", "employer",
    "nice", "have", "bonus", "point", "points", "etc", "e.g", "i.e",
    "overview", "about", "description", "title", "senior", "junior",
    "manage", "oversee", "own", "ownership", "drive", "execute", "execution",
    "strategy", "strategic", "tactical", "operational", "hands", "clean",
    "complex", "large", "scale", "high", "perform", "performance",
    "analyze", "analysis", "report", "reporting", "track", "monitor",
    "mentor", "coach", "hire", "recruit",
}

# Union of general and JD-specific stopwords for keyword filtering
ALL_STOPWORDS = STOPWORDS | GENERIC_JD_WORDS


# ---------------------------------------------------------------------------
# Standard ATS section headings and their common variants
# ---------------------------------------------------------------------------

STANDARD_HEADINGS = {
    "experience": [
        "experience", "work experience", "professional experience",
        "employment history", "work history", "career history",
        "relevant experience", "positions held",
    ],
    "education": [
        "education", "academic background", "educational background",
        "qualifications", "academic qualifications", "degrees",
    ],
    "skills": [
        "skills", "technical skills", "core competencies", "competencies",
        "key skills", "skill set", "areas of expertise", "expertise",
        "technologies", "tools & technologies", "tools and technologies",
    ],
    "summary": [
        "summary", "professional summary", "profile", "professional profile",
        "about me", "objective", "career objective", "career summary",
        "executive summary", "overview",
    ],
    "contact": [
        "contact", "contact information", "personal information",
        "personal details",
    ],
    "certifications": [
        "certifications", "certification", "licenses", "credentials",
        "professional certifications", "accreditations",
    ],
}


# ---------------------------------------------------------------------------
# Keyword technical-term patterns
# ---------------------------------------------------------------------------

TECHNICAL_PATTERNS = [
    r"^[A-Z][a-z]+(?:[A-Z][a-z]+)+$",      # CamelCase: TypeScript, PostgreSQL
    r"^[A-Z]{2,}(?:[a-z0-9]+)?$",          # ALL CAPS or mostly: SQL, AWS, API
    r"^[a-z]+(?:[A-Z][a-z0-9]+)+$",        # camelCase: dbt, iOS
    r".+[/\-\.].+",                          # Slash/dot/hyphen: CI/CD, Node.js
    r".*\d+.*",                              # Contains digits: Python3, EC2, S3
]
# Precompiled for reuse (avoids recompilation on every looks_technical call)
TECHNICAL_PATTERNS_COMPILED = [re.compile(p) for p in TECHNICAL_PATTERNS]


def looks_technical(word: str) -> bool:
    """Return True if a word looks like a technical term rather than generic English."""
    # Check word against each technical-term regex; first match wins
    for pattern in TECHNICAL_PATTERNS_COMPILED:
        if pattern.match(word):
            return True
    return False


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path: str) -> tuple[str, bool]:
    """
    Extract text from a PDF. Returns (text, is_extractable).
    Tries pdfplumber first (better layout preservation), then pypdf as fallback.
    """
    # Prefer pdfplumber for better layout preservation
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages).strip()
        if text:
            return text, True
    except ImportError:
        pass  # pdfplumber not installed; fall through to pypdf
    except Exception as e:
        print(f"Warning: pdfplumber extraction failed ({e}); trying pypdf.", file=sys.stderr)

    # Fallback to pypdf if pdfplumber fails or is unavailable
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n".join(pages).strip()
        if text:
            return text, True
    except ImportError:
        pass  # pypdf not installed
    except Exception as e:
        print(f"Warning: pypdf extraction failed ({e}).", file=sys.stderr)

    return "", False


# ---------------------------------------------------------------------------
# Keyword extraction and matching
# ---------------------------------------------------------------------------

# Precompiled: filter out pure numbers/short artefacts from keyword list
KEYWORD_FILTER_REGEX = re.compile(r"^[\d\s\-\.]+$")


def extract_jd_keywords(jd_text: str) -> list[str]:
    """
    Extract meaningful keywords from a job description using a 3-pass approach.

    Pass 1: Capitalized terms — proper nouns, tool names, technologies.
    Pass 2: Tech-pattern terms — slash/dot/hyphen compounds (CI/CD, Node.js).
    Pass 3: Meaningful 2-word lowercase phrases (data pipelines, machine learning).
    """
    keywords = set()

    # Pass 1: Capitalized single/multi-word terms (proper nouns, tools, technologies)
    cap_phrase_pattern = (
        r"\b([A-Z][a-zA-Z0-9]*(?:[\-/\.][a-zA-Z0-9]+)*"
        r"(?:\s+[A-Z][a-zA-Z0-9]*(?:[\-/\.][a-zA-Z0-9]+)*){0,2})\b"
    )
    for match in re.finditer(cap_phrase_pattern, jd_text):
        phrase = match.group(1).strip()
        phrase_lower = phrase.lower()
        words = phrase_lower.split()
        if len(phrase) < 2:
            continue
        if all(w in ALL_STOPWORDS for w in words):
            continue
        if len(words) == 1 and phrase_lower in ALL_STOPWORDS:
            continue
        keywords.add(phrase_lower)

    # Pass 2: Tech-pattern terms (slash/dot/hyphen compounds regardless of case)
    tech_pattern = r"\b([a-zA-Z][a-zA-Z0-9]*(?:[/\-\.][a-zA-Z0-9]+)+)\b"
    for match in re.finditer(tech_pattern, jd_text):
        term = match.group(1).strip().lower()
        if term not in ALL_STOPWORDS and len(term) > 1:
            keywords.add(term)

    # Pass 3: Meaningful 2-word lowercase phrases (e.g. "data pipelines")
    text_lower = jd_text.lower()
    cleaned = re.sub(r"[^\w\s\-/]", " ", text_lower)
    tokens = cleaned.split()
    for i in range(len(tokens) - 1):
        w1, w2 = tokens[i], tokens[i + 1]
        if (
            w1 not in ALL_STOPWORDS and w2 not in ALL_STOPWORDS
            and len(w1) > 2 and len(w2) > 2
        ):
            keywords.add(f"{w1} {w2}")

    # Drop pure numbers and very short artefacts before returning
    return [k for k in keywords if len(k) > 2 and not KEYWORD_FILTER_REGEX.match(k)]


def match_keywords(jd_text: str, resume_text: str) -> dict:
    """
    Match job description keywords against the resume text.

    Uses exact phrase match first; falls back to checking whether all
    significant words in a multi-word phrase appear individually (partial match).

    Returns matched and missing keyword lists with overall match rate.
    Does NOT produce a score — that is the AI's responsibility.
    """
    jd_keywords = list(set(extract_jd_keywords(jd_text)))
    resume_lower = resume_text.lower()

    matched = []
    missing = []

    # For each JD keyword: exact phrase match, or (for multi-word) all significant words present
    for kw in jd_keywords:
        found = False
        if " " in kw:
            if kw in resume_lower:
                found = True
            else:
                # Partial match: all non-stopword words of the phrase appear in resume
                sig_words = [
                    w for w in kw.split()
                    if w not in ALL_STOPWORDS and len(w) > 2
                ]
                if sig_words and all(
                    re.search(r"\b" + re.escape(w) + r"\b", resume_lower)
                    for w in sig_words
                ):
                    found = True
        else:
            if re.search(r"\b" + re.escape(kw) + r"\b", resume_lower):
                found = True

        (matched if found else missing).append(kw)

    total = max(len(jd_keywords), 1)
    match_rate = round(len(matched) / total * 100, 1)

    # Sort by phrase length then alphabetically; filter to meaningful keywords only
    def sort_key(kw):
        return (len(kw.split()), kw)

    def is_meaningful(kw):
        return not all(w in ALL_STOPWORDS for w in kw.split())

    return {
        "total_jd_keywords": total,
        "matched_count": len(matched),
        "missing_count": len(missing),
        "match_rate_pct": match_rate,
        "matched": sorted([k for k in matched if is_meaningful(k)], key=sort_key)[:40],
        "missing": sorted([k for k in missing if is_meaningful(k)], key=sort_key)[:40],
    }


# ---------------------------------------------------------------------------
# Section heading detection
# ---------------------------------------------------------------------------

def detect_section_headings(resume_text: str) -> dict:
    """
    Detect which standard ATS section headings are present in the resume.

    Checks for each heading on its own line or followed by a colon, as well
    as a simple substring presence fallback. Returns found/missing lists and
    the exact heading text detected for each section.

    Does NOT produce a score — that is the AI's responsibility.
    """
    resume_lower = resume_text.lower()
    details = {}

    # For each standard section, try variants: line-start + colon/newline, then substring
    for section, variants in STANDARD_HEADINGS.items():
        found = False
        found_as = None
        for variant in variants:
            pattern = r"(?:^|\n)\s*" + re.escape(variant) + r"\s*[:\n]"
            if re.search(pattern, resume_lower):
                found = True
                found_as = variant
                break
            if variant in resume_lower:
                found = True
                found_as = variant
                break
        details[section] = {"found": found, "found_as": found_as}

    return {
        "found": [s for s, d in details.items() if d["found"]],
        "missing": [s for s, d in details.items() if not d["found"]],
        "details": details,
    }


# ---------------------------------------------------------------------------
# Contact information detection
# ---------------------------------------------------------------------------

# Precompiled for reuse (avoids recompilation on every detect_contact_info call)
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_REGEX = re.compile(r"(?:\+?\d[\d\s\-\(\)\.]{7,}\d)")
LOCATION_REGEX = re.compile(
    r"(?:[A-Z][a-z]+(?:,\s*[A-Z]{2}|\s+[A-Z]{2})|\b\d{5}(?:-\d{4})?\b)"
)


def detect_contact_info(resume_text: str) -> dict:
    """
    Detect the presence of key contact fields (email, phone, location)
    in the extracted resume text.

    Note: if contact info is embedded in a PDF header/footer or inside a
    graphic, it may not appear in the extracted text even if visible on screen.
    Absence here is therefore a meaningful ATS risk signal.

    Does NOT produce a score — that is the AI's responsibility.
    """
    return {
        "email": bool(EMAIL_REGEX.search(resume_text)),
        "phone": bool(PHONE_REGEX.search(resume_text)),
        "location": bool(LOCATION_REGEX.search(resume_text)),
    }


# ---------------------------------------------------------------------------
# Date consistency detection
# ---------------------------------------------------------------------------

DATE_FORMAT_PATTERNS = {
    "Month YYYY": (
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*\.?\s+\d{4}\b"
    ),
    "MM/YYYY": r"\b\d{1,2}/\d{4}\b",
    "YYYY only": r"\b(?:19|20)\d{2}\s*[-–—]\s*(?:19|20)\d{2}\b",
    "YYYY-Present": r"\b(?:19|20)\d{2}\s*[-–—]\s*(?:Present|Current|Now)\b",
}
# Precompiled with IGNORECASE for reuse in detect_date_consistency
_COMPILED_DATE_PATTERNS = {
    k: re.compile(v if isinstance(v, str) else "".join(v), re.IGNORECASE)
    for k, v in DATE_FORMAT_PATTERNS.items()
}


def detect_date_consistency(resume_text: str) -> dict:
    """
    Detect employment date patterns and assess format consistency.

    Identifies which date format types are present (Month YYYY, MM/YYYY,
    YYYY only, YYYY-Present) and whether the resume mixes multiple formats —
    a known ATS tenure-calculation risk.

    Does NOT produce a score — that is the AI's responsibility.
    """
    formats_found: dict[str, list[str]] = {}
    all_dates: list[str] = []

    # Collect which date formats appear and flatten matches for sampling
    for fmt_name, pattern in _COMPILED_DATE_PATTERNS.items():
        matches = pattern.findall(resume_text)
        flat_matches = [m if isinstance(m, str) else " ".join(m) for m in matches]
        if flat_matches:
            formats_found[fmt_name] = flat_matches
            all_dates.extend(flat_matches)

    format_count = len(formats_found)
    consistent = format_count <= 1

    return {
        "has_dates": len(all_dates) > 0,
        "formats_detected": list(formats_found.keys()),
        "format_count": format_count,
        "consistent": consistent,
        "mixed_formats_risk": not consistent,
        "sample_dates": all_dates[:12],
    }


# ---------------------------------------------------------------------------
# Formatting signal detection
# ---------------------------------------------------------------------------

# Precompiled for reuse (avoids recompilation on every detect_formatting_signals call)
BULLET_REGEX = re.compile(r"(?:^|\n)\s*[•·▪▸►◦‣\-\*]\s+")
DASH_BULLET_REGEX = re.compile(r"(?:^|\n)\s*[-–]\s+\w")


def detect_formatting_signals(resume_text: str) -> dict:
    """
    Detect formatting characteristics relevant to ATS parseability.

    Checks for bullet points, resume length, and table indicators (excessive
    tabs). Cannot detect multi-column layout or graphics from extracted text
    alone — those must be assessed by the AI from context clues.

    Does NOT produce a score — that is the AI's responsibility.
    """
    # Bullets: symbol bullets (•, -, *) or at least 3 dash-style bullets
    has_symbol_bullets = bool(BULLET_REGEX.search(resume_text))
    dash_bullet_count = len(DASH_BULLET_REGEX.findall(resume_text))
    has_dash_bullets = dash_bullet_count >= 3

    word_count = len(resume_text.split())
    tab_count = resume_text.count("\t")

    return {
        "has_bullet_points": has_symbol_bullets or has_dash_bullets,
        "word_count": word_count,
        "adequate_length": word_count >= 200,
        "thin_resume": word_count < 200,
        "heavy_table_indicators": tab_count > 50,
        "tab_count": tab_count,
    }


# ---------------------------------------------------------------------------
# Main extractor
# ---------------------------------------------------------------------------

def extract_resume_data(resume_pdf_path: str, jd_text: str) -> dict:
    """
    Extract all mechanically-detectable ATS data from a resume PDF against
    a job description. Returns raw findings JSON — no scores.

    Covers: keyword match, section headings, contact info, date consistency,
    formatting signals.

    Does NOT cover: Experience Tenure (27%) and Education & Qualifications
    (18%) — those require semantic AI reasoning and cannot be derived from
    pattern matching alone.
    """
    resume_text, is_extractable = extract_text_from_pdf(resume_pdf_path)

    # Fail fast with clear error when PDF is image-based or empty
    if not is_extractable or not resume_text.strip():
        return {
            "is_extractable": False,
            "error": (
                "Could not extract text from this PDF. It appears to be image-based "
                "(scanned). ATS systems cannot read scanned PDFs — this is itself a "
                "critical ATS issue. The resume should be converted to a text-based PDF."
            ),
        }

    # Run all detectors and return raw findings (no scoring)
    return {
        "is_extractable": True,
        "keywords": match_keywords(jd_text, resume_text),
        "section_headings": detect_section_headings(resume_text),
        "contact_info": detect_contact_info(resume_text),
        "date_consistency": detect_date_consistency(resume_text),
        "formatting_signals": detect_formatting_signals(resume_text),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    # CLI: resume PDF, job description file, optional output path
    parser = argparse.ArgumentParser(
        description=(
            "ATS Resume Data Extractor — produces raw findings JSON for the "
            "ats-score-simulator skill. Does not score. Scoring is performed by the AI."
        )
    )
    parser.add_argument("--resume", required=True, help="Path to resume PDF")
    parser.add_argument("--jd", required=True, help="Path to job description text file")
    parser.add_argument(
        "--output", default="findings.json", help="Output JSON file path (default: findings.json)"
    )
    args = parser.parse_args()

    # Validate input paths
    resume_path = Path(args.resume)
    if not resume_path.exists() or not resume_path.is_file():
        print(f"Error: Resume PDF file not found: {args.resume}", file=sys.stderr)
        sys.exit(1)

    jd_path = Path(args.jd)
    if not jd_path.exists() or not jd_path.is_file():
        print(f"Error: Job description file not found: {args.jd}", file=sys.stderr)
        sys.exit(1)

    jd_text = jd_path.read_text(encoding="utf-8")
    result = extract_resume_data(str(resume_path), jd_text)

    # Write findings JSON (create parent dirs if needed)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if not result.get("is_extractable"):
        print(f"\nERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)

    # Summary for stdout
    kw = result["keywords"]
    hdg = result["section_headings"]
    ci = result["contact_info"]
    dc = result["date_consistency"]
    fmt = result["formatting_signals"]

    print("\nResume Data Extraction Complete")
    print(f"  Keywords:         {kw['matched_count']} matched / {kw['total_jd_keywords']} total ({kw['match_rate_pct']}%)")
    print(f"  Sections found:   {', '.join(hdg['found']) or 'none'}")
    print(f"  Sections missing: {', '.join(hdg['missing']) or 'none'}")
    print(f"  Contact info:     email={ci['email']}, phone={ci['phone']}, location={ci['location']}")
    print(f"  Date formats:     {', '.join(dc['formats_detected']) or 'none detected'} (consistent={dc['consistent']})")
    print(f"  Word count:       {fmt['word_count']} ({'adequate' if fmt['adequate_length'] else 'thin — < 200 words'})")
    print(f"\nFull findings saved to: {args.output}")
    print("\nNote: Experience Tenure (27%) and Education (18%) require AI analysis.")
    print("      Feed this JSON into the ats-score-simulator skill for the full scored report.")


if __name__ == "__main__":
    main()
