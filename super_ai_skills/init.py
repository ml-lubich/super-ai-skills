"""`superai-skills init`: one idempotent command that sets up the whole workstation."""

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Mapping, Optional

from rich.console import Console

console = Console()

ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass
class Result:
    name: str
    status: str  # ok | skip | fail
    detail: str = ""


# --- Bitbucket detection ---------------------------------------------------
def detect_bitbucket(remotes: List[str], env: Mapping[str, str], bb_config_exists: bool) -> bool:
    """Pure: true if any remote mentions bitbucket, a BITBUCKET_*/BB_* env is set, or ~/.config/bb exists."""
    if any("bitbucket" in r.lower() for r in remotes):
        return True
    if any(k.startswith(("BITBUCKET_", "BB_")) for k in env):
        return True
    return bb_config_exists


def resolve_bitbucket(flag: Optional[bool], detected: bool) -> bool:
    return detected if flag is None else flag


def _git_urls(repo: Path) -> List[str]:
    # Read .git/config directly: no subprocess, so --dry-run stays side-effect free.
    cfg = repo / ".git" / "config"
    try:
        lines = cfg.read_text().splitlines()
    except OSError:
        return []
    return [ln.strip() for ln in lines if ln.strip().startswith("url")]


def detect_bitbucket_here() -> bool:
    home = Path.home()
    repos = [Path.cwd()]
    dev = home / "dev"
    if dev.is_dir():
        repos += [p for p in sorted(dev.iterdir()) if p.is_dir()]
    remotes = [u for r in repos for u in _git_urls(r)]
    return detect_bitbucket(remotes, os.environ, (home / ".config" / "bb").exists())


# --- Steps -------------------------------------------------------------------
def _setup_dev() -> Result:
    from super_ai_skills.env import EnvironmentManager
    EnvironmentManager().bootstrap()
    return Result("setup-dev", "ok")


def _bb() -> Result:
    subprocess.run(["uv", "tool", "install", str(ROOT_DIR / "packages" / "bitbucket-cli")], check=True)
    return Result("bb", "ok")


def _plugins(tier: str = "default") -> Result:
    from super_ai_skills import plugins  # WP3
    results = plugins.install(tier, False)
    bad = [r for r in results if getattr(r, "status", "ok") == "fail"]
    return Result("plugins", "fail" if bad else "ok", "; ".join(str(getattr(r, "detail", r)) for r in bad))


def _tools() -> Result:
    from super_ai_skills.tools import install_tools
    res = install_tools("default", False, out=console.print)
    bad = [n for n, st in res.items() if st == "failed"]
    return Result("tools", "fail" if bad else "ok", ", ".join(bad))


def _skills() -> Result:
    from super_ai_skills.cli import install_skills
    install_skills.callback("all")
    return Result("skills", "ok")


def _brain(daemon: bool = False) -> Result:
    from super_ai_skills import brain_setup  # WP5
    r = brain_setup.install(False, daemon)
    return Result("brain", getattr(r, "status", "ok"), str(getattr(r, "detail", "")))


def _doctor() -> Result:
    from super_ai_skills.cli import doctor
    doctor.callback()
    return Result("doctor", "ok")


def run_init(dry_run: bool, bitbucket: Optional[bool], with_brain_daemon: bool, skip_plugins: bool) -> List[Result]:
    use_bb = resolve_bitbucket(bitbucket, detect_bitbucket_here() if bitbucket is None else False)
    steps: List[tuple] = [("setup-dev", _setup_dev)]
    if use_bb:
        steps.append(("bb", _bb))
    if not skip_plugins:
        steps.append(("plugins", _plugins))
    steps.append(("tools", _tools))
    steps += [("skills", _skills), ("brain", lambda: _brain(with_brain_daemon)), ("doctor", _doctor)]

    results = []
    for name, fn in steps:
        if dry_run:
            res = Result(name, "skip", "dry-run: would run")
        else:
            try:
                res = fn()
            except Exception as e:  # a failed step must not abort the rest; exit code reports it
                res = Result(name, "fail", f"{type(e).__name__}: {e}")
        color = {"ok": "green", "skip": "yellow", "fail": "red"}.get(res.status, "white")
        console.print(f"[{color}]{res.status:<4}[/{color}] {name} {res.detail}".rstrip(), markup=True)
        results.append(res)
    if not use_bb:
        console.print("[yellow]skip[/yellow] bb (no Bitbucket detected; force with --bitbucket)")
    return results
