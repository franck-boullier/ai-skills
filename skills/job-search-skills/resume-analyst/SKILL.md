---
name: resume-analyst
description: Analyzes a person's resume (PDF) and produces a structured assessment covering sentiment, skills and experience inventory, strengths, weaknesses, notable achievements, recruiter questions, and recruiter concerns. Use when the user wants to evaluate, review, score, or get feedback on a resume or CV, or when the user asks what a recruiter might think about someone's profile.
compatibility: Requires Python and pdfplumber (via the read-pdf-document sub-skill)
metadata:
  author: franck-boullier
  version: "1.1"
---

# Resume Analyst

Produces a structured, multi-section assessment of a resume from a PDF file.

## Prerequisite: check for the `read-pdf-document` skill

Before doing anything else, verify the `read-pdf-document` skill is available by checking whether the file `../read-pdf-document/SKILL.md` exists **relative to this skill's directory**.

- If the file **does not exist**, stop immediately and return this error to the user:

  > **Error**: The `resume-analyst` skill requires the `read-pdf-document` skill, which was not found.
  > Please install the `read-pdf-document` skill in the same skills directory before running this skill again.

- If the file **exists**, read it and follow its instructions to extract the resume text.

## Workflow

```
Task Progress:
- [ ] Step 0: Collect PDF input
- [ ] Step 1: Verify read-pdf-document skill is installed
- [ ] Step 2: Extract full text from the resume PDF
- [ ] Step 3: Analyse the extracted text
- [ ] Step 4: Produce the structured report
```

### Step 0 — Collect PDF input

If the user has not already provided a PDF resume file, stop and ask:

> "Please provide the resume PDF file you would like me to analyse."

**Wait for the user to supply the file before proceeding to Step 1.**

### Step 1 — Verify dependency

Check for `../read-pdf-document/SKILL.md` relative to this skill's location. Error out if missing (see above).

### Step 2 — Extract resume text

Read the `read-pdf-document` skill and follow its instructions to extract all text from the supplied PDF file. That skill handles layout-preserving extraction and OCR fallback for scanned documents automatically.

If the extracted text is empty, stop and apply the edge-case guidance in the **Edge Cases** section below.

### Step 3 — Analyse the resume

With the extracted text, perform the following analysis:

| Section                  | What to assess                                                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Sentiment**            | Overall tone (positive/neutral/negative), confidence level, assertiveness, professional register, use of action verbs vs passive language |
| **Skills & Experience**  | Hard skills, soft skills, tools/technologies, years of experience per domain, industries/roles covered                                    |
| **Strengths**            | Areas where the candidate clearly excels or has strong evidence to back claims                                                            |
| **Weaknesses**           | Gaps, vague claims, inconsistencies, missing information, potential red flags                                                             |
| **Notable Achievements** | Quantified results, awards, promotions, unique contributions that differentiate the candidate                                             |
| **Recruiter Questions**  | Questions a recruiter would likely probe during a screening call, based on gaps or interesting points                                     |
| **Recruiter Concerns**   | Concerns a recruiter might flag: gaps in employment, short tenures, missing skills for typical roles, etc.                                |

### Step 4 — Produce the report

Format the output using the template in [references/OUTPUT-TEMPLATE.md](references/OUTPUT-TEMPLATE.md).

## Edge Cases

| Scenario | How to handle |
| -------- | ------------- |
| **Empty or unreadable PDF** (no text extracted after OCR fallback) | Stop immediately. Return: "No text could be extracted from the provided PDF. The file may be corrupted, password-protected, or contain only images without OCR support. Please provide a different file." |
| **Very short resume** (fewer than ~200 words of extracted text) | Proceed with analysis but add a note in the report header: "The extracted resume content is unusually sparse. Some sections may have limited findings." |
| **Non-English resume** | Add a note at the top of the report that the resume appears to be in a language other than English. If the content is intelligible, proceed. If not, ask the user whether to continue. |

## Guidelines

- Be **specific**: quote or paraphrase evidence from the resume to support every point.
- Be **balanced**: list both genuine strengths and real weaknesses — avoid being sycophantic.
- Keep each section **focused**: 3–7 bullet points per section is usually right; use more only when clearly warranted.
- For the **Recruiter Questions** section, phrase each item as a direct question a recruiter would say out loud.
- For the **Recruiter Concerns** section, phrase each item as a concern statement, not a question.
- If a section has nothing meaningful to report (e.g. no notable achievements found), say so explicitly — do not fabricate.
