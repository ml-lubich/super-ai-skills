---
name: recruiter-reply
description: Automated recruiter email triage, resume variant matching, and unsent draft creation in Apple Mail via imail / apple-mail MCP.
---

# Recruiter Reply & Resume Matching Skill

Use this skill whenever triaging incoming recruiter outreach, contract agency emails, or job inquiries in Apple Mail.

## Workflow & Guidelines

### 1. Verification & Anti-Duplicate Check
- Inspect `INBOX` across personal accounts (`michaelle.lubich@gmail.com`, `metropol007@gmail.com`, `misha@lupfr.com`, `mishalubich@berkeley.edu`).
- **Always verify Sent Messages** before drafting to ensure an email has not already been replied to in a previous session.

### 2. Resume Selection & Suffix Removal
- Match the job requirements (AI/ML, Full Stack, SWE, Infrastructure/MLOps, FDE) against compiled resumes under `/Users/mlubich/dev/resumes/resumes/`.
- **Clean Suffix Removal (Mandatory):** Never attach files with internal variant names (e.g. `_ai`, `_swe`, `_infra`, `_fullstack_ai`, `_fde`, `_echostart`). Copy the matched PDF to a clean path (e.g. `~/tmp/resumes_clean/<variant>/resume_mlubich.pdf`) so the attachment name presented to recruiters is strictly `resume_mlubich.pdf`.

### 3. Draft Tone & Style
- **Warm human email style:** Write concise, polite, direct responses like a human typed them on a mobile phone or keyboard.
- **Punctuation & Formatting:** Casual lower-case and light punctuation are encouraged. No markdown, no analogies, no em dashes. Hourly drafts come from `brain reply` / `imail autodraft`.
- **Hard Exclusions:**
  - **No em dashes** (`—` or `--`).
  - **No corporate clichés** or vague filler phrases.
- **Answer Recruiter Questions:** Directly address any questions in their email (US Citizenship, work authorization, remote/onsite availability, rate/comp expectations, start dates).

### 4. Background Execution & Window Protection (Mandatory)
- **Use `imail` CLI:** Always use `imail send` or `imail draft` with `--body-file` for 100% background, headless execution.
- **No GUI Windows or Popups:** Never run AppleScript with `{visible: true}` or `open -a Mail` which creates compose windows in front of the user's screen or triggers modal save alerts.
- **Body File Usage:** Pass `--body-file /tmp/body_text.txt` when passing multi-line or long bodies to prevent string path stat errors in python.

### 5. Chat Output Requirement
- Always print a summary of all created drafts in the final chat response, including:
  - Recipient email and name
  - Email subject line
  - Matched resume variant used
  - Exact draft body text

### 6. Referral Policy
Who gets referred to Joseph Heupler, who stays Misha's (AMD/Uri, EchoStar, agentic-workflow and
intent-recognition roles), and who is never contacted (Perry Barrow): see the **Referral Policy**
section of the `linkedin-outreach` skill. It is the single source of truth for both channels.
