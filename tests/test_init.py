import subprocess

import pytest
from click.testing import CliRunner

from super_ai_skills import init as init_mod
from super_ai_skills.cli import cli

STEP_FNS = ["_setup_dev", "_bb", "_plugins", "_skills", "_brain", "_doctor"]


@pytest.fixture
def stub_steps(monkeypatch):
    calls = []
    for name in STEP_FNS:
        monkeypatch.setattr(
            init_mod, name,
            lambda *a, _n=name, **k: calls.append(_n) or init_mod.Result(_n, "ok"),
        )
    monkeypatch.setattr(init_mod, "detect_bitbucket_here", lambda: False)
    return calls


# --- detection (pure) -------------------------------------------------
@pytest.mark.parametrize("remotes,env,cfg,want", [
    (["origin\thttps://bitbucket.org/a/b.git (fetch)"], {}, False, True),
    (["origin\tgit@bitbucket.org:a/b.git (push)"], {}, False, True),
    ([], {"BITBUCKET_TOKEN": "x"}, False, True),
    ([], {"BITBUCKET_URL": "x"}, False, True),
    ([], {"BB_WORKSPACE": "x"}, False, True),
    ([], {}, True, True),
    (["origin\thttps://github.com/a/b.git (fetch)"], {"HOME": "/h"}, False, False),
    ([], {}, False, False),
])
def test_detect_table(remotes, env, cfg, want):
    assert init_mod.detect_bitbucket(remotes, env, cfg) is want


def test_flag_overrides_detection():
    assert init_mod.resolve_bitbucket(True, False) is True
    assert init_mod.resolve_bitbucket(False, True) is False
    assert init_mod.resolve_bitbucket(None, True) is True
    assert init_mod.resolve_bitbucket(None, False) is False


# --- CLI ---------------------------------------------------------------
def test_help_flags():
    r = CliRunner()
    for flag in ("-h", "--help"):
        out = r.invoke(cli, ["init", flag])
        assert out.exit_code == 0 and "--dry-run" in out.output
        assert r.invoke(cli, [flag]).exit_code == 0


def test_dry_run_prints_every_step_and_runs_no_subprocess(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("subprocess used in dry-run")
    monkeypatch.setattr(subprocess, "run", boom)
    monkeypatch.setattr(subprocess, "Popen", boom)
    out = CliRunner().invoke(cli, ["init", "--dry-run", "--bitbucket"])
    assert out.exit_code == 0, out.output
    for word in ("setup-dev", "bb", "plugins", "skills", "brain", "doctor"):
        assert word in out.output


def test_short_n_is_dry_run(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: 1 / 0)
    assert CliRunner().invoke(cli, ["init", "-n", "--no-bitbucket"]).exit_code == 0


def test_no_bitbucket_skips_bb(stub_steps):
    out = CliRunner().invoke(cli, ["init", "--no-bitbucket"])
    assert out.exit_code == 0
    assert "_bb" not in stub_steps and "_setup_dev" in stub_steps


def test_bitbucket_flag_runs_bb(stub_steps):
    assert CliRunner().invoke(cli, ["init", "--bitbucket"]).exit_code == 0
    assert "_bb" in stub_steps


def test_skip_plugins(stub_steps):
    CliRunner().invoke(cli, ["init", "--skip-plugins"])
    assert "_plugins" not in stub_steps


def test_step_failure_exit_1_but_continues(stub_steps, monkeypatch):
    monkeypatch.setattr(init_mod, "_plugins", lambda *a, **k: init_mod.Result("plugins", "fail", "nope"))
    out = CliRunner().invoke(cli, ["init"])
    assert out.exit_code == 1
    assert "_doctor" in stub_steps


def test_step_exception_is_a_failure(stub_steps, monkeypatch):
    def raises(*a, **k):
        raise RuntimeError("kaput")
    monkeypatch.setattr(init_mod, "_skills", raises)
    out = CliRunner().invoke(cli, ["init"])
    assert out.exit_code == 1 and "kaput" in out.output
