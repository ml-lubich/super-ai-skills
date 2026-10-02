"""Shell setup: oh-my-zsh, powerlevel10k, zsh plugins.

Every ~/.zshrc edit lives in a managed block (see ensure_zshrc_block); the login shell is never changed.
The wizard asks consent before calling install_ohmyzsh, which runs the vendor installer.
"""

import os
import platform
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from super_ai_skills.plugins import Result

OMZ_URL = "https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh"
P10K_URL = "https://github.com/romkatv/powerlevel10k.git"
FONT_CASK = "font-meslo-lg-nerd-font"
THEME_LINE = 'ZSH_THEME="powerlevel10k/powerlevel10k"'
PLUGIN_REPOS = ["zsh-autosuggestions", "zsh-syntax-highlighting"]  # syntax-highlighting must stay last
_SOURCE_RE = re.compile(r"^\s*source\s+\$ZSH/oh-my-zsh\.sh\s*$", re.M)
_PLUGINS_RE = re.compile(r"^[ \t]*plugins=\(([^)]*)\)", re.M)


def _run(argv, env=None):
    return subprocess.run(argv, env={**os.environ, **(env or {})}).returncode


def _markers(key):
    return f"# >>> superai-skills:{key} >>>", f"# <<< superai-skills:{key} <<<"


def _block_re(key):
    start, end = _markers(key)
    return re.compile(re.escape(start) + r".*?" + re.escape(end) + r"\n?", re.S)


def _outside_blocks(text):
    return re.sub(r"# >>> superai-skills:(\w+) >>>.*?# <<< superai-skills:\1 <<<\n?", "", text, flags=re.S)


def ensure_zshrc_block(home, key, lines):
    """Write `lines` between superai-skills:<key> markers in ~/.zshrc; returns True if the file changed.

    Placement (oh-my-zsh reads ZSH_THEME/plugins when `source $ZSH/oh-my-zsh.sh` runs, and the last
    assignment wins): a new block goes immediately BEFORE that source line, i.e. after the user's own
    ZSH_THEME=/plugins=( lines, which are left untouched and never duplicated, so our override takes
    effect. With no such source line (custom .zshrc), the block is appended to the end. An existing
    block is replaced in place. The first changing edit makes ~/.zshrc.superai-backup-<stamp> once.
    """
    zshrc = Path(home) / ".zshrc"
    old = zshrc.read_text() if zshrc.exists() else ""
    start, end = _markers(key)
    block = "\n".join([start, *lines, end]) + "\n"
    rx = _block_re(key)
    if rx.search(old):
        new = rx.sub(lambda _: block, old, count=1)
    else:
        m = _SOURCE_RE.search(old)
        if m:
            new = old[:m.start()] + block + old[m.start():]
        else:
            new = old + ("" if not old or old.endswith("\n") else "\n") + block
    if new == old:
        return False
    if zshrc.exists() and not list(Path(home).glob(".zshrc.superai-backup-*")):
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        (Path(home) / f".zshrc.superai-backup-{stamp}").write_text(old)
    zshrc.write_text(new)
    return True


def _missing(which, *names):
    return [n for n in names if not which(n)]


def install_ohmyzsh(dry_run=False, runner=_run, home=None, which=shutil.which):
    home = Path(home or Path.home())
    if (home / ".oh-my-zsh").exists():
        return Result("oh-my-zsh", "skip", "~/.oh-my-zsh already exists")
    argv = ["sh", "-c", f'sh -c "$(curl -fsSL {OMZ_URL})"']
    env = {"RUNZSH": "no", "CHSH": "no", "KEEP_ZSHRC": "yes"}
    if dry_run:
        return Result("oh-my-zsh", "dry-run", "RUNZSH=no CHSH=no KEEP_ZSHRC=yes " + argv[-1])
    miss = _missing(which, "git", "zsh")
    if miss:
        return Result("oh-my-zsh", "fail", f"missing on PATH: {', '.join(miss)}")
    if runner(argv, env=env) != 0:
        return Result("oh-my-zsh", "fail", "oh-my-zsh installer failed")
    return Result("oh-my-zsh", "ok", "installed; login shell unchanged")


def _fonts_dir_has_meslo(home):
    fonts = home / "Library" / "Fonts"
    return fonts.is_dir() and any(fonts.glob("Meslo*"))


def install_powerlevel10k(dry_run=False, runner=_run, home=None, which=shutil.which):
    home = Path(home or Path.home())
    omz = home / ".oh-my-zsh"
    dest = omz / "custom" / "themes" / "powerlevel10k"
    if dest.exists():
        return Result("powerlevel10k", "skip", "theme already cloned")
    if dry_run:
        return Result("powerlevel10k", "dry-run",
                      f"git clone --depth=1 {P10K_URL} {dest}; brew install --cask {FONT_CASK}; set {THEME_LINE}")
    if not omz.exists():
        return Result("powerlevel10k", "fail", "oh-my-zsh not installed; install it first")
    if _missing(which, "git"):
        return Result("powerlevel10k", "fail", "missing on PATH: git")
    font_needed = False
    if platform.system() == "Darwin" and not _fonts_dir_has_meslo(home):
        if not which("brew"):
            return Result("powerlevel10k", "fail",
                          "brew not found; install Homebrew or install a Meslo Nerd Font manually")
        font_needed = runner(["brew", "list", "--cask", FONT_CASK]) != 0
    if runner(["git", "clone", "--depth=1", P10K_URL, str(dest)]) != 0:
        return Result("powerlevel10k", "fail", "git clone powerlevel10k failed")
    if font_needed and runner(["brew", "install", "--cask", FONT_CASK]) != 0:
        return Result("powerlevel10k", "fail", f"brew install --cask {FONT_CASK} failed")
    ensure_zshrc_block(home, "p10k", [THEME_LINE])
    return Result("powerlevel10k", "ok",
                  "installed; run `p10k configure` to pick a style and set your terminal font to MesloLGS NF")


def install_zsh_plugins(dry_run=False, runner=_run, home=None, which=shutil.which):
    home = Path(home or Path.home())
    omz = home / ".oh-my-zsh"
    base = omz / "custom" / "plugins"
    if dry_run:
        return Result("zsh-plugins", "dry-run",
                      "git clone zsh-users/" + ", zsh-users/".join(PLUGIN_REPOS) + f" into {base}")
    if not omz.exists():
        return Result("zsh-plugins", "fail", "oh-my-zsh not installed; install it first")
    if _missing(which, "git"):
        return Result("zsh-plugins", "fail", "missing on PATH: git")
    cloned = []
    for name in PLUGIN_REPOS:
        if (base / name).exists():
            continue
        url = f"https://github.com/zsh-users/{name}.git"
        if runner(["git", "clone", "--depth=1", url, str(base / name)]) != 0:
            return Result("zsh-plugins", "fail", f"git clone {name} failed")
        cloned.append(name)
    zshrc = home / ".zshrc"
    text = _outside_blocks(zshrc.read_text()) if zshrc.exists() else ""
    found = _PLUGINS_RE.findall(text)
    existing = re.sub(r"#[^\n]*", "", found[-1]).split() if found else ["git"]
    plugins = [p for p in existing if p not in PLUGIN_REPOS] + PLUGIN_REPOS
    changed = ensure_zshrc_block(home, "plugins", [f"plugins=({' '.join(plugins)})"])
    if not cloned and not changed:
        return Result("zsh-plugins", "skip", "already installed and configured")
    return Result("zsh-plugins", "ok", f"plugins=({' '.join(plugins)}); restart your shell")
