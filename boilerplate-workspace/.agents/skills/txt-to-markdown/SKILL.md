---
name: txt-to-markdown
description: Converts plain text (.txt) files into well-structured Markdown (.md) files that strictly comply with the DavidAnson/vscode-markdownlint ruleset. Use this skill whenever the user wants to convert, transform, or reformat a text file into markdown — even if they say things like "turn this into markdown", "make this a markdown doc", "format my notes as markdown", "clean up this text file", or "convert my .txt to .md". Also trigger when the user uploads or references a .txt file and asks for any kind of document formatting, structuring, or reorganization. If a text file needs to be made readable, structured, or publishable as markdown, use this skill.
---

# Plain Text → Markdown Converter (markdownlint-compliant)

Your job is to read a plain text file and produce a clean, well-structured Markdown file that faithfully preserves the content, applies intelligent formatting, and **passes all default rules of the DavidAnson/vscode-markdownlint extension**.

The detailed rule reference is at: `references/markdownlint-rules.md` — read it if you need to check specifics. A validation script is at `scripts/lint_check.py`.

---

## Step 1: Read and understand the document

Before converting anything, read the whole document to understand:
- What kind of document is it? (meeting notes, article, recipe, report, readme, letter, etc.)
- What structural conventions does the author use? (ALL CAPS headings, numbered sections, dash bullets, etc.)
- Are there repeated patterns that signal headings, subheadings, or sections?

---

## Step 2: Infer structure intelligently

Use context and pattern recognition to identify elements:

**Headings** — Look for:
- Short lines (under ~60 chars) that start a new section, especially after a blank line
- ALL CAPS or Title Case lines that don't end in punctuation
- Lines followed by a blank line and then paragraph text
- Numbered sections like "1. Introduction" or "Section 2:"
- Underlined headings (a line of dashes or equals signs below the text — convert to ATX)

**Lists** — Look for:
- Lines starting with `-`, `*`, `•`, `+`, or similar (convert all to `-`)
- Lines starting with `1.`, `2.`, `a.`, `b.`, etc.
- Short parallel lines that clearly enumerate items
- Indented sub-items that nest under a parent item

**Code / preformatted text** — Look for:
- Content that looks like commands, file paths, shell output, JSON, config files
- Lines with `$` prompt prefixes or indented blocks of non-prose
- Always use fenced code blocks, never 4-space indentation

**Tables** — Look for tab-separated or aligned-column data

**Emphasis** — Use sparingly and only where clearly intended in the source

---

## Step 3: Handle paragraphs and line breaks correctly

- In Markdown, a single newline within a paragraph is *ignored* — you need a blank line to create a paragraph break.
- If the source has hard-wrapped lines (each line ~72 chars and wrapping mid-sentence), **join them** into single flowing paragraphs. Don't create line breaks where the author just had word-wrap.
- If the source has intentional line breaks (like poetry or addresses), use `<br>` rather than two trailing spaces (two trailing spaces are easy to accidentally strip).
- When in doubt: if lines form a coherent thought together, merge them; if each line stands alone, keep them separate.

---

## Step 4: Generate the front matter

Every output file must begin with a YAML front matter block. Set the following fields (infer only the description from the document content; set name and last-updated as specified below):

```yaml
---
name: <output filename including .md extension>
description: <One- or two-sentence summary of what this document covers and why it matters.>
last-updated: <today's date in YYYY-MM-DD format>
---
```

Guidelines for each field:

- **`name`**: Use the output filename including its `.md` extension (e.g., `notes.md`, `meeting_notes.md`). Do not use a title derived from the document content.
- **`description`**: Write a concise summary (1–2 sentences) that captures the subject and purpose of the document. This should be informative enough to understand the document without reading it.
- **`last-updated`**: Always set this to today's date in `YYYY-MM-DD` format.

Place this block at the very top of the file, before any markdown content (including the H1 heading). The front matter is not markdown content — the linter skips it automatically.

---

## Step 5: Apply markdownlint rules during formatting

This is the key addition — the output must pass the vscode-markdownlint defaults. The most impactful rules are:

### Headings
- **MD001**: Never skip heading levels. H2 must follow H1; H3 must follow H2. If the source jumps from a major heading to a third-level sub-section, insert a logical intermediate level.
- **MD003**: Always use ATX style (`## Heading`). Never write setext underline headings.
- **MD022**: Surround every heading with blank lines above and below.
- **MD023**: Headings start at column 0 — never indent a heading.
- **MD025**: Only one `# H1` in the whole document.
- **MD026**: Headings must not end with `.` `,` `:` `;` `!` `?` — strip trailing punctuation from headings.
- **MD036**: Don't use a line of `**bold text**` alone as a substitute for a real heading. If it functions as a heading, make it one.

