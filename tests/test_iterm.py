"""iterm.py: install skip/dry-run/non-mac/brew-missing/argv, dynamic profile shape, idempotence."""

import json

from super_ai_skills import iterm

PROFILE_REL = "Library/Application Support/iTerm2/DynamicProfiles/superai-skills.json"


class Recorder:
    def __init__(self, rc=0):
        self.calls, self.rc = [], rc

    def __call__(self, argv):
        self.calls.append(list(argv))
        return self.rc


def brew(name):
    return "/opt/homebrew/bin/brew" if name == "brew" else None


def nobrew(name):
    return None


def kw(tmp_path, **extra):
    return dict(home=tmp_path / "home", system_apps=tmp_path / "sys", platform="darwin", **extra)


# --- install_iterm2 ---

def test_install_non_mac_skips(tmp_path):
    r = Recorder()
    res = iterm.install_iterm2(runner=r, which=brew, **{**kw(tmp_path), "platform": "linux"})
    assert res.status == "skip" and "macOS" in res.detail and r.calls == []


def test_install_skips_when_in_system_apps(tmp_path):
    (tmp_path / "sys" / "iTerm.app").mkdir(parents=True)
    r = Recorder()
    assert iterm.install_iterm2(runner=r, which=brew, **kw(tmp_path)).status == "skip"
    assert r.calls == []


def test_install_skips_when_in_user_apps(tmp_path):
    (tmp_path / "home" / "Applications" / "iTerm.app").mkdir(parents=True)
    assert iterm.install_iterm2(runner=Recorder(), which=brew, **kw(tmp_path)).status == "skip"


def test_install_brew_missing_fails(tmp_path):
    r = Recorder()
    res = iterm.install_iterm2(runner=r, which=nobrew, **kw(tmp_path))
    assert res.status == "fail" and "brew" in res.detail and r.calls == []


def test_install_exact_argv(tmp_path):
    r = Recorder()
    res = iterm.install_iterm2(runner=r, which=brew, **kw(tmp_path))
    assert res.status == "ok"
    assert r.calls == [["brew", "install", "--cask", "iterm2"]]


def test_install_failure_reported(tmp_path):
    res = iterm.install_iterm2(runner=Recorder(1), which=brew, **kw(tmp_path))
    assert res.status == "fail" and "brew install --cask iterm2" in res.detail


def test_install_dry_run_no_commands_even_without_brew(tmp_path):
    r = Recorder()
    res = iterm.install_iterm2(dry_run=True, runner=r, which=nobrew, **kw(tmp_path))
    assert res.status == "dry-run" and "brew install --cask iterm2" in res.detail
    assert r.calls == []


# --- apply_iterm_profile ---

def test_profile_written_valid_json(tmp_path):
    r = Recorder()
    res = iterm.apply_iterm_profile(runner=r, **kw(tmp_path))
    assert res.status == "ok" and r.calls == []
    assert "Profiles menu" in res.detail and "delete" in res.detail
    data = json.loads((tmp_path / "home" / PROFILE_REL).read_text())
    (p,) = data["Profiles"]
    assert p["Name"] == "SuperAI" and p["Guid"]
    assert p["Normal Font"] == "MesloLGS-NF-Regular 13"
    assert p["Scrollback Lines"] == 10000 and p["Unlimited Scrollback"] is False
    assert p["Option Key Sends"] == 2 and p["Silence Bell"] is True
    assert p["Custom Directory"] == "Recycle"
    for i in range(16):
        c = p[f"Ansi {i} Color"]
        assert {"Red Component", "Green Component", "Blue Component"} <= set(c)
        assert all(0 <= c[k] <= 1 for k in ("Red Component", "Green Component", "Blue Component"))
    for k in ("Foreground Color", "Background Color", "Cursor Color", "Selection Color"):
        assert k in p


def test_profile_idempotent(tmp_path):
    iterm.apply_iterm_profile(**kw(tmp_path))
    res = iterm.apply_iterm_profile(**kw(tmp_path))
    assert res.status == "skip"


def test_profile_rewritten_when_content_differs(tmp_path):
    f = tmp_path / "home" / PROFILE_REL
    f.parent.mkdir(parents=True)
    f.write_text("{}")
    assert iterm.apply_iterm_profile(**kw(tmp_path)).status == "ok"
    assert "Profiles" in json.loads(f.read_text())


def test_profile_dry_run_writes_nothing(tmp_path):
    r = Recorder()
    res = iterm.apply_iterm_profile(dry_run=True, make_default=True, runner=r, **kw(tmp_path))
    assert res.status == "dry-run" and r.calls == []
    assert not (tmp_path / "home").exists()


def test_other_dynamic_profiles_untouched(tmp_path):
    other = tmp_path / "home" / PROFILE_REL
    other = other.with_name("mine.json")
    other.parent.mkdir(parents=True)
    other.write_text('{"Profiles": []}')
    iterm.apply_iterm_profile(**kw(tmp_path))
    assert other.read_text() == '{"Profiles": []}'


def test_make_default_runs_defaults_write(tmp_path):
    r = Recorder()
    res = iterm.apply_iterm_profile(make_default=True, runner=r, **kw(tmp_path))
    assert res.status == "ok"
    assert r.calls == [["defaults", "write", "com.googlecode.iterm2",
                        "Default Bookmark Guid", iterm.GUID]]


def test_make_default_failure(tmp_path):
    res = iterm.apply_iterm_profile(make_default=True, runner=Recorder(1), **kw(tmp_path))
    assert res.status == "fail"


def test_make_default_runs_even_if_file_current(tmp_path):
    iterm.apply_iterm_profile(**kw(tmp_path))
    r = Recorder()
    res = iterm.apply_iterm_profile(make_default=True, runner=r, **kw(tmp_path))
    assert res.status == "ok" and len(r.calls) == 1
