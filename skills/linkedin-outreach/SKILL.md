---
name: linkedin-outreach
description: Scan LinkedIn recruiter messages, auto-classify incoming inquiries, and draft professional, un-embarrassing human replies with attached matching resume PDFs.
---

# LinkedIn Outreach & Recruiter Reply Skill (`linkedin-outreach`)

Automates scanning LinkedIn DMs and drafting clean, professional responses to recruiters and hiring managers without cringe or awkward automated phrasing.

## 1. Outreach Principles

- **Tone**: Professional, concise, polite, direct (2-3 sentences max).
- **No Hyped AI Phrasing**: Plain English matching candidate preferences (US Citizen, W-2, SF Bay Area / Remote / Hybrid).
- **Targeted Resume Attachment**:
  - AI / LLM Engineering inquiries -> `resumes/resume_mlubich_ai/resume_mlubich_ai.pdf`
  - Forward Deployed / Field roles -> `resumes/resume_mlubich_fde/resume_mlubich_fde.pdf`
  - Federal / Gov / Regulated roles -> `resumes/resume_mlubich_gov/resume_mlubich_gov.pdf`
  - Platform / SWE roles -> `resumes/resume_mlubich_swe/resume_mlubich_swe.pdf`

## 2. Execution Workflow

1. Retrieve LinkedIn login from macOS Keychain (email: `michaelle.lubich@gmail.com`).
2. Open LinkedIn Messaging:
   ```bash
   agent-browser open --headed "https://www.linkedin.com/messaging/"
   ```
3. Scan unread threads and extract recruiter inquiry details (Company, Role, Location, Tech Stack).
4. Build appropriate matching resume PDF:
   ```bash
   ./build.sh build <variant>
   ```
5. Draft humanized response & present to user for approval or auto-send upon request.

## 3. Referral Policy — Joseph Heupler (applies to LinkedIn DMs *and* recruiter email)

Default for any inbound recruiter/agency message: **refer Joseph Heupler**, unless the
exclusion list below says otherwise. Referral, not application — Misha stays out of the loop
on those roles.

Joe's details:
- `jheupler@berkeley.edu` · `linkedin.com/in/joseph-heupler` · `josephheupler.com`
- Resume — always this one file, no variant matching:
  `/Users/mlubich/dev/resumes/resumes/resume_joseph_heupler/resume_joseph_heupler.pdf`
  (AI / ML Engineer: production agents, GraphRAG, LangGraph, evals, data platform).
  Attach it as `resume_joseph_heupler.pdf`. On LinkedIn, where attaching is awkward, paste his
  email and site and say the resume is on the way / available.

### Writing the referral message
- **3-5 sentences, hard max.** Short enough to read on a phone.
- **Personalized per person.** Name the recruiter, their company, and the actual role they
  pitched. Never a template blast; two recruiters must never get the same message.
- **Sound like a person typed it.** Plain English, light punctuation, casual lower-case is
  fine. No em dashes, no markdown, no corporate filler, no AI-hype words.
- **Lead with what Joe brings *their* business**, tailored to the role they described — e.g.
  support AI that cites its sources and keeps a human in the loop, agents behind deterministic
  guardrails, eval sets before anything ships, reporting that cut reconciliation 70% across
  100K+ invoices, quality analytics that cut replacements 18-32%.
- **Explicitly encourage them to reach out to Joe directly**, and say plainly that he is a
  strong candidate. Give the email; the ask is that they contact him.
- Be honest about the frame: this is Misha passing along someone he rates, not Misha applying.

### Do NOT refer — these stay Misha's
- **Mach**
- **Anduril**
- **EchoStar / Dish** (Misha's own employer since 2026-09-21)

Everything else is fair game. Enforced by the `EXCL` regex in `scan.py` (next to this file).

### Never contact
- **Perry Barrow** (W3Sourcing). No reply, no referral, no follow-up. Leave the thread alone
  and note it in the summary.

### Existing threads
If there is already a conversation with that recruiter, make the referral **in that thread**.
Do not open a new message or a new email chain for someone already talked to.

### Who gets a referral (hard rules, from Misha 2026-09-24)
The referee is Joe by default but can be someone else (Misha will name them). Swap the name,
email, links and pitch; the rules below stay the same.
- **Only people who reached out to Misha** and whose **last message has no reply yet**.
  Unread threads first.
- **Only real job opportunities.** Skip sales pitches (vendors, "are you experiencing X"),
  networking hellos, shared posts, scams (wrong name, generic Calendly bait).
- **Never double reply.** Skip any thread that already mentions the referee, and any thread where
  Misha's message is the last one. One referral per thread, ever.
- **Stay out of Misha's own live searches**: threads where he is booking calls, sent his resume,
  or asked them to apply for him. Those are his.
- Threads the recruiter already closed ("okay thanks", "same to you" after a no) get nothing.

### How to run it
Use the CLI; the full command flow lives in the `linkedin` skill (`~/.claude/skills/linkedin/SKILL.md`).
Never hand-write browser code for this.
1. `li login` (if signed out), then `li scan` -> compact JSON of candidates `{name,url,unread,text,fit}`.
2. Read each candidate and sort it: job, sales, or Misha's own. Write one personalized message per job
   into `queue.json` (`name`, `profile_url` or `thread_url`, `company`, `role`, `body`).
3. `li referral queue queue.json` (dry run), then `li referral queue queue.json --confirm`: opens each
   thread by URL, sends the body then `resume_joseph_heupler.pdf`, verifies both landed once, and writes
   the ledger (`~/.config/joe-referral/ledger.json`). Report sent / skipped with reasons.
(`li` can be shadowed by own-chrome's `li` in a venv; `linkedin` is the same CLI and always ours.)
