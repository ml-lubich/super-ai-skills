# Agent Prompt: Automated SuperAI-Skills Setup & Environment Initialization

You are an agent tasked with onboarding or equipping this workspace with Misha's **`superai-skills`** meta-suite. Follow these instructions strictly to set up, install, and verify all skills, MCP servers, and environment dependencies.

---

### Step 1: Clone or Update the `superai-skills` Repository
Ensure the repository is cloned recursively with all submodules into `~/dev/superai-skills`:

```bash
mkdir -p ~/dev
if [ ! -d "$HOME/dev/superai-skills/.git" ]; then
  git clone --recurse-submodules https://github.com/ml-lubich/superai-skills.git ~/dev/superai-skills
else
  cd ~/dev/superai-skills && git pull --rebase && git submodule update --init --recursive
fi
```

---

### Step 2: Install the Package & Python CLI
Install the Python OOP package in editable mode via `pip` or `uv`:

```bash
cd ~/dev/superai-skills
pip install -e .
# Or via uv:
# uv tool install --editable . --force
```

---

### Step 3: Run Native Environment Setup (No Shell Scripts)
Execute the Python-driven environment manager to provision necessary system dependencies (`gh`, `git`, `jq`, `node`, `uv`, etc.):

```bash
superai-skills setup-dev
```

---

### Step 4: Deploy All Agent Skills
Link or install all 35+ personal agent skills into your AI client directory (Claude, Cursor, Codex, Gemini):

```bash
superai-skills install-skills --target all
```

---

### Step 5: Verification & Diagnostics
Run the diagnostic doctor command to ensure all skills, submodules, and paths are healthy:

```bash
superai-skills doctor
superai-skills list-mcp
superai-skills list-skills
```

---

### Expected Outcome:
- All 14 MCP server submodules present in `packages/`
- All 35+ skills symlinked or copied into `~/.claude/skills`, `~/.cursor/skills`, `~/.codex/skills`, and `~/.gemini/config/skills`
- Executable commands available globally: `superai-skills` and `super-skills`
