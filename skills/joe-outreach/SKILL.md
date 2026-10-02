---
name: joe-outreach
description: Automated daily lead generation, email permuting (first.last, f.last, etc.), deduplication ledger, and outreach for Joseph Heupler with resume attachment.
---

# Joe Outreach & Recruiter Sourcing Skill (`joe-outreach`)

Automates discovering prospective engineering leads/recruiters, permuting company email patterns, verifying against contact history to prevent double-contact, and sending tailored referral pitches for Joseph Heupler with his resume attached.

## 1. Candidate Context
- **Candidate:** Joseph Heupler (`jheupler@berkeley.edu`)
- **LinkedIn:** `https://www.linkedin.com/in/joseph-heupler/` | **Portfolio:** `josephheupler.com`
- **Education:** UC Berkeley (Data Science & Cognitive Science)
- **Strengths:** Production AI Agents (LangGraph, GraphRAG with 96% grounded eval), Data Platform (dbt/Airflow, 100k+ invoices), Full Stack (Python, TypeScript, React, FastAPI).
- **Resume Path:** `/Users/mlubich/dev/resumes/resumes/resume_joseph_heupler/resume_joseph_heupler.pdf`

## 2. Hard Safeguards & Exclusions
- **NEVER CONTACT:** Perry Barrow (W3Sourcing).
- **NEVER REFER TO JOE (Kept for Misha):**
  - **Mach**
  - **Anduril**
  - **EchoStar / Dish**
- **Strict Deduplication:**
  - Before emailing or drafting, query the ledger (`~/.config/joe-referral/ledger.json`) and Mail.app's sent mailbox.
  - If a person or company email was contacted in the past 90 days, **SKIP**.

## 3. Email Permutation Patterns
When sourcing a lead with name `First Last` and company domain `example.com`:
- `first.last@example.com` (e.g., `john.doe@acme.com`)
- `flast@example.com` (e.g., `jdoe@acme.com`)
- `first@example.com`
- `firstl@example.com`
- `last.first@example.com`

Verify MX records or SMTP availability before sending, or prioritize verified recruiter addresses found via scraping/inbound.

## 4. Run it with refer.py (the tool, not a scratchpad)
`refer.py` next to this file does the email side through imail. Run it with imail's python:
`PY=~/.local/share/uv/tools/imail-mcp/bin/python`.

**Inbound (route recruiter job emails to Joe):**
1. `$PY refer.py scan --account michaelle.lubich@gmail.com --limit 60 > cands.json`
   (unreplied, sender not in the ledger, no excluded company; includes the body).
2. Agent reads each one. Refer only **real job opportunities where Joe fits** (AI/ML, data, python,
   full stack python/ts/react, FDE). Skip notifications, events, sales, Java-only, pure front-end,
   Go/K8s-heavy roles. One reply per agency per role (two recruiters from one agency pitching the same role → reply to one).
   Skip if the company is already in the ledger (a coworker was contacted) or Joe was already referred to that person on LinkedIn.
3. Write `~/.config/joe-referral/queue.json`: `[{name, email, company, role, subject: "Re: <their subject>", body}]`.
   The body is 3-4 sentences personalized to their role, ending with the ask to reach Joe at jheupler@berkeley.edu (cc'd).
   The script adds "resume attached, more at josephheupler.com. misha".
4. `$PY refer.py send ~/.config/joe-referral/queue.json`. It sends from michaelle.lubich@gmail.com, CCs Joe,
   attaches his resume, logs each send to the ledger as it goes, and empties the queue.

**No outbound job scanning.** Joe is only referred to people who already messaged Misha (email or LinkedIn inbox). Do not search job boards or LinkedIn Jobs, and do not collect job IDs or hiring-team names.

**After sending:** check `[Gmail]/Sent Mail` for the subjects, and look for bounces in the inbox
(`Undeliverable` / `Delivery Status Notification`). Bounced addresses stay in the ledger so they are never retried.
First run 2026-09-26: `first@` bounced at egnitehr.com and praecisai.com.

## 5. Legacy workflow notes
1. Check new inbound or scraped leads from job portals (Dice, LinkedIn, Indeed).
2. Filter out all exclusions (Mach, Anduril, EchoStar/Dish, Perry Barrow).
3. Generate concise, humanized referral pitch (3-4 sentences max, no em dashes, light casual punctuation).
4. Send or draft via `imail` CLI using `--body-file` and attaching Joe's resume:
   ```bash
   imail send --from michaelle.lubich@gmail.com --to <recruiter> --cc jheupler@berkeley.edu --subject "<subject>" --body-file /tmp/pitch.txt --attach /Users/mlubich/dev/resumes/resumes/resume_joseph_heupler/resume_joseph_heupler.pdf --no-markdown
   ```
5. Record entry in `~/.config/joe-referral/ledger.json`.
