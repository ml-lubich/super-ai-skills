"""Install Claude Code plugins from plugins.toml via the `claude plugin` CLI.

Never edits settings.json; only reads it to skip already-enabled plugins.
"""

import json
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path

MANIFEST = Path(__file__).resolve().parent.parent / "plugins.toml"
SETTINGS = Path.home() / ".claude" / "settings.json"


@dataclass
class Result:
    name: str
    status: str  # ok | skip | fail | dry-run
    detail: str = ""


def load_manifest(path=MANIFEST):
    with open(path, "rb") as f:
        return tomllib.load(f)


def _run(argv):
    return subprocess.run(argv, capture_output=True, text=True).returncode


def _enabled(settings_path):
    try:
        data = json.loads(Path(settings_path).read_text())
    except FileNotFoundError:
        return set()
    return {k for k, v in data.get("enabledPlugins", {}).items() if v}


def install_plugins(tier="default", dry_run=False, runner=_run,
                    settings_path=SETTINGS, which=shutil.which):
    """tier: 'default' or 'all' (default + optional). Returns one Result per plugin."""
    manifest = load_manifest()
    excluded = set(manifest["excluded"]["ids"])
    wanted = [p for p in manifest["plugin"]
              if p["id"] not in excluded and (tier == "all" or p["tier"] == "default")]
    if not dry_run and not which("claude"):
        return [Result("claude", "fail", "`claude` CLI not found on PATH; install Claude Code first")]
    enabled = _enabled(settings_path)
    added, results = set(), []
    for p in wanted:
        if p["id"] in enabled:
            results.append(Result(p["id"], "skip", "already enabled"))
            continue
        steps = []
        if p["repo"] not in added:
            steps.append(["claude", "plugin", "marketplace", "add", p["repo"]])
        steps.append(["claude", "plugin", "install", p["id"]])
        if dry_run:
            results.append(Result(p["id"], "dry-run", "; ".join(" ".join(s) for s in steps)))
            continue
        for s in steps:
            if runner(s) != 0:
                results.append(Result(p["id"], "fail", " ".join(s)))
                break
            if s[3:4] == ["add"]:
                added.add(p["repo"])
        else:
            results.append(Result(p["id"], "ok"))
    return results
