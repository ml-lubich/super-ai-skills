"""Install iTerm2 and add a non-destructive 'SuperAI' Dynamic Profile.

iTerm2 auto-loads DynamicProfiles/*.json and never overwrites the user's own profiles.
We only ever write our own file (superai-skills.json); delete it to undo.
"""

import json
import shutil
import sys
from pathlib import Path

from super_ai_skills.plugins import Result, _run

GUID = "6f1c2a3e-5a1e-4c2b-9a47-5355504552414"  # stable; never change or the default breaks
PROFILE_REL = Path("Library/Application Support/iTerm2/DynamicProfiles/superai-skills.json")

# Tokyo Night (https://github.com/enkia/tokyo-night-vscode-theme)
_ANSI = ["15161e", "f7768e", "9ece6a", "e0af68", "7aa2f7", "bb9af7", "7dcfff", "a9b1d6",
         "414868", "f7768e", "9ece6a", "e0af68", "7aa2f7", "bb9af7", "7dcfff", "c0caf5"]


def _color(hexstr):
    r, g, b = (int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return {"Red Component": r, "Green Component": g, "Blue Component": b,
            "Alpha Component": 1, "Color Space": "sRGB"}


def build_profile():
    p = {
        "Name": "SuperAI",
        "Guid": GUID,
        "Normal Font": "MesloLGS-NF-Regular 13",  # Nerd Font for powerlevel10k
        "Scrollback Lines": 10000,
        "Unlimited Scrollback": False,
        "Option Key Sends": 2,  # Esc+
        "Right Option Key Sends": 2,
        "Silence Bell": True,
        "Custom Directory": "Recycle",
        "Foreground Color": _color("c0caf5"),
        "Background Color": _color("1a1b26"),
        "Cursor Color": _color("c0caf5"),
        "Cursor Text Color": _color("1a1b26"),
        "Selection Color": _color("33467c"),
        "Selected Text Color": _color("c0caf5"),
    }
    for i, h in enumerate(_ANSI):
        p[f"Ansi {i} Color"] = _color(h)
    return {"Profiles": [p]}


def install_iterm2(dry_run=False, runner=_run, home=None, which=shutil.which,
                   platform=sys.platform, system_apps=Path("/Applications")):
    cmd = ["brew", "install", "--cask", "iterm2"]
    if platform != "darwin":
        return Result("iterm2", "skip", "iTerm2 is macOS only")
    home = Path(home) if home else Path.home()
    if any((d / "iTerm.app").exists() for d in (Path(system_apps), home / "Applications")):
        return Result("iterm2", "skip", "already installed")
    if dry_run:
        return Result("iterm2", "dry-run", " ".join(cmd))
    if not which("brew"):
        return Result("iterm2", "fail", "Homebrew (`brew`) not found on PATH; install it from https://brew.sh")
    if runner(cmd) != 0:
        return Result("iterm2", "fail", " ".join(cmd))
    return Result("iterm2", "ok")


def apply_iterm_profile(dry_run=False, runner=_run, home=None, which=shutil.which,
                        make_default=False, platform=sys.platform, system_apps=None):
    home = Path(home) if home else Path.home()
    path = home / PROFILE_REL
    content = json.dumps(build_profile(), indent=2) + "\n"
    default_cmd = ["defaults", "write", "com.googlecode.iterm2", "Default Bookmark Guid", GUID]
    if dry_run:
        extra = f"; {' '.join(default_cmd)}" if make_default else ""
        return Result("iterm-profile", "dry-run", f"write {path}{extra}")
    current = path.read_text() if path.exists() else None
    if current == content and not make_default:
        return Result("iterm-profile", "skip", "SuperAI profile already up to date")
    if current != content:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    if make_default and runner(default_cmd) != 0:
        return Result("iterm-profile", "fail", " ".join(default_cmd))
    return Result("iterm-profile", "ok",
                  f"wrote {path}; pick 'SuperAI' from iTerm2's Profiles menu"
                  + ("" if make_default else " (not set as default)")
                  + "; delete that file to undo")
