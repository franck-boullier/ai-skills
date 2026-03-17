---
name: ats-score-simulator
description: Simulates an ATS (Applicant Tracking System) compatibility score by comparing a resume against a job description. Produces a scored report covering keyword match, experience tenure, education, formatting, and prioritized improvement recommendations. Use when a user wants to know how well their resume matches a job posting, check their ATS score, optimize their resume for a specific role, or understand what keywords they are missing.
metadata:
  author: franck-boullier
  version: "1.5"
compatibility: "python>=3.9"
allowed-tools: Bash(python:*)
---

# ATS Score Simulator

Simulates an Applicant Tracking System (ATS) compatibility score by comparing a candidate's resume against a job description. Produces a structured report with a weighted score, gap analysis, and actionable improvement recommendations.

---

## Prerequisites: check required skills

This skill requires two dependency skills. They are verified in **Step 2** of the Workflow below — after inputs have been collected. Check whether these files exist **relative to this skill's directory**:

| Skill               | Expected path (relative to this skill) |
| ------------------- | -------------------------------------- |
| `read-pdf-document` | `../read-pdf-document/SKILL.md`        |
| `txt-to-markdown`   | `../txt-to-markdown/SKILL.md`          |

- If **either file does not exist**, stop immediately and return this error to the user:

  > **Error**: The `ats-score-simulator` skill requires the `[missing-skill]` skill, which was not found.
  > Please install the `[missing-skill]` skill in the same skills directory before running this skill again.

- If both files exist, proceed to the next step in the Workflow.

---

## Input validation

This skill requires **two inputs** from the user:

| Input               | Required format                                                                  | Why it is needed                                                                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Resume**          | PDF file                                                                         | The candidate's resume is parsed and scored against the job description. Without it, there is nothing to evaluate.                                                |
| **Job Description** | PDF, plain text (`.txt`), or Markdown (`.md`) file — or plain text pasted inline | The job description defines the target keywords, required experience, and qualifications that the ATS would match against. Without it, no comparison is possible. |

If **either input is missing**, stop immediately and ask the user to provide it. Use this message as a guide:

> To simulate your ATS score I need two things:
>
> 1. **Your resume** — please provide it as a PDF file.
> 2. **The job description** — please provide it as a PDF, plain text, or Markdown file (or paste the text directly).
>
> Both are required because the ATS score is calculated by comparing your resume against the specific requirements of the job posting.

Do not proceed until both inputs are available.

---

## Workflow

```text
Task Progress:
- [ ] Step 1: Validate inputs (resume + job description provided)
- [ ] Step 2: Verify dependency skills are installed
- [ ] Step 3: Extract resume text from PDF
- [ ] Step 4: Normalize job description to Markdown
- [ ] Step 4.5 (optional): Run data extraction script → findings.json
- [ ] Step 4.7: Identify knockout disqualifiers
- [ ] Step 5: Run ATS scoring simulation
- [ ] Step 5a: Score Keyword Match
- [ ] Step 5b: Score Experience Tenure
- [ ] Step 5c: Score Education & Qualifications
- [ ] Step 5d: Score Formatting & Completeness
- [ ] Step 5e: Score Contact Information
- [ ] Step 5f: Score Date Consistency
- [ ] Step 6: Produce the structured report
- [ ] Step 7: Save the report as a Markdown file
```

### Step 1 — Validate inputs

Confirm both the resume PDF and the job description have been provided. If not, stop and ask (see Input validation above).

### Step 2 — Verify dependency skills

Check for `../read-pdf-document/SKILL.md` and `../txt-to-markdown/SKILL.md` relative to this skill's directory. Error out for any missing skill (see Prerequisites above).

### Step 3 — Extract resume text from PDF

Read the `read-pdf-document` skill (`../read-pdf-document/SKILL.md`) and follow its instructions to extract all text from the resume PDF.

Prefer `pdfplumber` for extraction (it preserves layout better for resumes); fall back to `pypdf` if `pdfplumber` returns empty text. Both libraries and the exact fallback logic are implemented in `scripts/extract_resume_data.py` — see the `extract_text_from_pdf` function.

If both libraries return empty text, the PDF is image-based (scanned). Do not proceed with scoring — see **Edge Cases** at the bottom of this skill for how to handle this.

Store the extracted resume text for use in Step 5.

### Step 4 — Normalize job description to Markdown

The job description may arrive in several formats. Apply the following logic:

| Format                                         | Action                                                                                                                                           |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| Already a `.md` file                           | Use as-is. No conversion needed.                                                                                                                 |
| Plain text (`.txt` file or inline pasted text) | Use the `txt-to-markdown` skill (`../txt-to-markdown/SKILL.md`) to convert it to a `.md` file, then use the result.                              |
| PDF file                                       | First use the `read-pdf-document` skill to extract the text, then use the `txt-to-markdown` skill to convert the extracted text to a `.md` file. |

