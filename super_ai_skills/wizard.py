"""Guided setup wizard: explain each step, mark it (recommended)/(optional), let the user say no."""

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence

import click

from super_ai_skills.plugins import Result

# Result.status values: ok | skip (already present) | fail | dry-run | unsupported | declined
SUMMARY_GROUPS = [
    ("done", "ok"),
    ("skipped by you", "declined"),
    ("skipped, already present", "skip"),
    ("not applicable here", "unsupported"),
    ("failed", "fail"),
    ("planned (dry-run)", "dry-run"),
]


@dataclass
class Step:
    key: str
    title: str
    why: str
    recommended: bool
    default_yes: bool
    run: Callable[[bool], Result]
    ask: bool = True  # False: runs without a prompt (doctor)


def select_steps(steps: Sequence[Step], only: Optional[Iterable[str]] = None,
                 skip: Optional[Iterable[str]] = None) -> List[Step]:
    keys = {s.key for s in steps}
    only_set, skip_set = set(only or ()), set(skip or ())
    unknown = (only_set | skip_set) - keys
    if unknown:
        raise ValueError(f"unknown step(s): {', '.join(sorted(unknown))}; valid: {', '.join(s.key for s in steps)}")
    return [s for s in steps if (not only_set or s.key in only_set) and s.key not in skip_set]


def _hints(by_key: dict) -> List[str]:
    ok = lambda k: by_key.get(k) in ("ok", "skip")  # noqa: E731
    hints = []
    if any(ok(k) for k in ("ohmyzsh", "powerlevel10k", "zsh-plugins")):
        hints.append("Restart your shell (exec zsh) to load oh-my-zsh and its plugins.")
    if ok("powerlevel10k"):
        hints.append("Run `p10k configure` to pick your prompt style.")
    if ok("iterm2"):
        hints.append("Open iTerm2 to use the new profile (font: MesloLGS NF).")
    return hints


def run_wizard(steps: Sequence[Step], yes: bool = False, no_input: bool = False,
               only: Optional[Iterable[str]] = None, skip: Optional[Iterable[str]] = None,
               dry_run: bool = False, prompt: Callable[..., bool] = click.confirm,
               echo: Callable[[str], None] = click.echo) -> List[Result]:
    chosen = select_steps(steps, only, skip)
    auto = yes or no_input
    echo("superai-skills setup wizard")
    echo("Each step is explained first; answer n to skip any of them. Safe to re-run.")
    if dry_run:
        echo("(dry-run: nothing will be changed)")
    results: List[Result] = []
    for n, step in enumerate(chosen, 1):
        tag = "recommended" if step.recommended else "optional"
        echo(f"\nStep {n}/{len(chosen)}: {step.title} ({tag})")
        echo(f"  {step.why}")
        if not dry_run and step.ask:
            go = step.recommended if auto else prompt("Install?", default=step.default_yes)
            if not go:
                res = Result(step.key, "declined", "skipped by you")
                echo("  -> skipped")
                results.append(res)
                continue
        try:
            r = step.run(dry_run)
            res = Result(step.key, r.status, r.detail)
        except Exception as e:  # a failed step must not abort the rest
            res = Result(step.key, "fail", f"{type(e).__name__}: {e}")
        echo(f"  -> {res.status}{': ' + res.detail if res.detail else ''}")
        results.append(res)

    echo("\nSummary")
    for label, status in SUMMARY_GROUPS:
        names = [r.name for r in results if r.status == status]
        if names:
            echo(f"  {label}: {', '.join(names)}")
    if not dry_run:
        for h in _hints({r.name: r.status for r in results}):
            echo(f"  Next: {h}")
    return results
