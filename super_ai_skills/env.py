"""Environment and dependency management using Python and standard libraries."""

import sys
import os
import shutil
import subprocess
import urllib.request
from typing import List, Optional
from rich.console import Console

console = Console()

class EnvironmentManager:
    """Manages system tools, package managers, and developer runtimes cleanly via Python."""

    def __init__(self):
        self.platform = sys.platform
        self.is_mac = self.platform == "darwin"
        self.is_linux = self.platform.startswith("linux")

    def check_command(self, cmd: str) -> bool:
        """Check if an executable is present in PATH."""
        return shutil.which(cmd) is not None

    def ensure_uv(self) -> bool:
        """Ensure Astral uv is installed."""
        if self.check_command("uv"):
            console.print("[green]✓[/green] uv is installed")
            return True
        console.print("[cyan]Installing uv (fast Python installer)...[/cyan]")
        try:
            script_url = "https://astral.sh/uv/install.sh"
            with urllib.request.urlopen(script_url) as resp:
                installer = resp.read().decode("utf-8")
            subprocess.run([sys.executable, "-c", "import os, sys, subprocess; subprocess.run(['sh'], input=sys.stdin.read().encode())"], input=installer.encode(), check=True)
            return True
        except Exception as e:
            console.print(f"[red]Failed to install uv: {e}[/red]")
            return False

    def setup_macos(self, tools: Optional[List[str]] = None) -> None:
        """Provision developer tools on macOS using Homebrew via Python."""
        if tools is None:
            tools = ["gh", "git", "jq", "uv", "node", "ffmpeg"]

        if not self.check_command("brew"):
            console.print("[yellow]Homebrew not found. Please install Homebrew: https://brew.sh[/yellow]")
            return

        for tool in tools:
            if self.check_command(tool):
                console.print(f"[green]✓[/green] {tool} already installed")
            else:
                console.print(f"[cyan]Installing {tool} via brew...[/cyan]")
                subprocess.run(["brew", "install", tool], check=False)

    def setup_linux(self, packages: Optional[List[str]] = None) -> None:
        """Provision developer tools on Linux via native system package managers."""
        if packages is None:
            packages = ["git", "curl", "jq", "build-essential", "python3-pip"]

        if self.check_command("apt-get"):
            console.print("[cyan]Updating apt and installing packages...[/cyan]")
            subprocess.run(["sudo", "apt-get", "update", "-y"], check=False)
            subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=False)
        elif self.check_command("dnf"):
            console.print("[cyan]Installing packages via dnf...[/cyan]")
            subprocess.run(["sudo", "dnf", "install", "-y", "git", "curl", "jq", "python3-pip"], check=False)
        elif self.check_command("pacman"):
            console.print("[cyan]Installing packages via pacman...[/cyan]")
            subprocess.run(["sudo", "pacman", "-Sy", "--noconfirm", "git", "curl", "jq"], check=False)

    def bootstrap(self) -> None:
        """Run full cross-platform environment setup."""
        console.print(f"[bold cyan]Bootstrapping developer environment on {self.platform}...[/bold cyan]")
        if self.is_mac:
            self.setup_macos()
        elif self.is_linux:
            self.setup_linux()
        self.ensure_uv()
        console.print("[bold green]✓ Developer environment initialized successfully![/bold green]")
