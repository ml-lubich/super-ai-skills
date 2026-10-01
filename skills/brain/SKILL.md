---
name: brain
description: Misha's always-on inbox agent. Use when the user asks about the persistent/background agent, the "brain", auto-drafts, the approval queue, the daily briefing, why a draft did or didn't get created, or when adding a new channel or changing what the background agent watches. Triggers include "brain", "the daemon", "the always-on thing", "why didn't it draft", "approve that", "what's queued", "the briefing".
---

# brain — the persistent agent nervous system

Claude Code hooks are session-lifecycle only. They cannot fire on incoming mail.
So the heartbeat lives in launchd, and Claude is the worker it wakes up.

```
launchd com.mlubich.brain (every 600s)
  └─ brain tick
       ├─ snapshot: imail list --json | imsg read | wa chats  -> ~/.config/brain/context.md
       ├─ fingerprint (sha256, timestamp line stripped) vs ~/.config/brain/state
       │    unchanged -> exit, no Claude invoked, no tokens spent
       └─ changed -> claude -p (headless, restricted tools)
            ├─ EMAIL     -> real unsent Mail.app draft via `imail draft`
            ├─ IMSG / WA -> JSON line appended to ~/.config/brain/queue.jsonl
            ├─ PROJECTS  -> edits ~/.config/agent-todo/TODO.md in place
            └─ notify: macOS notification + Telegram (if configured)

launchd com.mlubich.brain-watchdog (every 300s)
  └─ brain watchdog  -> heartbeat stale? job unloaded? headless child hung?
       recovery ladder, non-destructive, circuit-breaker after 3 attempts/6h

launchd com.mlubich.brain-sync (every 30m)
  └─ brain sync  -> pull --rebase, commit, push the knowledge repo

launchd com.mlubich.brain-digest (22:00 daily)
  └─ brain digest  -> 10-line briefing from TODO.md + MEMORY.md

launchd com.mlubich.brain-reply (08:00, 14:00, 19:00)
  └─ brain reply  -> imail autodraft: LLM (openai gpt-5-nano, haiku fallback) + brain recall; auto-send only known contact, low stakes, conf ≥ 0.95; else draft; learned facts -> brain learn
```

## Commands

| Command | Does |
|---|---|
| `brain reply` | Mail autodraft via `imail autodraft` (3x daily). `brain reply --dry` previews. |
| `brain tick` | One poll cycle. What launchd runs. Safe to run by hand. |
| `brain queue` | Show pending iMessage/WhatsApp proposals, numbered. |
| `brain approve N` | Actually send proposal N, then remove it from the queue. |
| `brain drop N` | Discard proposal N. |
| `brain digest` | Generate the end-of-day briefing now. |
| `brain status` | Last tick, queue depth, launchd state, Telegram state. |
| `brain log [n]` | Tail the activity log. |
| `brain doctor` | Per-channel health. Non-zero exit if broken. |
| `brain channels` | What is discovered and how each is approved. |
| `brain install` / `uninstall` | Manage the launchd agents. Idempotent. |
| `brain init` | Write `~/.config/brain/config.env`. |
| `brain tick --dry` | Build the snapshot without invoking Claude. `--force` invokes it regardless. |
| `brain learn "..."` | Record a durable fact. `--title`, `--tags`, `--append`, `--push`. |
| `brain recall "..."` | Hybrid. FTS5 + Porter + name aliases, fused with MLX embeddings when installed. No thesaurus for words an agent invents. `BRAIN_EMBED=0` is lexical only. |
| `brain reindex` | Rebuild the index from markdown. Never touches a note. |
| `brain sync` | Pull, commit, push the knowledge repo. |
| `brain watchdog` | Recover a stalled agent. `--check` reports only, `--reset` clears the breaker. |
| `brain health` | Whole-system table: jobs, heartbeat, breaker, channels, knowledge, sync. |

## Knowledge layer

Markdown in git is the data; SQLite FTS5 is a derived index. That split is what
lets search and `git pull` coexist.

Brain is the cross-device memory. `~/.claude` on this laptop is a local restore
of the kit, so it lags until someone pulls. Another machine can learn a fact or
change a skill before this disk has it.

| What | Repo | How this machine catches up |
|---|---|---|
| Facts, notes | `ml-lubich/brain-knowledge` | `brain sync` then `brain recall` |
| Skills, agents, rules | `ml-lubich/claude-kit` | `claude-kit pull` (dry run), `claude-kit pull --force` to apply |

On any repeatable task, recall before trusting a local file:

```bash
brain recall "own-chrome"
```

