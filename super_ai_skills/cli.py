"""CLI interface for super-ai-skills."""

import os
import sys
import subprocess
import shutil
import click
from rich.console import Console
from rich.table import Table

console = Console()

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILLS_DIR = os.path.join(ROOT_DIR, "skills")
PACKAGES_DIR = os.path.join(ROOT_DIR, "packages")

@click.group()
def cli():
    """Universal Super AI Skills & MCP Suite for macOS, Linux, and Cloud."""
    pass

@cli.command("list-skills")
def list_skills():
    """List all available agent skills."""
    if not os.path.exists(SKILLS_DIR):
        console.print("[red]Skills directory not found![/red]")
        return
    table = Table(title="Available AI Agent Skills")
    table.add_column("Skill Name", style="cyan bold")
    table.add_column("Status", style="green")
    table.add_column("Path", style="dim")

    for item in sorted(os.listdir(SKILLS_DIR)):
        skill_path = os.path.join(SKILLS_DIR, item)
        if os.path.isdir(skill_path):
            table.add_row(item, "Ready", skill_path)
    console.print(table)

@cli.command("list-mcp")
def list_mcp():
    """List bundled MCP server packages."""
    if not os.path.exists(PACKAGES_DIR):
        console.print("[red]Packages directory not found![/red]")
        return
    table = Table(title="Bundled MCP Servers & Packages")
    table.add_column("Package Name", style="magenta bold")
    table.add_column("Type", style="yellow")
    table.add_column("Status", style="green")

    for item in sorted(os.listdir(PACKAGES_DIR)):
        pkg_path = os.path.join(PACKAGES_DIR, item)
        if os.path.isdir(pkg_path):
            is_mcp = "MCP Server" if "mcp" in item else "Tool / Submodule"
            table.add_row(item, is_mcp, "Installed / Linked")
    console.print(table)

@cli.command("install-skills")
@click.option("--target", type=click.Choice(["claude", "cursor", "codex", "gemini", "all"]), default="all", help="Target agent client")
def install_skills(target):
    """Link or copy skills to target client directories."""
    home = os.path.expanduser("~")
    destinations = {
        "claude": os.path.join(home, ".claude", "skills"),
        "cursor": os.path.join(home, ".cursor", "skills"),
        "codex": os.path.join(home, ".codex", "skills"),
        "gemini": os.path.join(home, ".gemini", "config", "skills"),
    }
    
    targets = [target] if target != "all" else list(destinations.keys())

    for t in targets:
        dest_dir = destinations[t]
        os.makedirs(dest_dir, exist_ok=True)
        console.print(f"[bold green]Installing skills to {t} ({dest_dir})...[/bold green]")
        for item in sorted(os.listdir(SKILLS_DIR)):
            src = os.path.join(SKILLS_DIR, item)
            dst = os.path.join(dest_dir, item)
            if not os.path.isdir(src):
                continue
            if not os.path.exists(dst):
                try:
                    os.symlink(src, dst)
                    console.print(f"  [cyan]+ Symlinked {item}[/cyan]")
                except OSError:
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    console.print(f"  [cyan]+ Copied {item}[/cyan]")
            else:
                console.print(f"  [dim]- Already present: {item}[/dim]")

    console.print("\n[bold green]✓ Skills successfully installed across targets![/bold green]")

@cli.command("setup-dev")
def setup_dev():
    """Run full developer environment bootstrap (Python-native EnvironmentManager)."""
    from super_ai_skills.env import EnvironmentManager
    mgr = EnvironmentManager()
    mgr.bootstrap()

@cli.command("doctor")
def doctor():
    """Run health check and environment diagnostics."""
    console.print(f"[bold]Platform:[/bold] {sys.platform}")
    console.print(f"[bold]Python:[/bold] {sys.version.split()[0]}")
    console.print(f"[bold]Root Dir:[/bold] {ROOT_DIR}")
    skills_count = len(os.listdir(SKILLS_DIR)) if os.path.exists(SKILLS_DIR) else 0
    pkgs_count = len(os.listdir(PACKAGES_DIR)) if os.path.exists(PACKAGES_DIR) else 0
@cli.command("voice-learn")
@click.argument("text")
@click.option("--context", default="general", help="Context tag (e.g. outreach, reply, email)")
def voice_learn(text, context):
    """Learn authentic human tone, style, and sentence rhythm from a real sample."""
    from super_ai_skills.voice import VoiceLearner
    vl = VoiceLearner()
    res = vl.learn_sample(text, context=context)
    console.print(f"[bold green]✓ Ingested sample:[/bold green] {res['word_count']} words, avg sentence length: {res['avg_sentence_len']} words")

@cli.command("voice-audit")
@click.argument("draft")
def voice_audit(draft):
    """Audit a draft against AI fluff/buzzwords and check character budget."""
    from super_ai_skills.voice import VoiceLearner
    vl = VoiceLearner()
    report = vl.audit_draft(draft)
    color = "green" if report["clean"] else "yellow"
    console.print(f"[{color}]Score: {report['score']}/100[/{color}] (Length: {report['char_count']} chars)")
    if not report["clean"]:
        console.print(f"[red]Flagged AI Fluff:[/red] {', '.join(report['flagged_ai_fluff'])}")
    else:
        console.print("[bold green]✓ Clean human voice — no AI tells detected.[/bold green]")

@cli.command("voice-rag")
@click.option("--limit", default=3, help="Number of few-shots to return")
def voice_rag(limit):
    """Retrieve learned few-shots for in-context RAG prompt grounding."""
    from super_ai_skills.voice import VoiceLearner
    vl = VoiceLearner()
    shots = vl.get_grounding_few_shots(limit=limit)
    if not shots:
        console.print("[dim]No voice samples learned yet. Use 'superai-skills voice-learn <sample>'[/dim]")
        return
    console.print("[bold cyan]In-Context Grounding Few-Shots:[/bold cyan]")
    for idx, s in enumerate(shots, 1):
        console.print(f"[bold]{idx}.[/bold] \"{s}\"")

def main():
    cli()

if __name__ == "__main__":
    main()
