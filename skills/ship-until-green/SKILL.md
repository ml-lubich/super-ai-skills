---
name: ship-until-green
description: Drive any CI/CD project to actually-deployed, looping on your own cron without asking the user. Use whenever a repo with CI or a hosting provider (Vercel, Fly, GitHub Actions) is red, stale, or "pushed but not live" — ERIA (eria-website) and briopedia especially. Triggers include "CI is failing", "the build is broken", "it's not deploying", "why isn't this live", "get this done", or discovering a red run while doing something else.
---

# Ship until green

**Misha does not want to be the loop.** "You have to just nudge yourself or
something on a cron job until fully done and deployed." Reporting a blocker and
stopping is the failure mode this skill exists to prevent. Define your own
success criteria, then drive to them.

## Definition of done — all four, with evidence

1. **CI green** on the pushed HEAD. `gh run list` → `success`, not "no runs".
2. **The deploy actually ran.** A green build is not a deploy.
3. **Production serves the new code.** Fetch the live URL and grep a marker string
   that ONLY the new build contains. A deploy reporting success while the CDN
   serves the old bundle is the exact failure this catches.
4. **No `git status` surprises** — nothing of yours left uncommitted.

Never report done on 1 and 2 alone.

## Loop, don't ask

Schedule your own recurring check with `CronCreate` and keep it until criterion
3 is met, then `CronDelete` it. Each firing: check, act on what you find, report
one line. "No change" is a fine tick. Escalate to Misha ONLY for something no
agent can do — a password, an OAuth grant, a billing/dashboard state change — and
then say it once, not hourly.

## Root-cause, don't retry

A red run is a bug report. Read the actual log (`gh run view <id> --log-failed`),
reproduce locally, fix the cause.

**Local passes but CI fails on "the same command" — check that it IS the same
command.** ERIA's CI step was named "Unit tests (same command as Vercel build)"
and omitted `--isolate`; without isolation the suite cross-pollutes and 36 tests
fail. CI was red for days on a problem production never had. The name asserted
the thing that was false.

Guard drift with a test that parses both files and compares. Match the whole
line — `bun test` is a prefix of `bun test --isolate`, so `toContain` passes
against the broken form. Verify the guard RED before you trust it green: a guard
that reads one pinning form and passes while production uses the other is worse
than no guard, because it converts "nobody checked" into "somebody checked and
it was fine".

## Vercel, in the order these actually bite

- **`BLOCKED` deployment + 0 ms build = the PROJECT is paused**, not an auth or
  build problem. Check `live` on the project; do not read build logs, there is no
  build. Unpausing is billing-linked and Misha's call.

  **How to detect this WITHOUT any Vercel credential** (briopedia, 2026-09-11 —
  the credential is exactly what you won't have when this bites):

  ```bash
  id=$(gh api repos/<owner>/<repo>/deployments -q '.[0].id')
  gh api repos/<owner>/<repo>/deployments -q '.[0].created_at'
  gh api repos/<owner>/<repo>/deployments/$id/statuses -q '.[0].created_at'
  ```

  Same second in both = zero elapsed = no build ran. A clone, an install or a
  compile that was too slow or too big fails *during* a build, minutes in; it
  cannot fail before one starts.

  Two things make this hard to see, and both cost days here:
  - **The site stays up.** Pausing stops new builds but leaves the last
    deployment serving, so production looks alive on an old bundle. That reads
    as "stale CDN" and sends you chasing caching, git integration, or repo size.
  - **The error text is a dead end.** GitHub shows only "Deployment has failed —
    run `npx vercel inspect … --logs`", and that command needs the credential
    you don't have. The message points at a log that does not exist.

  Do not accept a size/clone theory without a log. Vercel's `/docs/limits`
  documents **no maximum git repository size** for Git-integration builds — the
  only size limit is CLI *source upload* (100 MB Hobby / 1 GB Pro), and
  `.vercelignore` applies to that path only. Briopedia's 3.6 GB `.git` looked
  like an obvious culprit and was not one; acting on it would have meant a
  history rewrite, which is forbidden outright.
- **"Not authorized" is usually account/team drift, not an expired token.** Run
  `vgate ls` AND `vgate whoami` together, compare the active account row against
  the team line, before concluding anything or starting a device-code grant.
- **Never `vgate switch` / `vgate use`.** Vercel auth is global on this machine —
  one active account for every session — so aiming it at a client org makes that
  the default for sessions deploying personal projects. Pass `--scope <team>`
  explicitly; verified to work regardless of the pin. Client and personal never mix.
- Pushing to GitHub does not deploy these projects. "I pushed it" is never evidence.

## Hard rules

- **NEVER rewrite git history.** No git-filter-repo, filter-branch, BFG,
  force-push, rebase of pushed commits, `reset --hard` on shared branches. No
  deleting remotes, branches, or tags. Stated absolutely; not a trade-off to reopen.
- **Never `vercel logout`** — it destroys the only stored credential.
- **Never automate an OAuth/device-code approval.** Those denials are deliberate.
  A skill that packages a denied action is not authorization.
- Stage explicit paths. Never `git add -A` in a tree other sessions share.
