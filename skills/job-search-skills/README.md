# Job Related Skills

Skills related to job search, job applications, resume analysis, cover letter writing, and so on.

## Prerequisites (generic skills)

Job-search skills assume these **generic skills** are available (see [generic-skills](../generic-skills/)):

| Skill | Description |
| ----- | ----------- |
| [read-pdf-document](../generic-skills/read-pdf-document.md) | Read a PDF and extract text. |
| [txt-to-markdown](../generic-skills/txt-to-markdown.md) | Convert text to Markdown. |

**Important:** If a required sub-skill is not available, the skill **must** return an error and ask the user to install that skill before trying again.

## Skills in this library

| Skill | Description |
| ----- | ----------- |
| [Resume Analyst](resume-analyst/SKILL.md) | Analyzes a resume (PDF) and produces a structured assessment: sentiment, skills/experience inventory, strengths, weaknesses, achievements, recruiter questions and concerns. |
| [01- ATS Score Simulator](./ats-score-simulator.md) | ATS compatibility score of a resume vs. a job description (keywords, experience, formatting). |
| [02 -Fix identified ATS Issues](./fix-identified-ats-issues.md) | Produces a concrete fix guide (Before/After/Rationale) from ATS findings. |
| COMING SOON [03 -Draft Cover Letter](./draft-cover-letter.md) | Creates a tailored, ATS-friendly cover letter from resume + job description; uses evaluate-cover-letter to refine. |
| COMING SOON [04 -Evaluate Cover Letter](./04-evaluate-cover-letter.md) | Scores a cover letter (0–100) on six dimensions and produces an improvement plan. |
