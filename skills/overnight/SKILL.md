---
name: overnight
description: Run a long/unattended autonomous job (hours/overnight) with phased execution, checkpoint commits, evidence-based verification, crash resume, and finish notification. Use when the user says "overnight", "run this while I'm away", "long job", or wants unattended multi-hour execution.
---

# Overnight run

You are the MANAGER for an unattended run. Sonnet subagents execute; you plan, verify, checkpoint. Follow the phases in order.

## 1. Setup (before the user leaves)

- Restate the task as a measurable completion condition ("all 40 cases pass", "portal deploys and health-check returns 200"). If it isn't measurable, ask now — this is the last chance.
- Split the work into phases of roughly 30–60 minutes each. Under 10 min = merge phases; over 90 min = split.
- Write `STATUS.md` in the working directory: goal, completion condition, checkbox list of phases, empty sections for `Failed approaches` and `Results`.
- Tell the user to run `caffeinate -dims` in another terminal (or start it yourself in the background) so the Mac stays awake.

## 2. Execute each phase

- Delegate implementation to **sonnet** subagents (ultrawork/Workflow for parallel batches). Self-contained prompts: files, errors, boundaries, output format.
- Commit locally BEFORE any risky step and after each completed phase, so a crash loses minutes, not hours. Push only where the repo's rules allow.
- A phase is done only with evidence: fresh test output, build result, or screenshot. "Should work" does not close a phase.
- Same error 3 times in one phase → mark the phase BLOCKED in STATUS.md with the failure reason, move to the next independent phase (repairs converge within a few attempts or never). Run each retry in a fresh subagent — a transcript containing the failure poisons subsequent attempts.
- After every phase: update STATUS.md — check the box, record results as numbers/one-liners only, log failed approaches and why. No raw dumps.

## 3. Finish

- Run the full completion condition one final time and paste the evidence into STATUS.md.
- Notify: `curl -d "overnight run done: <one-line result>" ntfy.sh/<topic>` if the user gave a topic; otherwise `osascript -e 'display notification "..." with title "Claude overnight"'`.
- Final message to the user = verdict (DONE / PARTIAL with blocked phases) + evidence + link to STATUS.md. Never end with a bare "done".

## Resume after crash/restart

On invocation, if `STATUS.md` already exists: read it, skip checked phases, continue at the first unchecked phase. Retry a previously BLOCKED phase at most once.
