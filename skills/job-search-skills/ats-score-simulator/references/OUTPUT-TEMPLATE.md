---
name: OUTPUT-TEMPLATE.md
description: Report output template for the ats-score-simulator skill. Defines the exact structure of the ATS Score Simulation Report that the agent must produce in Step 6.
last-updated: 2026-03-17
---

# Output Template — ATS Score Simulation Report

Use the following template to structure the final report. Replace all `[PLACEHOLDER]` values with actual findings.

---

```markdown
# ATS Score Simulation Report

**Resume:** [filename or description]
**Job Title:** [job title extracted from job description]
**Date:** [today's date YYYY-MM-DD]

---

## Knockout Check

> Binary disqualifiers are processed before resume content is scored. Failing any of these in a real ATS typically causes automatic rejection, regardless of the overall match score.

| Criterion | Requirement (from job description) | Resume evidence | Status |
|---|---|---|---|
| [e.g. Work authorisation] | [exact text from JD] | [what the resume says, or "Not stated"] | ✅ Met / ❌ Not met / ⚠️ Unclear |

[If no knockout criteria were found, replace the table with: "No binary knockout criteria identified in this job description."]

---

## Overall ATS Compatibility Score

> **[SCORE]% — [🟢 Strong match / 🟡 Moderate match / 🟠 Weak match / 🔴 Very poor match]**

[One sentence interpreting the score and what it means for the candidate's chances of passing ATS filters.]

| Dimension | Raw Score (0–100) | Weight | Weighted Score |
|---|---|---|---|
| Keyword Match | [X]/100 | 35% | [X × 0.35] |
| Experience Tenure | [X]/100 | 27% | [X × 0.27] |
| Education & Qualifications | [X]/100 | 18% | [X × 0.18] |
| Formatting & Completeness | [X]/100 | 10% | [X × 0.10] |
| Contact Information | [X]/100 | 5% | [X × 0.05] |
| Date Consistency | [X]/100 | 5% | [X × 0.05] |
| **Overall** | — | 100% | **[TOTAL]/100** |

---

## Keyword Analysis

### Keywords Found (present in resume)

| Keyword | Category | Density | Placement quality |
|---|---|---|---|
| [keyword] | [Hard skill / Certification / etc.] | [X%] | [Optimal / Low / Stuffed] |

### Keywords Missing (in job description but absent from resume)

| Keyword | Category | Priority |
|---|---|---|
| [keyword] | [Hard skill / Certification / etc.] | [Critical / High / Medium] |

### Keyword Summary

- Total keywords extracted from job description: [N]
- Found in resume: [N] ([X%])
- Partially matched: [N]
- Missing: [N] ([X%])

---

## Experience Tenure Analysis

- **Required experience (from job description):** [X years / X–Y years]
- **Candidate's total relevant experience:** [X years]
- **Gap:** [None / +X years above max / -X years below minimum]
- **Date format consistency:** [Consistent / Inconsistent — describe issues]

[2–3 sentences summarizing the experience match and any risks.]

---

## Education & Qualifications Analysis

- **Required degree:** [degree level and field, or "not specified"]
- **Candidate's degree:** [degree, field, institution]
- **Match:** [Exact / Exceeds / Adjacent field / Below requirement / Not met]
- **Required certifications:** [list, or "none stated"]
- **Candidate's certifications:** [list, or "none found"]

[2–3 sentences summarizing the education match.]

---

## Formatting & Completeness Analysis

### Risk Factors Identified

| Risk factor | Severity | Recommendation |
|---|---|---|
| [risk] | [High / Medium / Low] | [fix] |

### Standard Sections Check

| Section | Present | Heading used |
|---|---|---|
| Summary/Objective | [Yes / No] | [heading text] |
| Experience | [Yes / No] | [heading text] |
| Education | [Yes / No] | [heading text] |
| Skills | [Yes / No] | [heading text] |
| Certifications | [Yes / No / N/A] | [heading text] |

[2–3 sentences summarizing formatting quality and ATS parseability.]

---

## Contact Information Analysis

| Field | Detected | Location | Risk |
|---|---|---|---|
| Email address | [Yes / No] | [Body / Header-footer / Image / Not found] | [None / Medium / High] |
| Phone number | [Yes / No] | [Body / Header-footer / Image / Not found] | [None / Medium / High] |
| Location | [Yes / No] | [Body / Header-footer / Image / Not found] | [None / Medium / High] |

[1–2 sentences summarizing contact info completeness and any parsing risks.]

---

## Date Consistency Analysis

- **Formats detected:** [list format types found, e.g., "Month YYYY, MM/YYYY"]
- **Consistency:** [Consistent / Mixed — describe]
- **Missing months:** [None / Yes — list affected entries]
- **Year-only dates:** [None / Yes — list affected entries]

[1–2 sentences summarizing date formatting quality and impact on ATS tenure calculation.]

---

## Improvement Plan

Prioritized actions to raise the ATS score. Address Critical items first.

### Critical (must fix — major score impact)

- [ ] [Specific action, e.g., "Add 'stakeholder management' to the Professional Summary and at least two bullet points in the Experience section."]

### High Priority (fix before applying)

- [ ] [Specific action]

### Medium Priority (improves score further)

- [ ] [Specific action]

### Low Priority (polish)

- [ ] [Specific action]

---

## Estimated Score After Improvements

If all Critical and High Priority items are addressed, the estimated new score range is:
**[RANGE]%** — [brief rationale]
```
