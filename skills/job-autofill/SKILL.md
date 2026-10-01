---
name: job-autofill
description: Automate job applications across ATS portals (Workday, Ashby, Greenhouse, Lever, USAJOBS) with tailored resume matching, AI application answers, and multi-tier anti-bot evasion (CDP, headed browser, cua-driver).
---

# Job Application Auto-Fill Skill (`job-autofill`)

Multi-platform skill for AI agents (Claude, Cursor, Gemini, Codex) to automate job application form filling and submission across Workday, Ashby, Greenhouse, Lever, and Federal job portals.

## 1. Skill Capabilities & Architecture

- **ATS Engines**:
  - **Workday**: Account creation / sign-in (`MishaGuidewire!007` pattern), 5-step wizard navigation, resume upload, EEO options, candidate portal tracking.
  - **Ashby**: Single-page form submission, resume autofill, human keypress emulation, `cua-driver` desktop GUI fallback for anti-bot bypass.
  - **Greenhouse / Lever**: Fast single-page field mapping, file upload, custom essay response injection.
  - **USAJOBS / Federal**: Multi-page federal form completion using 2-page detailed resumes (`resume_mlubich_gov.pdf`).

- **Resume Variant Auto-Selection**:
  - AI / LLM / Prompt Engineering -> `resumes/resume_mlubich_ai/resume_mlubich_ai.pdf`
  - Forward Deployed Engineer -> `resumes/resume_mlubich_fde/resume_mlubich_fde.pdf`
  - Federal / Government / Public Sector -> `resumes/resume_mlubich_gov/resume_mlubich_gov.pdf`
  - Defense Tech / Aerospace -> `resumes/resume_mlubich_defense/resume_mlubich_defense.pdf`
  - Regulated Enterprise / High Reliability -> `resumes/resume_mlubich_regulated/resume_mlubich_regulated.pdf`
  - General SWE / Microservices / Backend -> `resumes/resume_mlubich_swe/resume_mlubich_swe.pdf`

## 2. Execution Escalation Ladder

```
Level 1: agent-browser (Fast CDP CLI)
   │
   ├── [Anti-Bot Flagged?] ──► Level 2: agent-browser --headed + keystroke typing
   │
   └── [Captcha / Cloudflare Blocked?] ──► Level 3: cua-driver (Native macOS Desktop GUI)
```

## 3. Workflow Steps

1. **Build Resume PDF**: Run `./build.sh build <variant>` in candidate resume workspace to ensure latest compiled PDF.
2. **Open Portal**: `agent-browser open "<job_url>"` (or `agent-browser --headed open "<job_url>"`).
3. **Parse & Map Fields**:
   - `First Name`, `Last Name`: Michael Lubich
   - `Email`: michaelle.lubich@gmail.com
   - `Phone`: 4152750094 / (415) 275-0094
   - `Location`: San Francisco, CA 94102
   - `LinkedIn`: https://www.linkedin.com/in/misha-lubich/
   - `GitHub`: https://github.com/ml-lubich
   - `Work Authorization`: U.S. Citizen (No sponsorship required)
4. **Generate AI Application Responses**:
   - Use LLM prompt based on candidate's `resume.yaml` and target job posting requirements.
5. **Upload Resume**: `agent-browser upload "input[type='file']" <pdf_path>`.
6. **EEO Disclosures**: Male, White (Not Hispanic or Latino), Not a Veteran, Agree to Terms.
7. **Submit & Verify**: Verify confirmation screen ("Application Submitted" / "Application Received").

## 4. Verification Gate (TDD)
Before declaring an application complete:
1. Re-snapshot browser DOM (`agent-browser snapshot -i`).
2. Verify explicit confirmation text ("Application Submitted" or "Application Received").
3. Record Job Title, Req ID, and Submission Date in candidate log.
