# superai-skills

> **The single command that sets up a full AI-powered developer workstation** — skills, MCP servers, AI CLIs, and runtime tools for any collaborator.

---

## What this IS / What this IS NOT

| ✅ IS | ❌ IS NOT |
|-------|----------|
| Workstation bootstrap (brew + apt tools) | A RAG engine |
| Skill distribution (Claude / Cursor / Codex / Gemini) | A self-learning system |
| MCP server collection (15 submodules) | A memory store |
| AI CLI bootstrap (claude, gemini, codex) | A voice-learning pipeline |
| Cross-platform setup (macOS + Linux) | A replacement for `brain` |

**RAG / voice memory lives in the [`brain` repo](https://github.com/ml-lubich/brain-knowledge).**
`superai-skills` handles setup and skill distribution only — it does not learn on its own.

---

## Architecture

```
superai-skills/
├── skills/          # 35+ agent skills → symlinked into Claude/Cursor/Codex/Gemini
├── packages/        # 15 MCP server submodules
│   ├── linkedin-mcp      LinkedIn MCP server & CLI (Voyager API + CDP Chrome)
│   ├── imail-mcp         macOS Mail.app CLI + MCP server
│   ├── whatsapp-mcp      WhatsApp Web MCP server
│   ├── imsg-mcp          macOS iMessage MCP server
│   ├── jenkins-mcp       Jenkins CLI + MCP server
│   ├── inotes-mcp        macOS Apple Notes CLI + MCP server
│   ├── vercel-mcp        Multi-account Vercel CLI + MCP server
│   ├── railway-mcp       Railway Cloud CLI + MCP server
│   ├── google-voice-mcp  Google Voice CLI + MCP server
│   ├── own-chrome        Headless/headful Chrome CDP controller
│   ├── humanizer         Prose humanization & AI-writing filter
│   ├── claude-tiers      Model-tiered Claude Code delegation ruleset
│   ├── callgen           Audio/call transcript analyzer & visualizer
│   ├── bitbucket-cli     Minimal Bitbucket Data Center/Cloud CLI (`bb`)
│   └── like-fable        Agent behavior & collaboration prompt library
├── prompts/         # Agent-friendly setup prompts (headless / autonomous)
└── super_ai_skills/ # Python CLI source
```

---

## Quickstart

```bash
curl -fsSL https://raw.githubusercontent.com/ml-lubich/superai-skills/main/install.sh | sh
```

Clones to `~/dev/superai-skills` (override with `SUPERAI_HOME`), installs the CLI, then runs `superai-skills init`. Re-running is safe (pulls and re-inits). Pass flags after `sh -s --`, e.g. `| sh -s -- --dry-run` (prints the steps only), `--bitbucket` / `--no-bitbucket`, `--with-brain-daemon`, `--skip-plugins`.

For fully autonomous agent-driven setup, paste the prompt from:
👉 [`prompts/AGENT_SETUP_PROMPT.md`](prompts/AGENT_SETUP_PROMPT.md)

---

Skills are also on [skills.sh](https://skills.sh/ml-lubich/superai-skills): `npx skills add ml-lubich/superai-skills`.

## CLI Reference

| Command | Description |
|---------|-------------|
| `superai-skills setup-dev` | Full workstation bootstrap (brew/apt tools + Python + AI CLIs) |
| `superai-skills doctor` | Health check — all tools, CLIs, and skill links |
| `superai-skills list-skills` | List all 35+ available agent skills |
| `superai-skills list-mcp` | List all 15 MCP server submodules |
| `superai-skills install-skills --target all` | Symlink skills into Claude, Cursor, Codex, and Gemini |

---

## What `setup-dev` installs

**macOS (Homebrew):**
`gh` `git` `jq` `node` `bun` `ffmpeg` `ripgrep` `fd` `fzf` `bat` `zoxide` `starship` `tmux` `mise` `watchman`

**Linux (apt/dnf/pacman):**
`git` `curl` `jq` `build-essential` `python3-pip` `ripgrep` `fd-find` `fzf` `bat` `tmux` `watchman` + `bun` (via installer)

**AI CLIs (bun/npm):**
`claude` (`@anthropic-ai/claude-code`) · `gemini` (`@google-deepmind/gemini-cli`) · `codex` (`@openai/codex`)

**uv tools:**
`httpie` · `rich-cli`

**Python:** 3.13 via `uv python install 3.13`

---

## Collaborators

- **Misha Lubich** (`@ml-lubich`) — Owner
- **Joe** (`@java-heapler`) — Read / Write Collaborator
