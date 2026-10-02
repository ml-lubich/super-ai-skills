"""plugins.py: manifest, exclusions, skip-if-enabled, exact argv, missing claude."""

import json
import re

from super_ai_skills import plugins

DEFAULTS = {
    "oh-my-claudecode@omc",
    "superpowers@superpowers-dev",
    "ponytail@ponytail",
    "context7@context7-marketplace",
    "chrome-devtools-mcp@chrome-devtools-plugins",
    "claude-mem@thedotmack",
    "frontend-design@claude-plugins-official",
    "andrej-karpathy-skills@karpathy-skills",
    "mattpocock-skills@mattpocock",
    "agent-skills@addy-agent-skills",
    "taste-skill@taste-skill",
    "ui-ux-pro-max@ui-ux-pro-max-skill",
    "planning-with-files@planning-with-files",
    "caveman@caveman",
    "claude-hud@claude-hud",
}
OPTIONAL = {
    "vercel@claude-plugins-official",
    "sentry@claude-plugins-official",
    "sentry-cli@claude-plugins-official",
    "slack@claude-plugins-official",
    "claude-tiers@claude-tiers",
    "codex@openai-codex",
    "beads@beads-marketplace",
    "agentmemory@agentmemory",
    "document-skills@anthropic-agent-skills",
    "repomix-mcp@repomix",
}


class Recorder:
    def __init__(self, rc=0):
        self.calls = []
        self.rc = rc

    def __call__(self, argv):
        self.calls.append(argv)
        return self.rc


def settings(tmp_path, enabled):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"enabledPlugins": {k: True for k in enabled}}))
    return p


def run(tmp_path, tier="default", enabled=(), dry_run=False, rc=0, which=lambda _: "/bin/claude"):
    r = Recorder(rc)
    res = plugins.install_plugins(
        tier=tier, dry_run=dry_run, runner=r,
        settings_path=settings(tmp_path, enabled), which=which,
    )
    return r, res


def test_manifest_tiers():
    ms = plugins.load_manifest()
    assert {p["id"] for p in ms["plugin"] if p["tier"] == "default"} == DEFAULTS
    assert {p["id"] for p in ms["plugin"] if p["tier"] == "optional"} == OPTIONAL


def test_excluded_never_in_manifest_or_installed(tmp_path):
    ms = plugins.load_manifest()
    ids = {p["id"] for p in ms["plugin"]}
    repos = {p["repo"] for p in ms["plugin"]}
    assert not ids & set(ms["excluded"]["ids"])
    assert not repos & set(ms["excluded"]["repos"])
    r, _ = run(tmp_path, tier="all")
    flat = " ".join(" ".join(c) for c in r.calls)
    assert "scroll-craft" not in flat and "swift-lsp" not in flat and "ecc" not in flat.split()


def test_default_tier_excludes_optional(tmp_path):
    r, _ = run(tmp_path)
    flat = " ".join(" ".join(c) for c in r.calls)
    assert "vercel@" not in flat and "claude-tiers" not in flat


def test_all_tier_includes_optional(tmp_path):
    r, res = run(tmp_path, tier="all")
    assert len(res) == len(DEFAULTS | OPTIONAL)


def test_exact_argv(tmp_path):
    r, res = run(tmp_path)
    assert ["claude", "plugin", "marketplace", "add", "Yeachan-Heo/oh-my-claudecode"] in r.calls
    assert ["claude", "plugin", "install", "oh-my-claudecode@omc"] in r.calls
    assert all(x.status == "ok" for x in res)


def test_marketplace_added_once_per_repo(tmp_path):
    r, _ = run(tmp_path)
    adds = [c for c in r.calls if c[2:4] == ["marketplace", "add"]]
    assert len(adds) == len({c[4] for c in adds})


def test_already_enabled_skipped(tmp_path):
    r, res = run(tmp_path, enabled=["ponytail@ponytail"])
    assert ["claude", "plugin", "install", "ponytail@ponytail"] not in r.calls
    assert not any("DietrichGebert/ponytail" in c for c in r.calls)
    assert [x.status for x in res if x.name == "ponytail@ponytail"] == ["skip"]


def test_missing_settings_file_is_fine(tmp_path):
    r = Recorder()
    plugins.install_plugins(runner=r, settings_path=tmp_path / "nope.json", which=lambda _: "/bin/claude")
    assert r.calls


def test_dry_run_runs_nothing(tmp_path):
    r, res = run(tmp_path, dry_run=True)
    assert r.calls == []
    assert len(res) == len(DEFAULTS)
    assert all(x.status == "dry-run" for x in res)


def test_missing_claude_clear_fail(tmp_path):
    r, res = run(tmp_path, which=lambda _: None)
    assert r.calls == []
    assert len(res) == 1 and res[0].status == "fail" and "claude" in res[0].detail


def test_install_failure_reported(tmp_path):
    _, res = run(tmp_path, rc=1)
    assert all(x.status == "fail" for x in res)


def _plugins():
    return plugins.load_manifest()["plugin"]


def test_ids_well_formed_and_unique():
    ids = [p["id"] for p in _plugins()]
    assert len(ids) == len(set(ids))
    assert all(re.fullmatch(r"[a-z0-9._-]+@[a-z0-9._-]+", i) for i in ids)


def test_repos_owner_name_and_tiers_valid():
    for p in _plugins():
        assert re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9._-]+", p["repo"]), p
        assert p["tier"] in ("default", "optional"), p


def test_ecc_never_installable():
    ms = plugins.load_manifest()
    assert "ecc@ecc" in ms["excluded"]["ids"]
    bad = re.compile(r"(^|[^a-z0-9])ecc([^a-z0-9]|$)|everything-claude-code", re.I)
    for p in ms["plugin"]:
        assert not bad.search(p["id"]) and not bad.search(p["repo"]), p


def test_omc_is_default():
    assert {p["id"]: p["tier"] for p in _plugins()}["oh-my-claudecode@omc"] == "default"


def test_single_superpowers_entry():
    assert [p["id"] for p in _plugins() if p["id"].startswith("superpowers@")] == [
        "superpowers@superpowers-dev"
    ]
