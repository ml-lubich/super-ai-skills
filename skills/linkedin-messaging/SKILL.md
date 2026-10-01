---
name: linkedin-messaging
description: >
  Send, search, and manage LinkedIn messages via browser automation (agent-browser).
  Use when replying to recruiters or contacts on LinkedIn, searching message threads,
  attaching files (resumes, PDFs), or reading unread conversations. Triggers include:
  "reply to X on LinkedIn", "send a LinkedIn message", "check LinkedIn messages",
  "search LinkedIn DMs", "attach resume on LinkedIn", or any task requiring
  programmatic LinkedIn messaging interaction.
---

# LinkedIn Messaging Skill

Drive LinkedIn Messaging entirely through `agent-browser` (headless Chrome via CDP).
Never use the LinkedIn API or unofficial scraper — browser automation only.

## Credentials

Never hardcode. Always retrieve from macOS Keychain at runtime (see `keychain` skill):

```bash
LI_EMAIL="michaelle.lubich@gmail.com"
LI_PASS=$(security find-internet-password -s "linkedin.com" -a "michaelle.lubich@gmail.com" -w)
```

> **2FA Note:** LinkedIn may request 2FA via the mobile app ("Check your LinkedIn app") after
> login from a new browser session. If this appears, ask the user to approve the push
> notification, then continue after approval.

---

## Workflow

### 1. Open LinkedIn Messaging

```bash
agent-browser open --headed "https://www.linkedin.com/messaging/"
```

If redirected to login page (`/uas/login`), log in first:

```bash
agent-browser fill @e19 "michaelle.lubich@gmail.com"
agent-browser fill @e20 "$(security find-internet-password -s 'linkedin.com' -a 'michaelle.lubich@gmail.com' -w)"
agent-browser click @e14   # "Sign in" button
```

After login, wait ~3-4s and take a snapshot to confirm landing page.

---

### 2. Find a Conversation Thread

Use `agent-browser eval` to search by name if not visible in sidebar:

```bash
agent-browser eval "document.querySelector('[aria-label*=\"Tom Calver\"]')?.click()"
```

Or visually identify the conversation in the snapshot and click its `ref`:

```bash
agent-browser snapshot -i   # look for heading "Tom Calver" ref
agent-browser click @eXX    # click conversation
```

---

### 3. Read Message History

After selecting a thread:

```bash
agent-browser snapshot -i
```

Look for `generic` nodes containing message content (identified as `Misha Lubich` or the
contact name). Message content is visible in the `aria-label` or text of `generic` refs.

---

### 4. Write & Fill a Reply

Identify the message textbox (`textbox "Write a message…"`) from snapshot, then fill it:

```bash
agent-browser fill @eXXX "Your reply text here"
```

For long multi-line messages, use `agent-browser eval` with `innerHTML` injection or
`execCommand('insertText', false, text)` into the focused contenteditable:

```bash
agent-browser eval "
  const box = document.querySelector('.msg-form__contenteditable');
  box.focus();
  document.execCommand('insertText', false, 'Your message here');
"
```

---

### 5. Attach a File (PDF Resume)

LinkedIn's file upload button wraps a hidden `<input type="file">`. Do NOT click the
visible paperclip button — use `DOM.setFileInputFiles` directly via `agent-browser upload`:

```bash
# First confirm the hidden input exists:
agent-browser eval "document.querySelector('input[type=\"file\"]')?.id"

# Upload using CSS selector:
agent-browser upload "input[type='file']" "/Users/mlubich/dev/resumes/resumes/<variant>/<file>.pdf"
```

**Clean filename rule (same as `recruiter-reply`):** Never deliver files with internal
variant suffixes to recruiters. Copy to a clean path first:

```bash
cp /Users/mlubich/dev/resumes/resumes/resume_mlubich_staff_ai/resume_mlubich_staff_ai.pdf \
   /tmp/resume_mlubich.pdf
agent-browser upload "input[type='file']" "/tmp/resume_mlubich.pdf"
```

Wait ~2s and confirm the attachment appears in the snapshot (look for
`button "PDF <filename> XX KB Download"`).

---

### 6. Send the Message

Identify the "Send" button (usually `ref=e84` or similar) from snapshot:

```bash
agent-browser click @eXX   # "Send" button — must NOT be [disabled]
```

Then snapshot to confirm delivery: message appears as a new `generic` node with
`link "View Misha's profile Misha Lubich"` above it (indicating it came from you).

---

### 7. Verify Delivery

```bash
agent-browser snapshot -i
```

Confirm:
- The compose textbox is empty (`textbox "Write a message…": ` with no content)
- A new message bubble appears at the bottom of the thread attributed to `Misha Lubich`
- If a PDF was attached: look for `button "PDF <filename> XX KB Download"` in the thread

---

## Joe Heupler referral CLI

Repeatable sender for recruiter threads. It attaches to the logged-in Chrome on port 9222, writes a short referral, attaches `Joseph_Heupler_Resume.pdf`, checks the file chip, clicks Send, and checks the thread.

```bash
linkedin-refer --limit 15
linkedin-refer --dry-run --limit 1
```

Source: `~/dev/linkedin-refer/cli.js`. Copy rules are tested with `node --test copy.test.js` in that directory. Email is `jheupler@berkeley.edu`. No em dashes.

## Joe Heupler referral CLI

Repeatable sender for recruiter threads. It attaches to the logged-in Chrome on port 9222, writes a short referral, attaches `Joseph_Heupler_Resume.pdf`, checks the file chip, clicks Send, and checks the thread.

```bash
linkedin-refer --limit 15
linkedin-refer --dry-run --limit 1
```

Source: `~/dev/linkedin-refer/cli.js`. Copy rules are tested with `node --test copy.test.js` in that directory. Email is `jheupler@berkeley.edu`. No em dashes.

## Message Style Guidelines

Follow the same tone rules as `recruiter-reply`:
- **Warm, human, concise** — as if typed on a phone.
- **No em dashes** (`—`).
- **No corporate filler** ("I wanted to reach out...", "Please don't hesitate...").
- **Answer every question** the recruiter/contact asked, directly and specifically.
- **No "I updated my resume"** — just answer naturally and attach the PDF silently.

---

## Resume Variants

Available under `/Users/mlubich/dev/resumes/resumes/`:

| Variant                     | Best For                                      |
|-----------------------------|-----------------------------------------------|
| `resume_mlubich_ai/`        | General AI/ML roles                           |
| `resume_mlubich_staff_ai/`  | Staff AI, Lead AI Architect, agent-heavy roles |
| `resume_mlubich_swe/`       | General software engineering                  |
| `resume_mlubich_fde/`       | Field/solutions engineer roles                |

Build any variant with:
```bash
cd /Users/mlubich/dev/resumes
./build.sh build <variant_name>
./build.sh qa <variant_name>   # must exit 0 before sending
```

---

## Common Pitfalls

| Problem | Fix |
|---------|-----|
| 2FA modal appears after login | Ask user to approve LinkedIn app push notification |
| `upload @eXX` fails (wrong ref) | Use `agent-browser upload "input[type='file']" "<path>"` CSS selector instead |
| Send button `[disabled]` | Fill the textbox first OR wait for file upload to complete |
| Message not sending | Check that textbox is not empty and attachment upload finished |
| Thread not found in sidebar | Use `agent-browser eval` to search/click by aria-label |
