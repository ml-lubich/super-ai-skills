import re

from click.testing import CliRunner

from super_ai_skills.cli import cli
from super_ai_skills.tools import install_tools, is_auto, load_tools

TOOLS = load_tools()
ACTIONABLE = [t for t in TOOLS if t["kind"] != "reference"]
NEVER_RUN = {"github-mcp", "firecrawl-mcp", "multica", "gstack", "vibe-kanban"}


class Rec:
    def __init__(self, ok=True):
        self.calls, self.ok = [], ok

    def __call__(self, argv):
        self.calls.append(argv)
        return self.ok


def test_manifest_fields():
    assert TOOLS
    for t in TOOLS:
        assert t["name"] and t["kind"] in {"cli", "mcp", "skill", "reference"}
        if t["kind"] == "reference":
            assert t["url"].startswith("https://github.com/")
        else:
            assert t["install"] and t["tier"] in {"default", "optional"}
    assert len({t["name"] for t in TOOLS}) == len(TOOLS)


def test_expected_default_tier():
    default = {t["name"] for t in ACTIONABLE if t["tier"] == "default"}
    assert default == {"rtk", "headroom", "serena", "codegraph", "graphify", "repomix", "claude-code-router", "playwright-mcp"}


def test_default_tier_is_safe():
    for t in ACTIONABLE:
        if t["tier"] == "default":
            assert is_auto(t)
            assert not re.search(r"curl|\||KEY|TOKEN", " ".join(t["install"]))


def test_no_ecc():
    text = open("tools.toml").read().lower()
    assert "ecc" not in re.findall(r"\b\w+\b", text)
    assert "everything-claude-code" not in text


def test_secret_and_curl_never_run_even_with_all():
    rec = Rec()
    res = install_tools("all", runner=rec, which=lambda b: None if b not in {"brew", "uv", "npm", "claude"} else "/bin/" + b, out=lambda s: None)
    assert {n for n, s in res.items() if s == "manual"} == NEVER_RUN
    ran = [" ".join(c) for c in rec.calls]
    assert not any(re.search(r"curl|GITHUB_PAT|FIRECRAWL|setup|vibe-kanban", c) for c in ran)


def test_dry_run_runs_nothing():
    rec = Rec()
    res = install_tools("all", dry_run=True, runner=rec, which=lambda b: "/bin/x" if b in {"brew", "uv", "npm", "claude"} else None, out=lambda s: None)
    assert rec.calls == []
    assert res["rtk"] == "dry-run"


def test_already_installed_skipped():
    rec = Rec()
    res = install_tools("default", runner=rec, which=lambda b: "/bin/" + b, out=lambda s: None)
    assert res["rtk"] == "already present" and res["codegraph"] == "already present"
    assert res["playwright-mcp"] == "installed"  # no binary to probe
    assert ["brew", "install", "rtk"] not in rec.calls


def test_missing_prereq_skipped_and_failure_reported():
    rec = Rec()
    res = install_tools("default", runner=rec, which=lambda b: None, out=lambda s: None)
    assert rec.calls == [] and res["rtk"] == "skipped (needs brew)"
    res = install_tools("default", runner=Rec(ok=False), which=lambda b: "/bin/x" if b == "brew" else None, out=lambda s: None)
    assert res["repomix"] == "failed"


def test_default_tier_excludes_optional():
    res = install_tools("default", dry_run=True, which=lambda b: None, out=lambda s: None)
    assert "cc-switch" not in res and "github-mcp" not in res


def test_cli_help_and_commands():
    r = CliRunner()
    for args in (["-h"], ["--help"], ["install-tools", "-h"], ["list-tools", "-h"], ["setup-dev", "-h"], ["doctor", "-h"]):
        assert r.invoke(cli, args).exit_code == 0
    out = r.invoke(cli, ["install-tools", "--dry-run", "--tier", "all"])
    assert out.exit_code == 0 and "run manually" in out.output
    assert r.invoke(cli, ["list-tools"]).exit_code == 0
    d = r.invoke(cli, ["doctor"])
    assert d.exit_code == 0 and "rtk" in d.output


def test_setup_dev_dry_run_runs_nothing(monkeypatch):
    import subprocess
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("ran")))
    assert CliRunner().invoke(cli, ["setup-dev", "--dry-run"]).exit_code == 0
