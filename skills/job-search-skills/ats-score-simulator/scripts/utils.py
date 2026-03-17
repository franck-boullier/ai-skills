#!/usr/bin/env python3
"""
ATS Score Simulator — report filename and save utilities

Derives a candidate name from a resume PDF filename and saves the ATS score
report as a Markdown file alongside the source resume.

Usage:
    python scripts/utils.py \
        --resume "/path/to/Resume - Jane Smith.pdf" \
        --report-file "/tmp/report.md"

The output file is written to the same directory as the resume PDF using this
naming convention:
    ATS-Score-Report-<CANDIDATE-NAME>-<YYYY-MM-DD>.md

Functions available for import:
    derive_candidate_name(pdf_path) -> str
    build_report_filename(pdf_path) -> str
    save_report(pdf_path, report_content) -> Path
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path


def derive_candidate_name(pdf_path: str) -> str:
    """
    Derive a hyphen-separated candidate name from a resume PDF filename.

    Transformations applied in order:
      1. Strip common prefixes (case-insensitive): "Resume -", "Resume_", "CV -", "CV_"
      2. Strip trailing version suffixes: "_v2", "_3", "_final", "_updated", etc.
      3. Replace spaces and underscores with hyphens.
      4. Remove any character that is not a letter, digit, or hyphen.

    Returns "CANDIDATE" if no usable name can be derived after transformations.

    Examples:
        "Resume - Franck BOULLIER_4.pdf"  ->  "Franck-BOULLIER"
        "CV - Jane Smith.pdf"             ->  "Jane-Smith"
        "john_doe_resume_v2.pdf"          ->  "john-doe-resume"
        "MyResume.pdf"                    ->  "MyResume"
    """
    stem = Path(pdf_path).stem
    stem = re.sub(r"(?i)^(resume|cv)\s*[-_]\s*", "", stem)
    stem = re.sub(r"(?i)[_\s]+(v\d+|\d+|final|updated|new)$", "", stem.strip())
    stem = re.sub(r"[\s_]+", "-", stem.strip())
    stem = re.sub(r"[^\w\-]", "", stem)
    return stem or "CANDIDATE"


def build_report_filename(pdf_path: str) -> str:
    """Return the ATS report filename for the given resume PDF path."""
    candidate_name = derive_candidate_name(pdf_path)
    today = date.today().strftime("%Y-%m-%d")
    return f"ATS-Score-Report-{candidate_name}-{today}.md"


def save_report(pdf_path: str, report_content: str) -> Path:
    """
    Save report_content as a Markdown file in the same directory as the resume PDF.

    The output filename is derived from the PDF filename and today's date.
    Returns the Path the file was written to.
    """
    resume_path = Path(pdf_path)
    output_filename = build_report_filename(pdf_path)
    output_path = resume_path.parent / output_filename
    output_path.write_text(report_content, encoding="utf-8")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Save an ATS score report alongside the source resume PDF. "
            "Derives the output filename from the resume PDF filename and today's date."
        )
    )
    parser.add_argument("--resume", required=True, help="Path to the resume PDF")
    parser.add_argument(
        "--report-file",
        required=True,
        help="Path to a .md file containing the report content to save",
    )
    args = parser.parse_args()

    resume_path = Path(args.resume)
    if not resume_path.exists() or not resume_path.is_file():
        print(f"Error: Resume PDF not found: {args.resume}", file=sys.stderr)
        sys.exit(1)

    report_path = Path(args.report_file)
    if not report_path.exists() or not report_path.is_file():
        print(f"Error: Report file not found: {args.report_file}", file=sys.stderr)
        sys.exit(1)

    report_content = report_path.read_text(encoding="utf-8")
    output_path = save_report(str(resume_path), report_content)
    print(f"Report saved to: {output_path}")


if __name__ == "__main__":
    main()
