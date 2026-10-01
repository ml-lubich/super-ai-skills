---
name: software-factory
description: Run work end to end without a human in the loop - a client message or ticket becomes tested, reviewed, deployed code that is proven to be serving to users. Use when the user wants an autonomous pipeline, a "software factory", unattended overnight delivery, a fleet of agents working in parallel, or intake wired straight from WhatsApp/Slack/email to shipped code. Also use when deciding how to loop an agent until a goal is verifiably met, or when a previous run claimed done but nothing actually reached production.
---

# software-factory

Four layers. Three of them already exist — do not rebuild them.

| Layer | Use | Not |
|---|---|---|
| Intake | Claude Code **routine with an API trigger** | a polling daemon |
| Pipeline | **obra/superpowers** skills (installed) | a bespoke stage runner |
| Loop | **`/goal`** (built in, has a verifier) | `while true` in bash, cron wakeups |
| Fleet | **`claude --bg`** (auto git worktrees) | hand-coordinated shared checkouts |

The only thing worth writing yourself is the adapter from your event source to
the trigger URL.

## The one rule that makes or breaks it

**The `/goal` evaluator calls no tools and reads no files.** It grades the
transcript against your condition. So a condition naming a *state* lets the
agent assert that state in prose and pass. A condition naming *proof* does not.

```
BAD   /goal the tests pass and it is deployed
GOOD  /goal `npm run lint` and `npm run test:unit` have both been run and their
      exit codes shown as 0, AND `curl -s https://eria.co/tickets` has been run
      and its output contains "Corporate Vendor Expo". Show all three command
      outputs in full. Stop after 15 turns.
```

Name the command. Demand the output in the transcript. Bound the turns.

## Three facts people collapse into one

Green checks, a deployment record, and a live site are **three different facts**.
A change can pass CI, produce a deployment row, and still not be serving.

Real case: eria-website sat `live: false` (paused project) for four days. Every
deploy returned `readyState: BLOCKED` with a **0ms build** and the aliases
intact, so production served the old bytes while everything upstream looked
green. Anything gating on CI would have declared victory daily.

So the **last gate in every loop asserts on the public URL's bytes**:

```bash
curl -s https://eria.co/private-viewing | grep -q "Book a private viewing"
```

Assert on a string that exists *only after this change*. A 200 proves nothing —
this repo already has a dead booking link that returns 200. If the change is an
image, rename the file; the optimizer caches by URL.

**Put that assertion inside the `/goal` condition, not after it.** superpowers
ends at `finishing-a-development-branch` (merge / PR / keep / discard) and
nothing downstream ever checks that the change is serving. A post-hoc check is
something a finished run skips; a clause in the completion condition is
something the Stop hook cannot mark done without.

## Reading results programmatically

The agent never eyeballs output. Exit codes and JSON fields are the signal, and
noisy output goes to a file so it never enters context.

```bash
npm run lint > /tmp/lint.log 2>&1 && npm run test:unit > /tmp/test.log 2>&1
echo "gate=$?"        # only this line needs to reach the transcript

# CI for the exact commit, never "the branch"
gh api repos/<owner>/<repo>/commits/$(git rev-parse HEAD)/check-runs \
  --jq '[.check_runs[] | {name, status, conclusion}]'
```

For an orchestrator, make the verdict typed instead of prose:

```bash
claude -p "Run the gate and report" --output-format json \
  --json-schema '{"type":"object","properties":{"pass":{"type":"boolean"},
    "failing":{"type":"array","items":{"type":"string"}}},"required":["pass"]}' \
  | jq -e '.structured_output.pass'
```

## Intake

A routine is a saved prompt plus repos. Give it an API trigger and it gets a
permanent endpoint; anything that can POST starts an agent.

```bash
curl -X POST https://api.anthropic.com/v1/claude_code/routines/<trigger_id>/fire \
  -H "Authorization: Bearer <token>" \
  -H "anthropic-beta: experimental-cc-routine-2026-04-01" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"text": "Nikita asked: move the booking button above the fold"}'
