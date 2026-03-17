---
name: fix-identified-ats-issues
description: Analyzes a resume against a job description and produces a crystal-clear, action-oriented fix guide with Before/After/Rationale for each recommended ATS improvement. Use when the user wants to fix ATS issues in their resume, improve their ATS score, get specific resume edits to target a job posting, or implement recommendations from an ATS score report.
compatibility: Requires Python 3 with pdfplumber installed. Falls back to OCR via the read-pdf-document skill for scanned PDFs.
metadata:
  author: franck-boullier
  version: "1.0"
---

# Fix Identified ATS Issues

Produces a structured, edit-ready fix guide that maps every ATS score improvement recommendation to the **exact text** in the candidate's resume, with a ready-to-paste "After" rewrite and a "Rationale" explaining why each change matters.

---

## Input validation

| Input                | Required | Accepted formats                          |
| -------------------- | -------- | ----------------------------------------- |
| **Resume**           | Yes      | PDF file                                  |
| **Job Description**  | Yes      | PDF, `.txt`, `.md`, or inline pasted text |
| **ATS Score Report** | Optional | Markdown (`.md`)                          |

If the resume **or** the job description is missing, stop immediately and ask:

> To generate your ATS fix guide I need:
>
> 1. **Your resume** — please provide it as a PDF file.
> 2. **The job description** — please provide it as a PDF, plain text, or Markdown file (or paste the text directly).
>
> Optionally, you can also provide an **ATS Score Report** (Markdown) from a previous run of the `ats-score-simulator` skill. If you don't have one, I will generate it automatically.

Do not proceed until both required inputs are available.

---

## Prerequisites: check required skills

Once inputs are confirmed, verify that all dependency skills exist **relative to this skill's directory**:

| Skill                 | Expected path (relative to this skill) |
| --------------------- | -------------------------------------- |
| `read-pdf-document`   | `../read-pdf-document/SKILL.md`        |
| `txt-to-markdown`     | `../txt-to-markdown/SKILL.md`          |
| `ats-score-simulator` | `../ats-score-simulator/SKILL.md`      |

If **any file does not exist**, stop immediately and return this error:

> **Error**: The `fix-identified-ats-issues` skill requires the `[missing-skill]` skill, which was not found.
> Please install the `[missing-skill]` skill in the same skills directory before running this skill again.

If all three files exist, proceed to the workflow below.

---

## Workflow

```text
Task Progress:
- [ ] Step 1: Validate inputs
- [ ] Step 2: Verify dependency skills
- [ ] Step 3: Extract resume text from PDF
- [ ] Step 4: Normalize job description to Markdown
- [ ] Step 5: Obtain ATS Score Report (use provided or generate)
- [ ] Step 6: Map each recommendation to specific resume text
- [ ] Step 7: Produce the ATS Fix Guide
```

### Step 1 — Validate inputs

Confirm the resume PDF and job description are both provided. If not, stop and ask (see Input validation above).

### Step 2 — Verify dependency skills

Check that `../read-pdf-document/SKILL.md`, `../txt-to-markdown/SKILL.md`, and `../ats-score-simulator/SKILL.md` all exist relative to this skill's directory. Error out for any missing skill (see Prerequisites above).

### Step 3 — Extract resume text from PDF

Read `../read-pdf-document/SKILL.md` and follow its instructions to extract all text from the resume PDF.

Prefer `pdfplumber` for extraction (preserves layout better for resumes):

```python
import pdfplumber

with pdfplumber.open("resume.pdf") as pdf:
    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
```

If `pdfplumber` returns fewer than 100 characters of text across all pages, treat the extraction as failed and apply the following decision tree:

| Condition | Action |
| --------- | ------ |
| PDF appears scanned (no selectable text layer) | Fall back to OCR via the `read-pdf-document` skill. |
| PDF has a selectable text layer but extraction is still near-empty | Also attempt OCR via the `read-pdf-document` skill as a second pass (unusual encoding may be recoverable by OCR). |
| Both `pdfplumber` and OCR return fewer than 100 characters | Stop and inform the user: |

> I was unable to extract text from your resume PDF. This may be caused by password
> protection, an image-only scan, or an unusual file encoding that cannot be recovered
> by OCR. Please generate a new PDF and re-upload:
>
> - Use **"Save as PDF"** or **"Print to PDF"** directly from Word or Google Docs.
> - Avoid exporting from design tools (Canva, Adobe Illustrator, etc.) — they produce
>   image-based PDFs with no selectable text layer.

**Store the extracted resume text verbatim** — you will need to quote it exactly in the "Before" fields of the fix guide.

### Step 4 — Normalize job description to Markdown

| Format                                    | Action                                                                                              |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Already a `.md` file                      | Use as-is. No conversion needed.                                                                    |
| Plain text (`.txt` or inline pasted text) | Convert using `../txt-to-markdown/SKILL.md`, then use the result.                                   |
| PDF                                       | Extract text with `../read-pdf-document/SKILL.md`, then convert with `../txt-to-markdown/SKILL.md`. |

Store the normalized Markdown job description for use in Steps 5–6.

### Step 5 — Obtain ATS Score Report

- **If the user provided an ATS Score Report**, validate that it contains an "Improvement Plan" section (or an equivalent section listing prioritised recommendations by severity). If that section is absent, stop and ask:

  > The ATS Score Report you provided does not appear to contain an **Improvement Plan** section.
  > Please confirm one of the following:
  >
  > 1. Is this a report generated by the `ats-score-simulator` skill? If so, please check that the full report was included.
  > 2. Does the report use a different heading for its recommendations (e.g. "Action Items", "Recommended Changes", "Next Steps")? If so, please share that heading so I can locate the right section.
  > 3. Alternatively, paste the recommendations section directly and I will use it as the source of fixes.
  >
  > Do not proceed until a valid list of recommendations is available.