### Lists
- **MD004**: Use `-` for all unordered lists. Replace any `*` or `+` bullets with `-`.
- **MD007**: Sub-lists indented by exactly 2 spaces per level.
- **MD029**: Ordered lists use sequential numbers: `1.`, `2.`, `3.` — not `1.`, `1.`, `1.`.
- **MD030**: Exactly one space after the list marker.
- **MD032**: Surround every list block with a blank line above and below.

### Code blocks
- **MD031**: Surround every fenced code block with a blank line above and below.
- **MD040**: Always specify a language on fenced code blocks. Use `text` or `plain` if no specific language applies (e.g., generic command output or plain pre-formatted text).
- **MD046**: Always use fenced code blocks (` ``` `). Convert any 4-space-indented code to fenced.
- **MD048**: Always use backtick fences (` ``` `), never tilde fences (`~~~`).

### Whitespace
- **MD009**: No trailing spaces (spaces at end of line).
- **MD010**: No hard tab characters anywhere — use spaces.
- **MD012**: Maximum one blank line between any two elements.
- **MD047**: End the file with exactly one newline character.

### Inline formatting
- **MD037**: No spaces inside emphasis: `*text*` not `* text *`.
- **MD038**: No spaces inside code spans: `` `code` `` not `` ` code ` ``.
- **MD049**: Use `*asterisks*` for italics, not `_underscores_`.
- **MD050**: Use `**double asterisks**` for bold, not `__double underscores__`.
- **MD035**: Horizontal rules use exactly `---`.

---

## Step 6: Write the output file and validate

1. Name the output file the same as the input but with a `.md` extension (`notes.txt` → `notes.md`), unless the user specifies otherwise.
2. Save it to the same directory as the input file, unless the user specifies otherwise.
3. Don't add commentary, preamble, or metadata that wasn't in the original.
4. **Run the validator:**

```bash
python <skill-dir>/scripts/lint_check.py <output-file.md>
```

5. If there are violations, fix them and re-run until the output is clean.

---

## Quality bar

The converted file must:
- Pass all default vscode-markdownlint rules (zero violations from `lint_check.py`)
- Preserve 100% of the original content (no additions, no deletions)
- Be immediately renderable in any Markdown viewer without looking broken
- Be clean and readable in raw form as well as rendered

---

## Example transformations

**Input (heading-like text with ALL CAPS and trailing colon):**
```text
INTRODUCTION

This document covers the main points of the project.
We will discuss three areas.
```
**Compliant output** (MD026 removes the implicit colon; MD022 adds blank lines):
```markdown
## Introduction

This document covers the main points of the project. We will discuss three areas.
```

---

**Input (hard-wrapped paragraph):**
```text
The quarterly results show a strong performance
across all divisions. Revenue was up 12% compared
to the same period last year.
```
**Compliant output** (lines joined into paragraph):
```markdown
The quarterly results show a strong performance across all divisions. Revenue was up 12% compared to the same period last year.
```

---

**Input (mixed bullets, unformatted list):**
```text
Items needed:
* Flour
+ Sugar
- 2 eggs
- Butter (softened)
```
**Compliant output** (MD004 normalizes to `-`; MD032 adds blank lines; MD026 strips the colon from a would-be heading):
```markdown
Items needed:

- Flour
- Sugar
- 2 eggs
- Butter (softened)
```

---

**Input (indented code block):**
```text
To install, run:

    pip install mypackage
```
**Compliant output** (MD046 converts to fenced; MD040 adds language; MD031 adds blank lines):
```markdown
To install, run:

```bash
pip install mypackage
```
```

---

## Edge cases

- **Very short files**: Still apply structure inference; a single paragraph needs no heading.
- **Files with no structure at all**: Clean up line breaks, output as clean paragraphs — don't invent structure.
- **Non-English text**: Apply the same logic — markdownlint rules are language-agnostic.
- **Documents with no clear title**: Don't invent an H1 (MD041 only flags a missing H1 if the document has a title — omitting is fine for untitled notes).
- **Bold text used as headings** (MD036): If a line is just `**Introduction**` with nothing else on it, convert it to `## Introduction`.
- **Heading hierarchy gaps**: If the source has only one level of headings (all caps = all the same weight), you may need to decide which are H2 and which are H3 based on content. Use the document's overall structure as a guide.
