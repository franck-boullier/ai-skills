---
name: SCORING-METHODOLOGY.md
description: Detailed ATS scoring criteria, dimension weight definitions, keyword density thresholds, and the output report template for the ats-score-simulator skill.
last-updated: 2026-03-11
---

# ATS Scoring Methodology

Reference guide for the `ats-score-simulator` skill. Contains scoring criteria for each dimension, interpretation guidance, and the structured output template.

---

## Dimension 1 — Keyword Match (35%)

### What keywords to extract from the job description

Extract keywords in the following priority order:

1. **Job title and role variants** — exact title plus common abbreviations (e.g., "Product Manager", "PM")
2. **Hard skills and technologies** — tools, languages, platforms, software (e.g., "Python", "Salesforce", "AWS")
3. **Certifications and credentials** — named certifications (e.g., "PMP", "CPA", "AWS Certified Solutions Architect")
4. **Domain-specific terminology** — industry jargon, methodologies (e.g., "Agile", "Scrum", "SOX compliance")
5. **Soft skills explicitly named** — only those stated literally (e.g., "stakeholder management", "cross-functional collaboration")
6. **Action verbs tied to responsibilities** — verbs that appear in required duties (e.g., "lead", "architect", "deliver")

### Keyword density thresholds

| Density range | Classification | Implication |
|---|---|---|
| 0–1% | Low visibility | Resume likely deprioritized — keyword needs to be added or reinforced |
| 2–3% | Optimal | Ideal balance of relevance and natural readability |
| 4–5% | Noticeable stacking | Approaching threshold — monitor but acceptable |
| > 5% | Manipulation flag | Likely penalized by ATS for unnatural repetition |

### Keyword placement quality

Keywords are not weighted equally regardless of where they appear. Apply a placement multiplier when scoring:

| Placement location | Relative weight |
|---|---|
| Professional Summary or Objective | Highest |
| Job Titles | Highest |
| Section Headers | High |
| Bullet point leads (first 5–7 words) | Medium-high |
| Mid-bullet or secondary mentions | Medium |
| Skills list at bottom of resume | Low-medium |

### Keyword scoring scale

| Score | Criteria |
|---|---|
| 85–100 | ≥ 80% of high-priority keywords found; most at optimal density; good placement |
| 70–84 | 60–79% of high-priority keywords found; some placement gaps |
| 50–69 | 40–59% match; several important keywords missing |
| 30–49 | < 40% match; major keyword gaps across multiple categories |
| 0–29 | Minimal keyword alignment; fundamental mismatch |

---

## Dimension 2 — Experience Tenure (27%)

### How to parse experience from the resume

1. Identify all work experience entries.
2. For each entry, extract the start and end date. If end date is absent or says "Present", use today's date.
3. Sum the total duration across all entries. For roles with overlapping dates, count the span once (do not double-count concurrent roles).
4. Identify which roles are **directly relevant** to the target job (same function, industry, or skill domain) and separately note total relevant experience vs. total career experience.

### Date format compatibility

The most ATS-compatible format is `Month Year` (e.g., `January 2020 – March 2023`). Flag the following as parsing risks:

- Mixed formats within the same document (e.g., `Jan 2020` in one entry, `03/2021` in another)
- Year-only dates (e.g., `2019 – 2022`) — these reduce accuracy
- Missing months (the ATS may assume only partial year)

### Experience tenure scoring scale

| Score | Criteria |
|---|---|
| 85–100 | Total relevant experience meets or slightly exceeds the stated requirement; dates are consistently formatted |
| 70–84 | Experience is within ± 1 year of requirement; minor date format inconsistencies |
| 50–69 | Experience is 1–2 years below requirement; or date inconsistencies that may cause miscalculation |
| 30–49 | Experience is more than 2 years below minimum; significant date format issues |
| 0–29 | Experience drastically below requirement; or experience appears unrelated to the role |

---

## Dimension 3 — Education & Qualifications (18%)

### What to assess

1. **Degree level required** — Check whether the job description requires a specific degree (Bachelor's, Master's, PhD, or equivalent). Compare against the candidate's highest degree.
2. **Field of study** — Some roles require specific fields (e.g., "Computer Science", "Finance"). A related field receives partial credit; unrelated receives low credit.
3. **Named certifications** — If the job description explicitly requires a certification (e.g., "PMP required"), treat this as a knockout criterion. Score 0 for that sub-element if absent.
4. **Preferred vs. required** — Distinguish between "required" and "preferred" qualifications. Missing a "preferred" qualification has less scoring impact than missing a "required" one.