Store the normalized Markdown job description for use in Step 5.

### Step 4.5 — Run the data extraction script (optional but recommended)

This skill includes a Python script that mechanically extracts structured findings from the resume PDF and the job description. Running it gives you a precise, reproducible data foundation for four of the six scoring dimensions, and reduces reliance on AI recall for keyword matching and pattern detection.

**Install dependencies and run:**

```bash
pip install -r scripts/requirements.txt --break-system-packages -q

python scripts/extract_resume_data.py \
  --resume "/path/to/resume.pdf" \
  --jd "/tmp/job_description.txt" \
  --output "/tmp/findings.json"
```

> The job description should be saved as a plain text file (`.txt`). If it is a `.md` file, it can be used directly — Markdown is valid plain text for this script.

**What the script produces (`findings.json`):**

```json
{
  "is_extractable": true,
  "keywords": {
    "total_jd_keywords": 95,
    "matched_count": 68,
    "missing_count": 27,
    "match_rate_pct": 71.6,
    "matched": ["Python", "SQL", "API", "..."],
    "missing": ["Kubernetes", "Terraform", "..."]
  },
  "section_headings": {
    "found": ["experience", "education", "skills", "summary"],
    "missing": ["contact", "certifications"],
    "details": { "...": "..." }
  },
  "contact_info": { "email": true, "phone": true, "location": false },
  "date_consistency": {
    "has_dates": true,
    "formats_detected": ["Month YYYY"],
    "consistent": true,
    "mixed_formats_risk": false,
    "sample_dates": ["Jan 2018", "Mar 2023", "..."]
  },
  "formatting_signals": {
    "has_bullet_points": true,
    "word_count": 820,
    "adequate_length": true,
    "thin_resume": false,
    "heavy_table_indicators": false
  }
}
```

**What the script covers and does NOT cover:**

| Dimension                            | Script covers?                                   | Note                                                            |
| ------------------------------------ | ------------------------------------------------ | --------------------------------------------------------------- |
| Keyword Match (35%)                  | Yes — keyword list, match rate                   | AI applies the placement-quality and density judgment           |
| Formatting & Completeness (10%)      | Partially — bullet points, word count, tab count | AI assesses multi-column layout, graphics, creative headings    |
| Contact Information (5%)             | Yes — email, phone, location detected            | AI judges header/footer risk from context                       |
| Date Consistency (5%)                | Yes — formats detected, consistency flag         | AI cross-references with the Experience section                 |
| **Experience Tenure (27%)**          | **No**                                           | Requires AI semantic reasoning about career dates and relevance |
| **Education & Qualifications (18%)** | **No**                                           | Requires AI semantic reasoning about degrees and certifications |

If the script is not available or fails, proceed with AI-only analysis for all dimensions.

### Step 4.7 — Identify knockout disqualifiers

Before scoring, scan the job description for binary disqualifiers — requirements that would trigger an automatic rejection in a real ATS, regardless of the resume's overall match score. These are processed before content scoring and represent a separate evaluation layer.

**What to look for:**

| Disqualifier type | Examples |
| ----------------- | -------- |
| Work authorisation | "Must be authorised to work in the US", "No visa sponsorship" |
| Hard minimum experience | "Minimum 5 years of X required" (stated as a hard filter, not a preference) |
| Mandatory degree or field | "Bachelor's degree in Computer Science required", "MBA required" |
| Mandatory certification or licence | "PMP required", "CPA licence required", "Active security clearance required" |
| Logistical requirement | "Must be willing to relocate", "Requires 50% travel" |

**How to check:**

1. List every binary disqualifier found in the job description.
2. For each one, check whether the resume provides explicit evidence of meeting it.
3. Classify each as: **Met**, **Not met**, or **Unclear** (evidence ambiguous or absent).

**How to report:**

- If any disqualifier is **Not met** or **Unclear**, flag it as a **Critical** item in the Improvement Plan (Step 6) with the exact text from the job description.
- Note in the report that failing a knockout criterion in a real ATS typically results in automatic rejection before the resume score is evaluated.
- Do **not** subtract points from the weighted ATS score for knockout failures — the score simulates the resume content match; knockout logic is a separate layer. Instead, present knockout results in a dedicated "Knockout Check" section of the report, above the scoring table.
- If no knockout disqualifiers are found in the job description, note this explicitly: "No binary knockout criteria identified in this job description."

### Step 5 — Run ATS scoring simulation

Using the extracted resume text, the normalized job description, **and the `findings.json` output if available**, perform the following scoring analysis. Read [references/SCORING-METHODOLOGY.md](references/SCORING-METHODOLOGY.md) for the full scoring criteria and weight definitions.