```

The payload arrives wrapped and marked untrusted, and is **inert unless the
saved prompt explicitly says to act on it**. A routine that never mentions the
payload reads the message and does nothing. There is also no idempotency key, so
a webhook retry starts a second session — dedupe on your side before the curl.

## Fleet

```bash
id=$(claude --bg --name fix-lint --model sonnet "fix lint in src/components")
claude agents --json --all | jq '.[] | {id, state, waitingFor}'
claude logs "$id"; claude stop "$id"; claude rm "$id"
```

Every background session gets its own worktree under `.claude/worktrees/`, so
parallel writers cannot collide. `blocked` is the state a fleet stalls in — it
wants a permission answer.

**Make pushing part of every worker's done-condition.** `claude rm` refuses to
remove a worktree holding unpushed commits, and recovery needs an exact
`--discard-unpushed <commit>@<worktree-id>` value the failed command printed
once. Workers that forget to push leave worktrees you cannot clean.

## Traps that cost real days

- **`claude -p` without `--bare`** executes the target repo's own
  `.claude/settings.json` hooks and `.mcp.json` servers in a folder nobody
  trusted. Always `--bare` for unattended runs on repos you did not write.
- **`--max-turns` is undocumented** in current versions. Bound with
  `--max-budget-usd` and a turn cap inside the goal text.
- **A green routine run means the session started and exited**, not that the
  task succeeded. Blocked requests and task failures live inside the transcript,
  invisible to the status indicator.
- **Rate limits leave a goal active**; auth failure, exhausted credits,
  unclearable context overflow and an unavailable model all clear it.
- Several turns with no tool use trips a circuit breaker and hands control back
  with the goal still set.

## Wiring superpowers for unattended runs

Nothing in superpowers hard-requires interactivity. It registers one hook
(`SessionStart`, synchronous, no TTY assumption) and `AskUserQuestion` appears
nowhere in the core skills.

**The seam is a plan file on disk.** `skills/executing-plans/SKILL.md` opens with
"Read plan file", which splits the pipeline cleanly:

| Half | Skills | Needs a human |
|---|---|---|
| Authoring | `brainstorming` → `writing-plans` | Yes, by design |
| Execution | `executing-plans` → `subagent-driven-development` → TDD → review | **No** |

So intake is not a framework. It is one small generator that turns a ticket or a
message into a plan file, after which you launch `claude -p` pointed at
`executing-plans` and skip brainstorming entirely.

What blocks headless operation is **prose, not code** — three checkpoints in
`executing-plans`: raise concerns before starting, stop and ask on a blocker,
and finish by presenting merge/PR/keep/discard. They are markdown instructions,
so the invoking prompt overrides them. **Redirect, do not delete:** on a blocker
write a status file and exit instead of asking, and hard-set the finish action to
"open PR". That keeps stop-on-blocker, which is the discipline worth having, and
removes only the waiting.

## Do not adopt

`claude-flow` / `ruflo`, despite the highest star count in the category. An
independent audit by GitHub user `roman-rr` (2026-04-04, gist
`ed603b676af019b8740423d2bb8e4bf6`, against v3.5.51) read the source, traced
process execution, and called the tools hands-on: **~290 of 300+ MCP tools
returned well-formed state JSON with no executor behind them.** `agent_spawn`
reported idle without creating a subprocess; `neural_train` returned a random
accuracy; `wasm_agent_prompt` echoed its input. Roughly ten were real.

The maintainer acknowledged it on 2026-05-03 and shipped 24 documented fixes
(v3.6.14–v3.6.22); several architectural gaps stayed open and **nobody has
re-audited since**. So the honest statement is not "it is fake" — it is that
adopting it means auditing it yourself, which disqualifies it as a foundation.

**The generalisable lesson, which matters more than the project:** the tools did
not throw errors. They returned plausible successes. Any layer that reports its
own status can lie this way — a green routine run, a deployment row, a 200 from a
dead link. Assert on the effect, never on the report.

## Order of assembly

1. Prove the loop by hand on one real ticket with `/goal` and a proof-shaped condition.
2. Add the public-URL assertion as the final gate.
3. Wire one event source to the trigger with dedupe.
4. Only then fan out with `--bg`.

Each step is verifiable on its own. Skipping to step 4 produces a fleet whose
output nobody can trust.
