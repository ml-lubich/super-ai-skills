# AGENT SETUP PROMPT — superai-skills

You are setting up the **AI super-developer workstation** for a new collaborator.
Execute each step in order. Do not skip. Do not ask questions — proceed.

---

## Step 0 — Prerequisites

Verify the platform before continuing:

- **macOS**: Homebrew must be installed. If missing: `https://brew.sh`
- **Linux**: `apt-get`, `dnf`, or `pacman` must be available.

```bash
# macOS check
command -v brew || echo "MISSING: install Homebrew first"

# Linux check
command -v apt-get || command -v dnf || command -v pacman || echo "MISSING: no package manager found"
```

---

## Step 1 — Clone the repo (with submodules)

```bash
git clone --recurse-submodules https://github.com/ml-lubich/superai-skills.git ~/dev/superai-skills
cd ~/dev/superai-skills
```

If already cloned without submodules:

```bash
cd ~/dev/superai-skills
git submodule update --init --recursive
```

---

## Step 2 — Install uv

```bash
command -v uv || curl -LsSf https://astral.sh/uv/install.sh | sh
# Reload shell after install if uv is not yet in PATH
source ~/.zshrc 2>/dev/null || source ~/.bashrc 2>/dev/null || true
```

---

## Step 3 — Install Python 3.13

```bash
uv python install 3.13
# Verify
uv run --python 3.13 python --version
```

---

## Step 4 — Install the superai-skills package

```bash
cd ~/dev/superai-skills
uv tool install --editable .
# Verify
superai-skills --help
```

---

## Step 5 — Bootstrap the full environment

```bash
superai-skills setup-dev
```

This installs (macOS via brew / Linux via apt):
`gh git jq node bun ffmpeg ripgrep fd fzf bat zoxide starship tmux mise watchman`

And installs Python uv tools: `httpie`, `rich-cli`.

---

## Step 6 — Install AI CLIs

```bash
# claude
bun add -g @anthropic-ai/claude-code

# gemini
bun add -g @google-deepmind/gemini-cli

# codex
bun add -g @openai/codex

# Verify all three
claude --version
gemini --version
codex --version
```

---

## Step 7 — Link skills into all AI clients

```bash
superai-skills install-skills --target all
```

This symlinks `skills/` into:
- `~/.claude/skills/`
- `~/.cursor/skills/`
- `~/.codex/skills/`
- `~/.gemini/config/skills/`

---

## Step 8 — Initialize MCP submodules

```bash
cd ~/dev/superai-skills
git submodule update --init --recursive
```

Each MCP server lives under `packages/`. Start individual servers per their own README.

---

## Step 9 — Health check

```bash
superai-skills doctor
```

Expected output: green checkmarks for uv, python3.13, bun, claude, gemini, codex, and all brew tools.

---

## Expected Outcome — Full Checklist

After all steps complete you should have:

| Item | Status |
|------|--------|
| Homebrew | ✓ |
| uv | ✓ |
| Python 3.13 (via uv) | ✓ |
| gh, git, jq, node, bun | ✓ |
| ffmpeg, ripgrep, fd, fzf, bat | ✓ |
| zoxide, starship, tmux, mise, watchman | ✓ |
| claude CLI | ✓ |
| gemini CLI | ✓ |
| codex CLI | ✓ |
| httpie, rich-cli (uv tools) | ✓ |
| superai-skills (editable install) | ✓ |
| Skills linked (Claude/Cursor/Codex/Gemini) | ✓ |
| MCP submodules initialized | ✓ |

---

> **Note:** RAG / voice memory lives in the `brain` repo (`ml-lubich/brain-knowledge`).
> This repo (`superai-skills`) only handles workstation setup and skill distribution — it does **not** learn on its own.