Use the local skill under `~/.claude/skills` after that. If a recalled note and
the skill disagree, the note that arrived from git is the newer machine. Do not
treat `~/.claude` as the copy other devices already have.

- notes: `~/.config/brain/knowledge/notes/*.md` -> private repo `ml-lubich/brain-knowledge`
- index: `~/.config/brain/knowledge.db` — gitignored, rebuildable, safe to delete

Dedup is by content hash, so an agent re-learning the same fact is a no-op. A
same-title-different-content note is kept **side by side** — nothing overwrites
a note, nothing deletes one. The always-on rule at
`~/.cursor/rules/brain-knowledge.mdc` tells every session to recall before
guessing and learn when it discovers something durable.

## Resilience

`brain watchdog` runs on its own launchd timer, offset from the tick so one
wedged process cannot take both down. Its ladder, all non-destructive:

1. hung headless child -> SIGTERM, SIGKILL after 20s grace
2. launchd job missing -> reload
3. heartbeat stale (>3 missed cycles) -> `launchctl kickstart` one tick
4. breaker open (3 attempts in 6h) -> stop acting, alert only

**The kill is surgical.** It only ever signals a PID that a tick itself recorded
in `tick.pid`, re-verified as a live `claude -p`. This Mac runs 14+ interactive
claude sessions and none of them can ever be a target. `test_watchdog_ignores_a_
pid_that_is_not_headless_claude` is the guard; never let it regress.

## The safety model — do not weaken this

- The headless agent runs with `--allowedTools` limited to reads, edits, and
  `imail draft`. `imail send`, `imail autodraft`, `imsg send`, and `wa send` are
  explicitly in `--disallowedTools`. **Headless Claude cannot send anything.**
- The only unattended send path is `imail autodraft` via `brain reply`, and only
  for known-correspondent, super-clear, low-stakes follow-ups (confidence ≥ 0.95).
  Everything else is a Mail.app draft.
- Email approval is Mail.app itself: drafts sit unsent, sync to iPhone, Misha
  hits send. No custom approval UI exists or should be built.
- iMessage/WhatsApp approval is `brain approve N`, which is the only send path.
- If asked to let it auto-send, say no once and explain this boundary, then do
  it if he confirms.

## Files

| Path | Is |
|---|---|
| `~/dev/brain/` | Source. Python package `mac-brain`, installed with `uv tool install -e .`, exposes `brain`. |
| `~/.config/brain/config.env` | Telegram token + chat id. Secrets. |
| `~/.config/brain/queue.jsonl` | Pending proposals, one JSON object per line. |
| `~/.config/brain/context.md` | Latest inbox snapshot the agent reads. |
| `~/.config/brain/state` | Last fingerprint, the token-saving gate. |
| `~/.config/brain/brain.log` | Activity log. |
| `~/Library/LaunchAgents/com.mlubich.brain*.plist` | The two heartbeats. |

## Remote control from the phone

Full control (walking around, voice): Tailscale is already up as
`m3-max.tailba802f.ts.net`. From Blink or Termius on iOS:
`ssh mlubich@m3-max.tailba802f.ts.net`. iOS dictation gives
voice input for free. This is the real remote surface, not a custom app.

Light control (approve/deny while away): Telegram, configured in `config.env`.

## Debugging

- Nothing happening: `brain status` -> `launchd` should read 2/2. If not: `brain install`.
- A channel gone quiet: `brain doctor` names the reason.
- Ticking but never drafting: `brain log 40`. A "no change, skipping claude"
  every cycle means the fingerprint is stuck — check `~/.config/brain/context.md`
  actually has content and the CLIs aren't erroring inside the snapshot.
- launchd hands jobs a minimal PATH. `service.PATH` states it explicitly; any new
  binary a channel shells out to must be on that list.
- Full Disk Access: `imsg doctor` and `imail doctor` are the first checks when a
  channel goes silent.

## Extending it

New channel: drop one module in `~/dev/brain/brain/channels/` subclassing
`Channel`. Discovery is automatic (pkgutil + `__subclasses__`) — no registry to
edit, no import to add. Set `sendable = False` when approval happens in the
channel's own app rather than via `brain approve`, the way `mail` does.
Then `uv tool install -e ~/dev/brain --force` and `brain doctor`.

Tests: `cd ~/dev/brain && uv run --with pytest --with typer --with rich python -m pytest tests/ -q`.
`test_send_tools_are_forbidden` is the one that must never be allowed to regress.
Do NOT add a database, a web dashboard, or a queue daemon. Mail.app drafts plus
one JSONL file is the design, and it is deliberate.
