---
name: imail
description: Send email and look up contacts on this Mac via the user's own `imail` tool (a.k.a. mail-mcp / mcp-apple-mail) — driving Apple Mail.app directly, no IMAP. Use whenever a task means sending an email, drafting one, listing/triaging the inbox, or resolving a person's email address from Contacts. Triggers include "email X", "send a mail", "cc so-and-so", "check my inbox", "what's <person>'s email", or filing something to a helpdesk by email.
---

# imail — Apple Mail from the CLI (and MCP)

The user built `imail` (package `mac-imail`). It drives **Apple Mail.app** locally — no IMAP, no himalaya. Same tool is exposed two ways; prefer the CLI for one-shot actions:

- **CLI:** `imail` → `~/.local/bin/imail`
- **MCP server:** `mcp-apple-mail` (a.k.a. "mail-mcp") → `~/.local/share/uv/tools/mcp-apple-mail/bin/mcp-apple-mail`.

## 1. Sanity Check & Account Walls
```sh
imail doctor      # -> "ok: Mail.app reachable" + lists accounts
imail accounts    # valid --from addresses (the "walls")
```
Known walls on this Mac:
- **Personal:** `michaelle.lubich@gmail.com`, `metropol007@gmail.com`, `misha@lupfr.com`

No employer account is configured. Run `imail accounts` for the live list. If a
work account is added later, treat it as its own wall and never mix it with personal.

## 2. Human Writing & Outreach Rules for Agents
When sending or drafting emails via `imail`:
- **Reply Wall Integrity**: When replying, ALWAYS send from the exact account/address that received the email. Never cross work/personal walls.
- **Full Thread Review**: Always read/inspect the full email thread history before writing a reply to prevent duplicating information or conflicting statements.
- **Attachment Inspection**: Read and analyze attachment content (e.g. resumes, job descriptions, PDFs) before sending to ensure complete alignment with the topic/role.
- **Markdown HTML Default**: `--markdown` is ON by default. All emails render with 100% uniform Gmail Sans Serif (`Arial, Helvetica, sans-serif`, 14px, `#222222`).
- **Lowercased Subject Lines**: All initiated email subjects must be lowercase by default (e.g. `senior full stack & infrastructure engineer opportunity`).
- **NO Subject Title Headings in Body**: NEVER put `# Subject` or `<h1>Subject</h1>` title headers inside the email body text. Start directly with the greeting (`Hi Michaelle,`).
- **NO Emojis**: Emojis are strictly prohibited in email subject lines or body text for outreach/replies.
- **Quotes `" "` Over Backticks `` ` ``**: Use quotes `"filename.pdf"` instead of code backticks `` `filename.pdf` `` when referencing files or terms.
- **No Random Bolding**: Avoid random bolding (`**text**`) inside email bodies. Keep text clean and unbolded.
- **Prefer PDF Attachments**: Prefer attaching `.pdf` documents (resumes, job descriptions, portfolios) rather than raw `.md` files when emailing contacts/recruiters.
- **Short, Brief & Sweet**: Keep email body text brief, polite, and to the point. Max 1–2 exclamation marks per email.
- **Natural Human Sign-offs**: NO `Best regards` or `Best`. Use natural sign-offs (`Thanks,`, `Talk soon,`, `Cheers,`, `Thank you!`, `Looking forward to our call!`, `Sincerely,`).
- **Human Touch (`-H` / `--humanize`)**: Use `-H` / `--humanize` for subtle natural human casing/punctuation variations (inspired by `blader/humanizer`).
- **Misha voice (autodraft / agent drafts):** lowercase, short, no analogies, no markdown, no em dashes. Sign off `thanks,` / `misha`. Scheduled job is `brain reply` → `imail autodraft`, not a second launchd control plane.

## 2b. Autodraft (auto-reply agent, via brain)

Runs 08:00, 14:00, 19:00 as launchd `com.mlubich.brain-reply` -> `brain reply` -> `imail autodraft`.

```sh
imail autodraft --dry --limit 25   # preview decisions, no side effects
imail autodraft-eval                # run labeled cases through the real model; non-zero exit on any unsafe send
imail autodraft-log -n 20           # what it did: sent / drafted / skipped / error, with confidence + reason
brain reply --dry
```

Pipeline per inbox message (accounts: `michaelle.lubich@gmail.com`, `metropol007@gmail.com`; **never `misha@lupfr.com`**):
1. Regex prefilter (noreply, newsletters, receipts, alerts, staffing blasts) -> skipped without an LLM call.
2. Skip if already replied to or already seen.
3. `brain recall "<sender> <subject>"` -> context. Email body is framed as UNTRUSTED data in the prompt.
4. LLM: OpenAI `gpt-5-nano` (minimal reasoning; key = keychain item `OPENAI_API_KEY` or env), fallback `claude -p` haiku with `--system-prompt` + no tools. Returns JSON.
5. `validate_decision` fails closed: wrong types (`"false"`, `"0.99"`, `"LOW"`) -> error, not seen, retried next run.
6. Auto-SEND only if all: confidence >= 0.95, stakes low, sender (real address via `parseaddr`) in Contacts, reply <= 400 chars, no incoming attachments, not recruiter. Everything else -> unsent Mail.app draft (syncs to phone; Misha sends).
7. Facts stated in the email -> `brain learn` (flag-like strings dropped). Every decision -> `~/.config/imail/autodraft-log.jsonl`.

Config: `~/.config/imail/accounts.json` -> `autodraft` block (accounts list excludes lupfr on purpose; owner/sign-off; resume_dir + variants). Without `autodraft.accounts` it falls back to `walls.personal.emails`, which INCLUDES lupfr — never remove that key.

Do not loosen step 6 or 5 without Misha explicitly asking. Source: `~/dev/imail-mcp` (github ml-lubich/imail-mcp, public: no personal data in fixtures).

## 3. Send Email
```sh
imail send \
  --from "michaelle.lubich@gmail.com" \
  --to   "someone@example.com" \
  --subject "senior full stack engineer opportunity" \
  --body-file "/path/to/letter.md" \
  --attach "/path/to/resume.pdf" \
  -m \
  -H \
  -o
```

Flags:
- `-m` / `--markdown`: Convert markdown to clean, uniform Gmail-style Sans Serif HTML.
- `-H` / `--humanize`: Lowercase subject line, strip emojis, apply subtle human casing/punctuation touch (no gross misspellings).
- `-a` / `--attach`: Path to file attachment (repeatable for multiple files).
- `--zip`: Bundle multiple attachments into a single `.zip` archive.
- `-o` / `--open`: Launch native unsent WebKit `.eml` draft in Mail.app for review before sending.

## 4. Look up a contact's email (Contacts.app)
Query Contacts.app via AppleScript by writing a temporary script file:
```sh
cat > /tmp/find_contact.applescript <<'APPLESCRIPT'
tell application "Contacts"
  set out to ""
  repeat with p in (every person)
    set nm to name of p
    repeat with e in (emails of p)
      set ev to (value of e) as string
      if nm contains "SEARCH" or ev contains "SEARCH" then
        set out to out & nm & " | " & ev & linefeed
      end if
    end repeat
  end repeat
  return out
end tell
APPLESCRIPT
osascript /tmp/find_contact.applescript
```
Replace `SEARCH` with the contact name/domain.