When `findings.json` is available, use its data as the primary source of evidence for Steps 5a, 5d, 5e, and 5f. Apply your judgment on top of that data — the script provides raw signals, not final scores.

#### Scoring dimensions

Score each dimension on a 0–100 scale, then apply the weights below to compute the overall score.

| Dimension                      | Weight | What to evaluate                                                                             |
| ------------------------------ | ------ | -------------------------------------------------------------------------------------------- |
| **Keyword Match**              | 35%    | Presence, frequency, and placement of job description keywords in the resume                 |
| **Experience Tenure**          | 27%    | Total years of relevant experience vs. what the job description requires                     |
| **Education & Qualifications** | 18%    | Degree level, field of study, certifications vs. requirements                                |
| **Formatting & Completeness**  | 10%    | ATS-friendly structure, standard headings, no parsing traps (tables, graphics, multi-column) |
| **Contact Information**        | 5%     | Email, phone, and location present in plain text (not inside headers/footers or images)      |
| **Date Consistency**           | 5%     | Employment dates follow a parseable, consistent format throughout the resume                 |

**Overall Score** = `(Keyword × 0.35) + (Tenure × 0.27) + (Education × 0.18) + (Formatting × 0.10) + (Contact × 0.05) + (Dates × 0.05)`

#### Keyword analysis sub-steps

If `findings.json` is available, use `keywords.matched` and `keywords.missing` as your starting keyword lists — the script's 3-pass extractor (capitalized terms, tech-pattern terms, meaningful 2-word phrases) is more systematic than ad-hoc recall.

1. Extract all significant keywords and phrases from the job description (job titles, hard skills, tools, technologies, certifications, soft skills explicitly named). If `findings.json` is available, start from its lists and supplement with any semantically important keywords the script may have missed (e.g., role-specific soft skills, industry jargon phrased in full sentences).
2. Check each keyword against the resume text (exact match and close variants).
3. Classify each keyword as: **Found**, **Partial match**, or **Missing**.
4. Calculate keyword density for the top keywords (number of appearances / total resume word count × 100). Flag keywords with density > 5% as potential stuffing.
5. Note placement quality: keywords in the Summary, Job Titles, or Section Headers carry more weight than those in deep bullet points.

#### Experience tenure sub-steps

1. Parse all job entries in the resume to extract date ranges.
2. Sum the total years of relevant experience.
3. Extract the experience requirement stated in the job description (e.g., "5+ years", "3–7 years").
4. Score based on gap: exact match = high score; below minimum = low score; above maximum = moderate reduction.

#### Education sub-steps

1. Identify the education requirement in the job description (degree level, field, certifications).
2. Match against the candidate's stated education and certifications.
3. Score based on match: exact or exceeding = high; related field = medium; missing = low.

#### Formatting sub-steps

If `findings.json` is available, use `formatting_signals` (bullet points, word count, table indicators) and `section_headings` (found/missing sections with exact heading text) as your primary data source.

1. Check for ATS-parsing risks: multi-column layout signals, tables for core content, graphics, headers/footers used for contact info, non-standard section headings. Note: the script detects tab-count as a proxy for tables but cannot detect multi-column layout or graphics — assess those from context.
2. Use `section_headings.found` and `section_headings.missing` from the script, or check manually: Summary/Objective, Experience, Education, Skills, Certifications.
3. Flag creative headings (e.g., "My Journey") identified in `section_headings.details` or found during reading.
4. Identify any keyword stuffing flags (density > 5%).

#### Contact information sub-steps

If `findings.json` is available, use `contact_info.email`, `contact_info.phone`, and `contact_info.location` as the detection baseline.

1. Use the script's `contact_info` findings: if a field is `false`, it was not found in extracted text — which itself is an ATS risk (either absent or trapped in a header/footer/image).
2. If a field is `true` in the script output, use your judgment to assess whether it is in the body text or likely in a header/footer zone based on the resume structure.
3. Flag any contact details that appear to be embedded in images, graphics, or header/footer zones — ATS parsers typically skip those zones.
4. Score: full marks (100) if all three fields are present and in the body; deduct proportionally for each missing or at-risk field.

#### Date consistency sub-steps

If `findings.json` is available, use `date_consistency.formats_detected`, `date_consistency.consistent`, `date_consistency.mixed_formats_risk`, and `date_consistency.sample_dates` as your data source.

1. Use the script's `date_consistency` findings to identify detected date formats and any mixing.
2. Flag any entries with year-only dates or missing months — these reduce ATS accuracy for tenure calculations.
3. Score: full marks (100) if all dates are present, consistent in format, and parseable; reduce score proportionally for mixed formats, missing months, or absent dates.

### Step 6 — Produce the structured report