- **If no report was provided**, read `../ats-score-simulator/SKILL.md` and follow its full workflow to generate the report using the resume and job description obtained in Steps 3–4. Inform the user that the report is being generated before proceeding.

Store the complete report — specifically the **Improvement Plan** section (or confirmed equivalent heading) — for use in Step 6.

### Step 6 — Map recommendations to specific resume text

For **each improvement item** in the ATS Score Report's Improvement Plan, perform the following:

1. **Identify the target section** — determine which part of the resume (summary, job title, bullet point, section heading, date field, skills list, etc.) the recommendation refers to.

2. **Quote the exact "Before"** — find and copy the verbatim text from the extracted resume that must change.
   - If the text is a full bullet point, quote the entire bullet.
   - If the recommendation is to _add_ something entirely new (e.g., a missing section or a missing keyword group), set the "Before" to `(section does not exist)` or `(not present in resume)`.
   - Do **not** paraphrase or summarize — quote character-for-character.

3. **Draft the "After"** — write a complete, ready-to-paste replacement that:
   - Incorporates the missing keywords, phrases, or structural changes specified in the recommendation.
   - Retains the candidate's authentic voice, tone, and factual accuracy.
   - Is written in the same style as the surrounding resume content (tense, person, formatting).
   - Is the full text of the revised element (entire bullet, full heading, complete section, etc.) — never a partial snippet.
   - Standardizes any date ranges touched by the fix to "Month Year – Month Year" format (e.g., "January 2020 – March 2023"), ensuring consistent tenure calculation by ATS parsers.

4. **Write the "Rationale"** — explain in 2–4 sentences:
   - Which ATS scoring dimension is improved (Keyword Match, Experience Tenure, Education & Qualifications, or Formatting & Completeness).
   - Why the specific change increases the score (e.g., keyword now present in summary carries 2× weight vs. deep bullet; date format now consistent allowing correct tenure calculation).
   - How significant the impact is (Critical / High / Medium / Low, matching the Improvement Plan priority).

### Step 7 — Produce the ATS Fix Guide

Format the final output using the template in [references/OUTPUT-TEMPLATE.md](references/OUTPUT-TEMPLATE.md).

**Before/After formatting:** Always wrap the "Before" and "After" content in **fenced code blocks** with the `text` language tag so they are clearly delimited and easy to copy:

- Use `**Before:**` followed by a blank line, then a ` ```text ` block containing the exact resume text.
- Use `**After:**` followed by a blank line, then a ` ```text ` block containing the replacement text.
- Do **not** use blockquotes (`>`) for Before/After content — use only ` ```text ` ... ` ``` `.

Name the output file: `ATS-Fix-Guide-[Candidate Last Name]-[Job Title Slug].md`
Example: `ATS-Fix-Guide-BOULLIER-Head-API-Embedded-Finance.md`

---

## Guidelines

- **Verbatim "Before"**: The "Before" field must contain the **exact text** from the resume, word-for-word, including original punctuation, casing, and spacing. Never paraphrase. Format it inside a ` ```text ` code block (see OUTPUT-TEMPLATE).
- **Ready-to-paste "After"**: The "After" field must be complete and usable immediately — not a description of what to write, but the actual replacement text. Format it inside a ` ```text ` code block (see OUTPUT-TEMPLATE).
- **No invented facts**: Never fabricate experience, qualifications, skills, or employer details the candidate does not have. If a Critical recommendation cannot be addressed without adding inaccurate information, note this explicitly and suggest honest alternatives (e.g., reframing existing experience).
- **Priority order**: Present fixes in the same priority order as the ATS Score Report: Critical → High → Medium → Low.
- **Completeness**: Address **every** item from the Improvement Plan — do not cherry-pick. If a recommendation produces multiple distinct edits (e.g., updating three separate bullets), create a separate numbered fix for each.
- **Structural layout issues**: Structural problems are part of the Formatting & Completeness dimension (10–15% of the ATS score) and must be treated as High or Critical fixes when present. Scan the extracted resume text for the following patterns and include a structural fix item for any that are detected:
  - **Two-column layouts** — parsers read horizontally across the full page width, merging unrelated columns into nonsensical strings. Recommend converting to a single-column layout.
  - **Tables used for core content** (skills, experience, contact info) — older and mid-tier ATS engines skip or misread table cells entirely. Recommend replacing with plain bullet lists.
  - **Contact info in headers or footers** — many ATS extraction engines focus on the document body and ignore header/footer regions. Recommend moving all contact details to the top of the main body.
  - **Graphics, icons, or decorative elements** — invisible to most parsers; OCR may fail to interpret text embedded in images. Recommend removing all non-text decorative elements.
  - **Non-standard section headings** (e.g., "Seasoned Executive", "My Journey") — parsers rely on standard anchors like "Professional Experience", "Education", "Skills". Recommend replacing with standard headings.
- **Keyword density**: In "After" rewrites, target 2–3% keyword density for any given term across the full resume. Do not repeat a single keyword more than 3–4 times — density above 5% triggers an ATS manipulation flag and may reduce the score rather than improve it.
- **Date format standardization**: All date ranges in "After" rewrites must use "Month Year – Month Year" format (e.g., "January 2020 – March 2023"). Inconsistent formats cause ATS parsers to miscalculate tenure, directly reducing the Experience Tenure score (25–30% of the total ATS score).
- **Tone**: The fix guide is for the candidate, not the recruiter. Write the "After" text and "Rationale" in a clear, professional, first-person-ready voice.
