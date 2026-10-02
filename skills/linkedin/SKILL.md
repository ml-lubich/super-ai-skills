---
name: linkedin
description: Drive your own LinkedIn with the `linkedin` CLI (alias `li`) over a logged-in Chrome, so an agent never hand-writes browser code. Use to sign in, scan the inbox for unanswered recruiter messages, read a thread, and reply (text, optional resume PDF) with a dedupe ledger.
---

# LinkedIn via `linkedin` (alias `li`)

One CLI, one Chrome (CDP port 9222). Never write browser/CDP code: every step is a command.
Install: `superai-skills init` (the `linkedin-mcp` package), then `linkedin doctor`.
If `li` is shadowed by another tool on your PATH, use `linkedin`.

## Output is token-minimal
Read commands print ONE line of compact JSON. Shrink output with flags, not jq:
- `--fields name,url` keep only those keys (before or after the subcommand)
- `--limit N` max rows (a last `{"more":k}` row says how many were cut); put it before the subcommand
- `--max-chars N` truncate strings (default 300; 0 = full text)
Errors are one line: `error: <what> | next: <command to run>`. Do what `next` says.
`-h` works on every command. Anything that sends needs `--confirm`; without it nothing is sent.

## Flow
1. `linkedin login --account you@example.com` signs Chrome in from your macOS Keychain
   (`security add-internet-password -s linkedin.com -a you@example.com -w`, type the password
   at the prompt). One attempt; it stops on captcha/2FA and tells you.
   `linkedin doctor` checks Chrome, login and config.
2. `linkedin scan` lists threads that still need a reply: `[{name,url,unread,text,fit}]`.
   Read more of one thread: `linkedin messages read --url <url> --max-chars 0`.
3. Write ONLY the message bodies into `queue.json`:
   `[{"name":"Ada L","profile_url":"https://www.linkedin.com/in/..","company":"Acme","role":"AI engineer","body":"..."}]`
   (use `thread_url` instead of `profile_url` to reply inside an existing thread).
4. `linkedin referral queue queue.json` is a dry run: check each row's `status` and `reason`.
5. `linkedin referral queue queue.json --confirm` sends each body, then the resume PDF as its own
   message, re-reads the thread to verify, and records the person in a ledger so nobody is
   messaged twice. `--limit N` stops after N.

Other commands: `linkedin classify "<text>"`, `linkedin messages threads --unread`,
`linkedin messages send <text> --to <name> --confirm`, `linkedin profile <id>`, `linkedin search <q>`.

## Rules
- Only reply to people who messaged you, about real jobs. Skip sales, scams, closed threads.
- One message per person, ever. The ledger enforces it; never bypass it.
- Never oversell: skip roles the `fit` verdict marks `skip`, and call a `stretch` a stretch.
  Do not claim skills, years or clearance you do not have.
- Plain, human wording, no em dashes, no markdown. Name the person, company and role.
- Send only when asked. `--confirm` is the only send switch.