Format the final output using the report template in [references/OUTPUT-TEMPLATE.md](references/OUTPUT-TEMPLATE.md).

### Step 7 — Save the report as a Markdown file

After producing the report, save it as a `.md` file in **the same directory as the resume PDF**. This keeps the report co-located with the source document and makes it easy to find.

#### Naming convention

```
ATS-Score-Report-[CANDIDATE-NAME]-[YYYY-MM-DD].md
```

| Component           | Value                              | How to derive                                         |
| ------------------- | ---------------------------------- | ----------------------------------------------------- |
| `ATS-Score-Report-` | Fixed prefix                       | Always use this exact prefix                          |
| `[CANDIDATE-NAME]`  | Candidate's name, hyphen-separated | Derive from the resume PDF filename (see rules below) |
| `[YYYY-MM-DD]`      | Today's date                       | Use the ISO date of the day the report is run         |

**Examples:**

| Resume PDF filename              | Output report filename                           |
| -------------------------------- | ------------------------------------------------ |
| `Resume - Franck BOULLIER_4.pdf` | `ATS-Score-Report-Franck-BOULLIER-2026-03-11.md` |
| `CV - Jane Smith.pdf`            | `ATS-Score-Report-Jane-Smith-2026-03-11.md`      |
| `john_doe_resume_v2.pdf`         | `ATS-Score-Report-john-doe-2026-03-11.md`        |
| `MyResume.pdf`                   | `ATS-Score-Report-MyResume-2026-03-11.md`        |

#### Rules for deriving CANDIDATE-NAME from the PDF filename

Apply these transformations in order to the filename stem (without extension):

1. Strip common prefixes (case-insensitive): `Resume -`, `Resume_`, `CV -`, `CV_`
2. Strip trailing version suffixes: `_v2`, `_v3`, `_2`, `_3`, `_final`, `_updated`, etc.
3. Replace spaces and underscores with hyphens.
4. Strip any remaining characters that are not letters, digits, or hyphens.

If the filename does not yield a usable name after these transformations, extract the candidate's name from the first line of the resume content (typically the large-text name at the top of the document).

#### Save the report using `scripts/utils.py`

```bash
python scripts/utils.py \
  --resume "/path/to/resume.pdf" \
  --report-file "/tmp/report.md"
```

The script derives the candidate name from the PDF filename (stripping common prefixes and version suffixes), appends today's date, and writes the report to the same directory as the resume. See `scripts/utils.py` for the `derive_candidate_name` logic and all naming transformation rules.

After saving, confirm to the user with the full file path:

> **Report saved:** `[full path to the .md file]`

---

## Guidelines

- Be **specific**: cite evidence from both the resume and the job description to justify every score.
- Be **honest**: if the resume is a poor match, the score should reflect that. Do not inflate scores.
- Be **encouraging but honest** in tone — like a career coach giving real, useful feedback, not a bureaucratic checklist.
- Be **actionable**: every weakness identified must have a concrete recommendation in the Improvement Plan. Do not give generic advice like "add more keywords" — instead say "Add 'stakeholder management' to the Professional Summary and at least two bullet points in the Experience section."
- For the keyword gap table, list **all** missing high-priority keywords, not just a sample.
- For the Overall Score, use this interpretation scale:

  | Score   | Label              | ATS Outcome                                |
  | ------- | ------------------ | ------------------------------------------ |
  | 80–100% | 🟢 Strong match    | Likely to pass most ATS filters            |
  | 60–79%  | 🟡 Moderate match  | May pass but risks being ranked lower      |
  | 40–59%  | 🟠 Weak match      | Likely to be filtered out or ranked poorly |
  | 0–39%   | 🔴 Very poor match | High probability of automatic rejection    |

---

## Edge Cases

Handle the following situations explicitly rather than producing a partial or misleading score:

| Situation                                                                 | How to handle                                                                                                                                                               |
| ------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scanned/image-based PDF** (both pdfplumber and pypdf return empty text) | Report a score of 0 on all dimensions. Explain that image-based PDFs cannot be read by ATS — this is itself a critical ATS issue. Recommend converting to a text-based PDF. |
| **Very short resume** (< 200 words after extraction)                      | Flag this as a concern even if keywords match. Thin resumes often rank poorly. Note it explicitly in the Improvement Plan.                                                  |
| **Creative section headings** (e.g., "My Journey", "Where I've Been")     | Flag each one by name and explain the ATS risk. Recommend replacing with a standard heading.                                                                                |
| **Job description in a non-English language**                             | Score as normal but note the language context and that keyword matching may be less reliable.                                                                               |
| **Resume already scores > 90**                                            | Celebrate the strong result. Still identify any remaining gaps and recommend addressing them for completeness.                                                              |
