#!/usr/bin/env python3
"""
markdownlint-compatible checker for txt-to-markdown skill outputs.

Checks the rules most relevant to generated markdown documents,
mirroring the defaults of the DavidAnson/vscode-markdownlint extension.

Usage:
    python lint_check.py <file.md>
    python lint_check.py <file.md> --fix   # auto-fix what can be auto-fixed

Exit code: 0 = no violations, 1 = violations found
"""

import re
import sys
import argparse
from pathlib import Path


def strip_front_matter(text: str) -> tuple[str, int]:
    """
    If the file begins with a YAML front matter block (--- ... ---),
    strip it and return (remaining_text, number_of_lines_stripped).
    markdownlint ignores front matter, so we do the same.
    """
    if not text.startswith("---"):
        return text, 0
    lines = text.splitlines(keepends=True)
    # Find the closing ---
    for i in range(1, len(lines)):
        if lines[i].rstrip() == "---":
            stripped = "".join(lines[i + 1:])
            return stripped, i + 1
    return text, 0


def check(md_path: str, fix: bool = False) -> list[dict]:
    path = Path(md_path)
    raw_text = path.read_text(encoding="utf-8")
    text, front_matter_lines = strip_front_matter(raw_text)
    lines = text.splitlines()
    violations = []

    def v(rule, alias, line_no, detail, fixable=False):
        # Offset line number to account for stripped front matter
        violations.append({
            "rule": rule, "alias": alias,
            "line": line_no + front_matter_lines, "detail": detail, "fixable": fixable
        })

    # ── helpers ────────────────────────────────────────────────────────────
    def is_code_fence_start(line):
        return bool(re.match(r'^ {0,3}(`{3,}|~{3,})', line))

    def is_inside_code(line_idx, fence_ranges):
        return any(start <= line_idx <= end for start, end in fence_ranges)

    def build_fence_ranges(lines):
        """Return list of (start, end) tuples for fenced code blocks."""
        ranges = []
        in_fence = False
        fence_char = None
        start_idx = None
        for i, line in enumerate(lines):
            m = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
            if m:
                char = m.group(1)[0]
                if not in_fence:
                    in_fence = True
                    fence_char = char
                    start_idx = i
                elif char == fence_char:
                    ranges.append((start_idx, i))
                    in_fence = False
                    fence_char = None
        return ranges

    fence_ranges = build_fence_ranges(lines)

    # ── MD003: heading style must be ATX (# Heading) ──────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        # Setext underline: next line is all = or all -
        if i + 1 < len(lines):
            next_line = lines[i + 1]
            if re.match(r'^=+\s*$', next_line) or re.match(r'^-+\s*$', next_line):
                if line.strip():
                    v("MD003", "heading-style", i + 1,
                      "Use ATX-style headings (## Heading), not setext underline style", fixable=True)

    # ── MD001: heading levels increment by one ────────────────────────────
    prev_level = 0
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        m = re.match(r'^(#{1,6})\s+\S', line)
        if m:
            level = len(m.group(1))
            if prev_level > 0 and level > prev_level + 1:
                v("MD001", "heading-increment", i + 1,
                  f"Heading jumped from H{prev_level} to H{level} — increment by one level at a time")
            prev_level = level

    # ── MD018/MD019: spaces after # in ATX headings ───────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if re.match(r'^#{1,6}[^ #\n]', line):
            v("MD018", "no-missing-space-atx", i + 1,
              "No space after '#' in heading", fixable=True)
        if re.match(r'^#{1,6}  +\S', line):
            v("MD019", "no-multiple-spaces-atx", i + 1,
              "Multiple spaces after '#' in heading", fixable=True)

    # ── MD022: headings must be surrounded by blank lines ─────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if re.match(r'^#{1,6}\s', line):
            # blank line before (skip if first line)
            if i > 0 and lines[i - 1].strip() != "":
                v("MD022", "blanks-around-headings", i + 1,
                  "Heading not preceded by a blank line", fixable=True)
            # blank line after
            if i + 1 < len(lines) and lines[i + 1].strip() != "":
                v("MD022", "blanks-around-headings", i + 1,
                  "Heading not followed by a blank line", fixable=True)

    # ── MD023: headings must start at beginning of line ───────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if re.match(r'^ +#{1,6}\s', line):
            v("MD023", "heading-start-left", i + 1,
              "Heading is indented — must start at column 0", fixable=True)

    # ── MD025: only one H1 per document ───────────────────────────────────
    h1s = [i + 1 for i, line in enumerate(lines)
           if not is_inside_code(i, fence_ranges) and re.match(r'^# \S', line)]
    if len(h1s) > 1:
        for line_no in h1s[1:]:
            v("MD025", "single-title", line_no,
              "Multiple H1 headings — only one H1 is allowed per document")

    # ── MD026: no trailing punctuation in headings ────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        m = re.match(r'^#{1,6}\s+(.+)$', line)
        if m:
            heading_text = m.group(1).rstrip()
            if heading_text and heading_text[-1] in '.,:;!?':
                v("MD026", "no-trailing-punctuation", i + 1,
                  f"Heading ends with '{heading_text[-1]}' — remove trailing punctuation", fixable=True)

    # ── MD004: unordered list style must be dash ──────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if re.match(r'^ {0,3}[*+] +\S', line):
            v("MD004", "ul-style", i + 1,
              "Use '-' for unordered lists, not '*' or '+'", fixable=True)

    # ── MD007: unordered list indentation (2 spaces per level) ────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        m = re.match(r'^( +)- ', line)
        if m:
            indent = len(m.group(1))
            if indent % 2 != 0:
                v("MD007", "ul-indent", i + 1,
                  f"List indented {indent} spaces — use multiples of 2 spaces")

    # ── MD009: no trailing spaces ─────────────────────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if line.endswith("  "):
            pass  # two trailing spaces = intentional line break, allowed
        elif line != line.rstrip():
            v("MD009", "no-trailing-spaces", i + 1,
              "Trailing spaces", fixable=True)

    # ── MD010: no hard tabs ───────────────────────────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if '\t' in line:
            v("MD010", "no-hard-tabs", i + 1,
              "Hard tab character — use spaces instead", fixable=True)

    # ── MD012: no multiple consecutive blank lines ────────────────────────
    for i in range(1, len(lines) - 1):
        if lines[i].strip() == "" and lines[i - 1].strip() == "":
            v("MD012", "no-multiple-blanks", i + 1,
              "Multiple consecutive blank lines", fixable=True)

    # ── MD029: ordered list item prefix ──────────────────────────────────
    # Check for non-sequential numbering (1. 3. 5. instead of 1. 2. 3.)
    in_list = False
    expected_num = 1
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            in_list = False
            continue
        m = re.match(r'^(\d+)\. ', line)
        if m:
            num = int(m.group(1))
            if not in_list:
                in_list = True
                expected_num = num + 1
            else:
                if num != expected_num:
                    v("MD029", "ol-prefix", i + 1,
                      f"Ordered list item is {num}, expected {expected_num}", fixable=True)
                expected_num = num + 1
        else:
            in_list = False
            expected_num = 1

    # ── MD030: spaces after list markers ─────────────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if re.match(r'^( {0,3})[-*+](?![-*+])  +\S', line):
            v("MD030", "list-marker-space", i + 1,
              "Multiple spaces after list marker — use exactly one space", fixable=True)
        if re.match(r'^\d+\.  +\S', line):
            v("MD030", "list-marker-space", i + 1,
              "Multiple spaces after ordered list marker — use exactly one space", fixable=True)

    # ── MD031: fenced code blocks surrounded by blank lines ───────────────
    for i, line in enumerate(lines):
        # Check opening fence (only check fences that are at the start of a block)
        for start, end in fence_ranges:
            if i == start:
                if i > 0 and lines[i - 1].strip() != "":
                    v("MD031", "blanks-around-fences", i + 1,
                      "Fenced code block not preceded by a blank line", fixable=True)
        # Check closing fence
        for start, end in fence_ranges:
            if i == end:
                if i + 1 < len(lines) and lines[i + 1].strip() != "":
                    v("MD031", "blanks-around-fences", i + 1,
                      "Fenced code block not followed by a blank line", fixable=True)

    # ── MD032: lists should be surrounded by blank lines ─────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        is_list_item = bool(re.match(r'^ {0,3}[-*+] |^ {0,3}\d+\. ', line))
        if is_list_item:
            # Check if previous line is non-blank, non-list, non-heading
            if i > 0:
                prev = lines[i - 1]
                prev_is_list = bool(re.match(r'^ {0,3}[-*+] |^ {0,3}\d+\. ', prev))
                if prev.strip() and not prev_is_list and not re.match(r'^#{1,6}\s', prev):
                    v("MD032", "blanks-around-lists", i + 1,
                      "List not preceded by a blank line", fixable=True)

    # ── MD035: horizontal rule style must be --- ──────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        stripped = line.strip()
        # Matches ***, ___,  * * *, - - -, etc. but not ---
        if re.match(r'^(\*\*\*+|\* \* \*[* ]*|___+|_ _ _[_ ]*|---[ -]*)$', stripped):
            if stripped != "---" and not re.match(r'^-{3,}$', stripped):
                v("MD035", "hr-style", i + 1,
                  f"Horizontal rule should be '---', found '{stripped}'", fixable=True)

    # ── MD037: no spaces inside emphasis markers ──────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if re.search(r'\* \S[^*]*\*|\*[^*]* \*', line):
            v("MD037", "no-space-in-emphasis", i + 1,
              "Spaces inside emphasis markers: use *text* not * text *", fixable=True)

    # ── MD038: no spaces inside code spans ───────────────────────────────
    # Only flag when space is INSIDE the span. Do NOT flag when space is
    # before the opening backtick (e.g. "word `code`" is valid).
    # Exclude false positives: "` and `", "` or `", "`, `" (two adjacent spans).
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        # Leading space inside: ` code` — but not "` and `" or "` or `" or "`, `".
        if re.search(r'(?:^|[^\s])(` (?!and `|or `|, )\S[^`]*`)', line):
            v("MD038", "no-space-in-code", i + 1,
              "Spaces inside code span: use `code` not ` code `", fixable=True)

    # ── MD040: fenced code blocks should have language specified ──────────
    for i, line in enumerate(lines):
        # Only check opening fences, not closing fences
        is_opening_fence = any(i == start for start, end in fence_ranges)
        if is_opening_fence:
            m = re.match(r'^ {0,3}(`{3,}|~{3,})\s*$', line)
            if m:
                v("MD040", "fenced-code-language", i + 1,
                  "Fenced code block has no language specified — add a language hint (e.g. ```bash, ```python, ```text)")

    # ── MD046: code block style must be fenced ────────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        # 4-space or tab indented code blocks (not inside a list)
        if re.match(r'^    \S', line) or re.match(r'^\t\S', line):
            # Crude check: not a continuation of a list item
            prev = lines[i - 1] if i > 0 else ""
            prev_is_list = bool(re.match(r'^ {0,3}[-*+] |^ {0,3}\d+\. ', prev))
            if not prev_is_list:
                v("MD046", "code-block-style", i + 1,
                  "Use fenced code blocks (``` ... ```) not 4-space indentation", fixable=True)

    # ── MD047: file should end with single newline ────────────────────────
    if text and not text.endswith("\n"):
        v("MD047", "single-trailing-newline", len(lines),
          "File does not end with a newline character", fixable=True)
    if text.endswith("\n\n"):
        v("MD047", "single-trailing-newline", len(lines),
          "File ends with multiple blank lines — end with exactly one newline", fixable=True)

    # ── MD048: code fence style must be backtick ──────────────────────────
    for i, line in enumerate(lines):
        if re.match(r'^ {0,3}~{3,}', line):
            v("MD048", "code-fence-style", i + 1,
              "Use backtick fences (```) not tilde fences (~~~)", fixable=True)

    # ── MD049: emphasis style must be asterisk ────────────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        # _text_ (single underscore emphasis) — not inside a word
        if re.search(r'(?<!\w)_(?!_)\S[^_]*_(?!\w)', line):
            v("MD049", "emphasis-style", i + 1,
              "Use *asterisks* for emphasis, not _underscores_", fixable=True)

    # ── MD050: strong style must be double asterisk ───────────────────────
    for i, line in enumerate(lines):
        if is_inside_code(i, fence_ranges):
            continue
        if re.search(r'__\S[^_]*__', line):
            v("MD050", "strong-style", i + 1,
              "Use **double asterisks** for bold, not __double underscores__", fixable=True)

    return violations


def main():
    parser = argparse.ArgumentParser(description="Check markdown file for markdownlint violations")
    parser.add_argument("file", help="Markdown file to check")
    parser.add_argument("--fix", action="store_true", help="Show fixable violations only")
    args = parser.parse_args()

    violations = check(args.file)

    if not violations:
        print(f"✅ {args.file}: No violations found")
        sys.exit(0)

    fixable = [v for v in violations if v.get("fixable")]
    non_fixable = [v for v in violations if not v.get("fixable")]

    print(f"❌ {args.file}: {len(violations)} violation(s) found\n")
    for v in violations:
        fix_tag = " [fixable]" if v.get("fixable") else ""
        print(f"  Line {v['line']:>4}  {v['rule']}/{v['alias']}{fix_tag}")
        print(f"           {v['detail']}")

    print(f"\nSummary: {len(violations)} total, {len(fixable)} fixable, {len(non_fixable)} need manual review")
    sys.exit(1)


if __name__ == "__main__":
    main()
