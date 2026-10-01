"""Environment and dependency management using Python and standard libraries."""

import sys
import os
import shutil
import subprocess
import urllib.request
from typing import List, Optional, Dict
from rich.console import Console
from rich.table import Table

console = Console()


class EnvironmentManager:
    """Manages system tools, package managers, and developer runtimes cleanly via Python."""

    # Full brew tool list for macOS
    BREW_TOOLS: List[str] = [
        "gh", "git", "jq", "node", "bun", "ffmpeg",
        "ripgrep", "fd", "fzf", "bat", "zoxide", "starship",
        "tmux", "mise", "watchman",
    ]

    # AI CLIs: (command_name, npm_package)
    AI_CLIS: List[tuple] = [
        ("claude", "@anthropic-ai/claude-code"),
        ("gemini", "@google-deepmind/gemini-cli"),
        ("codex", "@openai/codex"),
    ]

    # uv tools to install globally
    UV_TOOLS: List[str] = ["httpie", "rich-cli"]

    # Linux apt equivalents (best-effort)
    APT_PACKAGES: List[str] = [
        "git", "curl", "jq", "build-essential",
        "python3-pip", "ripgrep", "fd-find", "fzf", "bat",
        "tmux", "watchman",
    ]

    def __init__(self):
        self.platform = sys.platform
        self.is_mac = self.platform == "darwin"
        self.is_linux = self.platform.startswith("linux")
        # Track install results for summary: name -> "installed" | "already present" | "failed"
        self._summary: Dict[str, str] = {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def check_command(self, cmd: str) -> bool:
        """Check if an executable is present in PATH."""
        return shutil.which(cmd) is not None

    def _run(self, args: List[str], **kwargs) -> bool:
        """Run a subprocess, return True on success."""
        try:
            subprocess.run(args, check=True, **kwargs)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            console.print(f"[red]Command failed ({args[0]}): {exc}[/red]")
            return False

    def _mark(self, name: str, status: str) -> None:
        self._summary[name] = status

    # ------------------------------------------------------------------
    # uv
    # ------------------------------------------------------------------

    def ensure_uv(self) -> bool:
        """Ensure Astral uv is installed."""
        if self.check_command("uv"):
            console.print("[green]✓[/green] uv already installed")
            self._mark("uv", "already present")
            return True
        console.print("[cyan]Installing uv (fast Python installer)...[/cyan]")
        try:
            script_url = "https://astral.sh/uv/install.sh"
            with urllib.request.urlopen(script_url) as resp:
                installer = resp.read().decode("utf-8")
            result = subprocess.run(["sh"], input=installer.encode(), check=True)
            self._mark("uv", "installed")
            return True
        except Exception as e:
            console.print(f"[red]Failed to install uv: {e}[/red]")
            self._mark("uv", "failed")
            return False

    # ------------------------------------------------------------------
    # Python 3.13
    # ------------------------------------------------------------------

    def setup_python(self) -> bool:
        """Install Python 3.13 via uv if not already available."""
        try:
            out = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True
            )
            if "3.13" in out.stdout:
                console.print("[green]✓[/green] Python 3.13 already active")
                self._mark("python3.13", "already present")
                return True
        except FileNotFoundError:
            pass

        console.print("[cyan]Installing Python 3.13 via uv...[/cyan]")
        ok = self._run(["uv", "python", "install", "3.13", "--preview"])
        self._mark("python3.13", "installed" if ok else "failed")
        return ok

    # ------------------------------------------------------------------
    # macOS
    # ------------------------------------------------------------------

    def setup_macos(self, tools: Optional[List[str]] = None) -> None:
        """Provision developer tools on macOS using Homebrew."""
        if tools is None:
            tools = self.BREW_TOOLS

        if not self.check_command("brew"):
            console.print("[yellow]Homebrew not found. Install from https://brew.sh then re-run.[/yellow]")
            return

        for tool in tools:
            if self.check_command(tool):
                console.print(f"[green]✓[/green] {tool} already installed")
                self._mark(tool, "already present")
            else:
                console.print(f"[cyan]Installing {tool} via brew...[/cyan]")
                ok = self._run(["brew", "install", tool])
                self._mark(tool, "installed" if ok else "failed")

    # ------------------------------------------------------------------
    # Linux
    # ------------------------------------------------------------------

    def setup_linux(self, packages: Optional[List[str]] = None) -> None:
        """Provision developer tools on Linux via native package managers."""
        if packages is None:
            packages = self.APT_PACKAGES

        if self.check_command("apt-get"):
            console.print("[cyan]Updating apt and installing packages...[/cyan]")
            self._run(["sudo", "apt-get", "update", "-y"])
            self._run(["sudo", "apt-get", "install", "-y"] + packages)
            for pkg in packages:
                self._mark(pkg, "installed")
        elif self.check_command("dnf"):
            console.print("[cyan]Installing packages via dnf...[/cyan]")
            self._run(["sudo", "dnf", "install", "-y", "git", "curl", "jq", "python3-pip"])
        elif self.check_command("pacman"):
            console.print("[cyan]Installing packages via pacman...[/cyan]")
            self._run(["sudo", "pacman", "-Sy", "--noconfirm", "git", "curl", "jq"])

        if not self.check_command("bun"):
            console.print("[cyan]Installing bun...[/cyan]")
            ok = self._run(["sh", "-c", "curl -fsSL https://bun.sh/install | bash"])
            self._mark("bun", "installed" if ok else "failed")
        else:
            self._mark("bun", "already present")

    # ------------------------------------------------------------------
    # AI CLIs
    # ------------------------------------------------------------------

    def setup_ai_clis(self) -> None:
        """Install claude, gemini, and codex CLIs via bun (or npm fallback)."""
        installer = "bun" if self.check_command("bun") else ("npm" if self.check_command("npm") else None)
        if installer is None:
            console.print("[yellow]Neither bun nor npm found — skipping AI CLI installs.[/yellow]")
            return

        add_cmd = "add" if installer == "bun" else "install"

        for cli, package in self.AI_CLIS:
            if self.check_command(cli):
                console.print(f"[green]✓[/green] {cli} already installed")
                self._mark(cli, "already present")
            else:
                console.print(f"[cyan]Installing {cli} ({package}) via {installer}...[/cyan]")
                ok = self._run([installer, add_cmd, "-g", package])
                self._mark(cli, "installed" if ok else "failed")

    # ------------------------------------------------------------------
    # uv tools
    # ------------------------------------------------------------------

    def setup_uv_tools(self) -> None:
        """Install global uv tools (httpie, rich-cli, etc.)."""
        # Install superai-skills itself in editable mode
        repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        console.print("[cyan]Installing superai-skills (editable)...[/cyan]")
        ok = self._run(["uv", "tool", "install", "--editable", repo_root])
        self._mark("superai-skills (editable)", "installed" if ok else "failed")

        for tool in self.UV_TOOLS:
            if self.check_command(tool):
                console.print(f"[green]✓[/green] {tool} (uv tool) already installed")
                self._mark(f"uv:{tool}", "already present")
            else:
                console.print(f"[cyan]Installing {tool} via uv tool...[/cyan]")
                ok = self._run(["uv", "tool", "install", tool])
                self._mark(f"uv:{tool}", "installed" if ok else "failed")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def print_summary(self) -> None:
        """Print a rich checklist table of what was installed vs already present."""
        table = Table(title="Bootstrap Summary", show_header=True, header_style="bold magenta")
        table.add_column("Tool / Package", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")

        status_styles = {
            "installed": "[bold green]✓ installed[/bold green]",
            "already present": "[green]✓ already present[/green]",
            "failed": "[bold red]✗ failed[/bold red]",
        }

        for name, status in sorted(self._summary.items()):
            table.add_row(name, status_styles.get(status, status))

        console.print(table)

        failed = [n for n, s in self._summary.items() if s == "failed"]
        if failed:
            console.print(f"\n[bold red]⚠ {len(failed)} item(s) failed:[/bold red] {', '.join(failed)}")
        else:
            console.print("\n[bold green]✓ All items installed or already present![/bold green]")

    # ------------------------------------------------------------------
    # Bootstrap entry point
    # ------------------------------------------------------------------

    def bootstrap(self) -> None:
        """Run full cross-platform AI super-developer environment setup."""
        console.print(f"[bold cyan]Bootstrapping AI super-developer workstation on {self.platform}...[/bold cyan]\n")

        # 1. uv first (needed for python install + uv tools)
        self.ensure_uv()

        # 2. System tools
        if self.is_mac:
            self.setup_macos()
        elif self.is_linux:
            self.setup_linux()

        # 3. Python 3.13
        self.setup_python()

        # 4. AI CLIs (claude, gemini, codex)
        self.setup_ai_clis()

        # 5. uv tools
        self.setup_uv_tools()

        # 6. Print summary
        console.print()
        self.print_summary()