### Education scoring scale

| Score | Criteria |
|---|---|
| 85–100 | Degree level meets or exceeds requirement; field matches; all required certifications present |
| 70–84 | Degree meets requirement; field is adjacent; optional certifications absent |
| 50–69 | Degree is one level below requirement OR field is unrelated but compensated by experience |
| 30–49 | Degree significantly below requirement; missing required certification(s) |
| 0–29 | No relevant degree or certification match; or a knockout certification is missing |

---

## Dimension 4 — Formatting & Completeness (10%)

### ATS parsing risk factors

Check the resume for the following. Each risk factor identified reduces the formatting score.

| Risk factor | Severity | Likely ATS impact |
|---|---|---|
| Multi-column layout | High | Parser may scramble left/right column text |
| Tables used for core content | High | Older ATS may skip table content entirely |
| Headers/footers used for contact info | Medium-high | Many parsers ignore header/footer zones |
| Graphics, icons, or images | High | OCR failure; content lost |
| Non-standard section headings | Medium | Parser fails to categorize content correctly |
| No professional summary | Low-medium | ATS cannot extract initial context |
| Missing Skills section | Medium | Keyword extraction relies on explicit skills section |

### Standard section headings (ATS-friendly)

An ATS-friendly resume includes these sections with conventional headings:

- Summary / Professional Summary / Objective
- Experience / Work Experience / Professional Experience
- Education
- Skills / Technical Skills / Core Competencies
- Certifications (if applicable)

Using creative headings like "My Journey", "What I've Built", or "Where I've Been" risks mislabeling or losing entire sections.

### Formatting scoring scale

| Score | Criteria |
|---|---|
| 85–100 | Single-column layout; standard headings; no graphics or tables for core content; all core sections present |
| 70–84 | Minor issues (e.g., one non-standard heading) |
| 50–69 | Some medium-risk factors (e.g., table used for skills) |
| 30–49 | Multiple high-risk factors; several sections missing or with non-standard headings |
| 0–29 | Severe formatting issues (multi-column + tables + graphics); major sections absent |

---

## Dimension 5 — Contact Information (5%)

### What to assess

Check that all three key contact fields are present in the body of the resume (not inside a header/footer zone or embedded in a graphic — ATS parsers typically skip those zones):

| Field | What to look for |
|---|---|
| **Email address** | Standard format (e.g., `name@domain.com`) in body text |
| **Phone number** | Parseable digits with optional country code, spaces, or dashes |
| **Location** | City, country, postal/zip code, or region — even a general location is sufficient |

### Contact information scoring scale

| Score | Criteria |
|---|---|
| 85–100 | All three fields (email, phone, location) present in body text |
| 60–84 | Two of three fields present; or all three present but one is in a header/footer zone |
| 30–59 | Only one field present; or contact info is primarily in a header/footer or image |
| 0–29 | No contact information detectable in the body of the resume |

---

## Dimension 6 — Date Consistency (5%)

### What to assess

1. Identify all employment date ranges in the resume.
2. Detect the format(s) used (e.g., `Month YYYY`, `MM/YYYY`, `YYYY only`).
3. Check for **mixed formats** within the same document (e.g., `Jan 2020` in one entry and `03/2021` in another).
4. Flag any entries using year-only dates or missing months — these reduce ATS accuracy for tenure calculations.

### ATS-compatible date formats (ranked)

| Format | Example | ATS compatibility |
|---|---|---|
| Full month name + year | `January 2020 – March 2023` | Best |
| Abbreviated month + year | `Jan 2020 – Mar 2023` | Excellent |
| MM/YYYY | `01/2020 – 03/2023` | Good |
| Year only | `2020 – 2023` | Poor — ATS may miscount tenure |
| Mixed formats | `Jan 2020` in one entry, `03/2021` in another | Poor — inconsistency causes parsing errors |

### Date consistency scoring scale

| Score | Criteria |
|---|---|
| 85–100 | All dates present; single consistent format; months included throughout |
| 70–84 | All dates present; minor format inconsistency (e.g., one entry differs) |
| 50–69 | Dates present but mixed formats, or some months missing |
| 30–49 | Significant date gaps; multiple format types; year-only dates used |
| 0–29 | Dates largely absent or completely inconsistent across the resume |

---

> The report output template is available at [`OUTPUT-TEMPLATE.md`](OUTPUT-TEMPLATE.md).
