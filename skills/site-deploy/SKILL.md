---
name: site-deploy
description: Deploy Misha's personal-brand sites (mishalubich.com, josephheupler.com, yuvarajt.com, ashveer-sewpersad) and wire up their JoeAI/YuvarajAI/AshveerAI chat agents. Use whenever a change to one of those repos needs to reach the internet, when someone says the site "isn't updating" or "still shows the old version", when a Vercel deploy or its tests fail, or when a chat panel answers "Chat is not configured". Also covers the Fly-hosted backends (brio-sales-navigator, briopedia). Triggers include "deploy the site", "push it live", "ship it", "why isn't my change live", "the site is stale", "vercel failed".
---

# Deploying the personal sites

## The one thing to know first

**Check whether the project auto-deploys before assuming it doesn't.** This skill used to
say flatly that pushing to GitHub never deploys these projects. That is wrong, and believing
it sends you hunting for a manual deploy that was never needed.

Verified 2026-09-13 with `gh api repos/ml-lubich/<repo>/deployments`:

| Repo | Auto-deploys on push? |
|---|---|
| `portfolio` | **Yes** — `vercel[bot]`, status `Vercel – portfolio: success` |
| `jheupler-site` | **Blocked** since 2026-09-18 — `TEAM_ACCESS_REQUIRED` (see below) |
| `yuvaraj-site-ey` | **Blocked** since 2026-09-18 — `TEAM_ACCESS_REQUIRED` (see below) |
| `briopedia` | **Yes** — last Production deploy 2026-09-13 |
| `ashveer-site` | **No** — zero deployments ever; no integration attached |
| `eria-website` | **Stopped** — last GitHub deployment 2026-07-25, nothing since |

So: `portfolio`, `jheupler-site`, `yuvaraj-site-ey` and `briopedia` ship on a plain `git push`.
Only `ashveer-site` needs the CLI, and `eria-website`'s integration died in July.

Confirm per project rather than trusting either blanket rule:

```bash
gh api repos/ml-lubich/<repo>/commits/main/status --jq '.statuses[].context + ": " + .state'
gh api repos/ml-lubich/<repo>/deployments --jq '.[0] | .created_at + " " + .environment'
```

**Git pushes blocked with `TEAM_ACCESS_REQUIRED` (2026-09-18):** the GitHub user
`ml-lubich` maps to a *different* Vercel account (userId `dkBMYx9…`, the one that owns
team `ml-lubichs-projects` and the `v0-*` duplicate projects) that is not a member of
`mlubich-projects`. The commit email is already correct, so amending the author does
not help. Ship with `sitedeploy ship --only <repo>` (CLI deploy as the team member).
Read the reason from `GET /v13/deployments/<id>` → `seatBlock.blockCode`.

**A push is still not proof a change is live.** Fetch the site and grep a marker string that
only the new build contains.

## Use the CLI

```bash
sitedeploy doctor        # what is blocking right now — read-only, safe to spam
sitedeploy login         # opens a Terminal tab for the interactive vercel login
sitedeploy env           # copy chat env from portfolio to the agent sites
sitedeploy ship          # deploy everything, verify each against a live marker
sitedeploy all           # env + ship
sitedeploy ship --only jheupler-site
```

`doctor` is the right first move for any "the site is stale" report. It prints
credential state, per-repo git state, and whether each live URL is serving the
current build — which is usually the whole diagnosis.

## What you cannot do, and must not try to route around

`sitedeploy login` opens a Terminal tab and stops. That is deliberate.

The Vercel CLI uses an OAuth device grant: it prints a code, and a human
approves it in a browser. Approving that grant hands durable account access to
whoever asked, so it is a person's decision. This sandbox blocks the tools that
would let an agent click it — `cua-driver`'s CLI and MCP tools are both denied,
and Chrome is not exposed on a debugging port. **Those denials are the feature.**
Do not look for another way through; surface the code and let Misha click.

Symptoms of the credential being stale:

- `vercel whoami` → `Error: Not authorized`
- `vercel --scope mlubich-projects` → `The specified scope does not exist`
- `vgate ls` shows the account as `expired`

`vgate` cannot fix this. `vgate sync` saves an *already active* login; it cannot
renew a dead one. Only `vercel login` can, and **never run `vercel logout`** —
it destroys the only stored credential.

## The chat agents

Each site ships an OpenRouter agent ported from the portfolio: JoeAI, YuvarajAI,
AshveerAI. Each needs `OPENROUTER_API_KEY` and `CHAT_RATE_SECRET` in its own
Vercel project, or `/api/chat` returns a clean `503 {"error":"Chat is not
configured."}`. That 503 is correct behaviour, not a crash — the rest of the
site is unaffected.

`sitedeploy env` copies both keys from the portfolio project, which is the one
that already has them. It never prints a value.

Cookie names are namespaced per site (`joeai_q`, `yuvarajai_q`, `ashveerai_q`)
so their rate-limit quotas cannot collide.

## Tests failing in Vercel

Only the portfolio runs tests during its Vercel build (`vitest run && next
build`); the other three run `next build` alone. So a Vercel test failure is
almost always the portfolio.

The usual cause is a test that reaches the public internet. Link-rot checks are
worth keeping — they have caught four dead links — but they must not gate a
deploy: a third-party CDN having a bad minute would block shipping an unrelated
change. Those checks are gated behind `if (process.env.VERCEL) skip`, so they
run locally and in the git hooks and skip in the deploy. **If you add a test
that makes a network call, gate it the same way.**

## Fly backends

`flyctl` is authenticated separately and generally works when Vercel does not.

```bash
flyctl apps list
flyctl status -a brio-sales-navigator
flyctl deploy -a brio-sales-navigator --now
```

`brio-sales-navigator` and `briopedia-backend` are Fly apps. A `suspended` state
means it needs a deploy to come back. These use scale-to-zero, so a cold first
request taking several seconds is configured behaviour, not a fault.

## Verifying, properly

Never report a site as shipped on the strength of a green build. Fetch the URL
and assert a marker that only the new build contains — `sitedeploy ship` does
this automatically and fails loudly when the marker is missing. A deploy that
reports success while the CDN still serves the old bundle is the exact failure
this guards against.
