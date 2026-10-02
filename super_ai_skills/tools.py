"""Popular CLI/MCP add-ons, driven by tools.toml (skip-if-installed, dry-run, print-only unsafe)."""

import os
import re
import shutil
import subprocess
import sys
from typing import Callable, Dict, List, Optional

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

TOOLS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools.toml")

# curl|bash, or anything that carries a secret/placeholder, is never executed.
_UNSAFE = re.compile(r"curl|wget|\|\s*(ba|z)?sh|\$[A-Z_{]|API_KEY|TOKEN|SECRET|PASSWORD", re.I)


def load_tools(path: str = TOOLS_FILE) -> List[dict]:
    with open(path, "rb") as f:
        return tomllib.load(f)["tool"]


def is_unsafe(tool: dict) -> bool:
    return bool(_UNSAFE.search(" ".join(tool.get("install", []))))


def is_auto(tool: dict) -> bool:
    """Runs automatically only if not flagged manual and not unsafe."""
    return tool.get("auto", True) and not is_unsafe(tool)


def _default_runner(argv: List[str]) -> bool:
    try:
        subprocess.run(argv, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_tools(
    tier: str = "default",
    dry_run: bool = False,
    runner: Callable[[List[str]], bool] = _default_runner,
    which: Callable[[str], Optional[str]] = shutil.which,
    out: Callable[[str], None] = print,
    tools: Optional[List[dict]] = None,
) -> Dict[str, str]:
    """Install tools of the tier ('default' or 'all'). Returns name -> status."""
    result: Dict[str, str] = {}
    for t in tools if tools is not None else load_tools():
        if t["kind"] == "reference":
            continue
        if tier == "default" and t["tier"] != "default":
            continue
        name, cmd = t["name"], " ".join(t["install"])
        if t.get("check") and which(t["check"]):
            result[name] = "already present"
        elif not is_auto(t):
            out(f"{name}: run manually -> {cmd}")
            result[name] = "manual"
        elif t.get("needs") and not which(t["needs"]):
            result[name] = f"skipped (needs {t['needs']})"
        elif dry_run:
            out(f"{name}: would run -> {cmd}")
            result[name] = "dry-run"
        else:
            out(f"{name}: {cmd}")
            result[name] = "installed" if runner(t["install"]) else "failed"
    return result
