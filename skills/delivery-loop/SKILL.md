---
name: delivery-loop
description: The standing build-and-ship loop for Misha's client work (ERIA and any other client repo). Use whenever a task means "get this done" end to end rather than answering a question - implementing a ticket, acting on a client ask from WhatsApp/Linear/ClickUp, or any request phrased as "finish it", "get it done", "ship it", "don't ask me again until it's done", "and verify". Defines what one iteration of the loop is, what the gates are, and which existing skill owns each phase.
---

# Delivery loop

One iteration = **ask → test → build → verify → gate → ship → close → tell them**.
An iteration is not done because the code is written. It is done when the gate is
green, it is live, and the person who asked knows.

Never invent a phase-owner skill. Each phase below delegates to one that exists.

## The eight phases

| # | Phase | Owner | Exit condition |
|---|-------|-------|----------------|
| 1 | Gather the real ask | `client-comms` for tone, WhatsApp/Linear/ClickUp for source | The ask is written down in one sentence, in the client's own words. Latest message wins over earlier ones. |
| 2 | Failing test first | `superpowers:test-driven-development` | A test exists that fails **now** and would have passed only after the change. Skip only for docs/typo/behaviour-neutral edits. |
| 3 | Smallest change that passes | `ponytail` | Test green. Root cause, not the one caller named in the ticket. |
| 4 | See it with your eyes | `agent-browser` (UI) or a real run | For UI: screenshot at desktop **and** iPhone width, after the reveal animation settles. Markup correctness is not a pass. |
| 5 | Green gate | this repo's documented command | `npm run lint` + `npm run test:unit` (bun needs `--isolate`; a bare `bun test src` invents failures). Fresh output pasted, not remembered. |
| 6 | Ship | `git push origin main` | Straight to `main`, never a branch. Stage by explicit path — other sessions share this tree. Vercel deploys on push. |
| 7 | Close the ticket | `ticket-closeout` | The tracker state matches reality the moment it lands. |
| 8 | Tell them | `client-comms` | Plain business value, no commit hashes, no jargon. |

## Gates that are not optional

- **No fake completion.** A TODO, a `test.skip`, a stubbed branch, or "should work"
  is a blocker to report — never evidence of done. Grep the diff for them before
  claiming anything.
- **Evidence or it didn't happen.** Every completion claim carries fresh command
  output, a test result, or a screenshot. Banned in completion claims: "should
  work", "probably", "seems to".
- **Config presence is not liveness.** An env var being set, a row existing, a
  200 response — none of those prove the path works. Exercise the real path.
- **Verify in a fresh lane.** The context that wrote the code does not get to
  approve it. Same error three times → stop patching, report the root issue.

## When the loop is autonomous

"Don't ask me again until it's done" means: no blocking questions, work every
unblocked item, and when something is genuinely blocked (a rate limit, a missing
asset, an answer only the client has) — do every other item in full, then report
exactly what is left and why. Waiting out a timed block is part of the loop, not
a reason to stop. Long unattended runs → `overnight`.

## After every loop

Capture what bit you. A fix you had to rediscover is a memory
(`~/.claude/projects/<project>/memory/`); a procedure you had to re-derive is a
skill. Update the existing file rather than adding a near-duplicate.
