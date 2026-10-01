---
name: vercel-login-auto
description: Complete a `vercel login` device-code approval in a named Chrome profile, without a human clicking. Use when `vercel whoami` says "Not authorized", `vgate ls` shows every account expired, a deploy fails with "The specified scope does not exist", or a site is serving a stale build because nothing can authenticate. Also covers why the Briopedia frontend cannot deploy from its git integration. Triggers include "vercel login", "not authorized", "vgate expired", "the site is stale", "deploy is blocked on a credential".
---

# Completing a Vercel login without a human at the keyboard

## The one-liner

```bash
~/.claude/skills/vercel-login-auto/vercel-login-auto.sh michaelle.lubich@gmail.com
```

Takes **any** account — `engineering@eriaevents.co`, `metropol007@gmail.com` —
or a raw profile directory (`"Profile 2"`). The account is a required argument
on purpose; see the wall below.

It: starts `vercel login`, scrapes the device URL it blocks on, opens that URL
in the Chrome profile whose **primary** account matches, clicks the approve
control by visible label, waits for the CLI, verifies with `vercel whoami`,
then **`vgate sync` — verified against `vgate ls`, not fire-and-forget** — and
finally lists the teams this login unlocks. It fails loudly rather than
reporting success it did not confirm.

**`vgate sync` is not optional.** Without it the login is not switchable, so
the next session needing a different account strands this one. And a silent
`vgate sync` failure looks exactly like a success — it only surfaces days later
as `expired` — so the script re-reads `vgate ls` and reports the row it stored.

**Any account, any team, any project.** The account is the argument; the teams
that login unlocks are printed at the end. Pass `--scope <team>` per command —
never `vgate switch`/`use` to pin one, because Vercel auth is global on this
machine and pinning a client team makes it the default for every session.

**The failure this now names out loud:** if the resolved Chrome profile is not
signed in to vercel.com, the device page renders the login screen and "Allow
Access" is present but **disabled**. No retry or re-worded click fixes it — the
script stops with that exact message instead of a generic timeout. Signing that
profile in is one manual step, once per profile per service (2026-09-11: this
is what stalled every automated attempt on `Default`).

## One code, one process — never two logins at once

A device code (`XXXX-XXXX`) belongs to exactly **one** `vercel login` process.
Vercel binds the code to the process that printed it, and the code is consumed
the moment it is approved. So:

- Two `vercel login` processes = two codes. Approving one does nothing for the
  other, and entering a code a second time (or the wrong one) gives
  **"Could not verify user code. Review the spelling or issue a new code."**
- The script now **refuses to start** while another `vercel login` is pending
  (`pgrep -f 'vercel login'`), and prints the pid to kill. Never start a
  second login "to be safe" — that is exactly what strands the first.
- Need two accounts logged in? Pass them all in one call:
  `vercel-login-auto.sh engineering@eriaevents.co michaelle.lubich@gmail.com`.
  The script runs them **sequentially**, and each account gets its own
  `vercel login` process, its **own device code**, its own Chrome profile,
  approval and `vgate sync`. **One code is never used for two profiles.** Vercel
  auth is global, so the **last** account listed stays active; `vgate switch`
  flips between the stored ones.
- The approve click goes to the Chrome tab whose URL contains **this login's
  code**, never to "the front window". The front window can be another
  profile's, which approves the wrong account or an already-dead code. If no tab
  shows the code, it says so and you approve by hand in the named profile.
- Success is read from the CLI's own log ("signed in"), then confirmed with
  `vercel teams ls`. `vercel whoami` is **not** a health check — it 401s on
  healthy logins (2026-09-17: the script called a good login a failure on it).
- After `vgate sync` the script checks the stored email is the account you
  asked for. Approving the page in a Chrome profile signed in as someone else
  logs *that* account in (2026-09-17: asked for `engineering@eriaevents.co`,
  got the personal account) — the script now dies loudly on that instead of
  reporting success.

## The profile wall — the reason this is a script

Chrome's directories are `Default`, `Profile 1`, `Profile 2`… and the number
says nothing about the account. On this machine:

| directory | primary account |
|---|---|
| `Default` | michaelle.lubich@gmail.com (personal) |
| `Profile 2` | **engineering@eriaevents.co (CLIENT)** |
| `Profile 13` | mikelubich@gmail.com |

`Profile 2` also lists the personal address as a *secondary* account. So a
naive "does this profile mention my email" match returns the **client**
profile, and the flow authorises a personal tool inside a client org. The
resolver matches the primary account only, and refuses rather than guessing:

```bash
./resolve-chrome-profile.py                      # list every profile
./resolve-chrome-profile.py you@example.com      # -> directory name
```

## Prerequisites — one-time, and a human decision

The script cannot grant these to itself, and that is deliberate.

1. **Chrome → View → Developer → "Allow JavaScript from Apple Events"**
2. **System Settings → Privacy & Security → Automation** → allow the calling
   terminal to control Google Chrome
3. **If run from an agent harness**, the harness must permit `osascript`.
   Claude Code's auto-mode classifier blocks `osascript` against Chrome by
   default — both `execute javascript` and System Events UI control — so an
   agent hits a denial no amount of retrying will pass. Add a Bash permission
   rule for `osascript` if you want an agent to run this unattended. **Do not
   try to route around the denial**; it exists because approving an OAuth grant
   hands durable account access to whoever asked.

## Never

- **`vercel logout`** — destroys the only stored credential.
- **`vgate` to fix an expired login.** `vgate sync` *saves an already-active*
  login so it can be switched back to later. It cannot revive a dead one. Only
  `vercel login` can. Run `vgate sync` after, never instead.

## Briopedia: why the frontend will not deploy from git

Diagnosed 2026-09-07, and it is not a credential problem, so this script will
not fix it:

```
gh api repos/ml-lubich/briopedia/deployments  ->  a deployment per push
                                              ->  each FAILS in ~1 second
.git   3.6 GB      working tree  15 GB      wiki/  3.8 GB
```

Vercel's git integration **clones the repository**. It dies before reaching any
build — the code itself builds fine (`next build`, exit 0, 3310 paths). One
second is far too fast to be a build failure.

`.vercelignore` does not help: it applies to **CLI uploads**, not to the git
clone. Which is exactly why CLI deploys worked and the git integration never
has. So for this repo:

- **Use the CLI path** — `vercel --prod --yes --scope mlubich-projects`, which
  respects `.vercelignore` and uploads a small tree, or the
  `deploy-frontend.yml` workflow that does the same on a runner with a
  `VERCEL_TOKEN` secret.
- The Fly backend is unaffected; it deploys through
  `.github/workflows/deploy-backend.yml`.

`sitedeploy doctor` is the fastest read on credential + freshness state.

## Verifying

Never report a site as shipped on a green build. Fetch the URL and assert
something only the new build contains, or read `age:` from the response
headers — a Vercel CDN will happily serve a 31-hour-old bundle behind a
"successful" deploy.
