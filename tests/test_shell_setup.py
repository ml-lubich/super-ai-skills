"""shell_setup.py: oh-my-zsh, powerlevel10k, zsh plugins, managed .zshrc block."""

import re

import pytest

from super_ai_skills import shell_setup as ss

OMZ_TEMPLATE = (
    'export ZSH="$HOME/.oh-my-zsh"\n'
    'ZSH_THEME="robbyrussell"\n'
    "plugins=(git)\n"
    "source $ZSH/oh-my-zsh.sh\n"
    "alias ll='ls -l'\n"
)


class Rec:
    def __init__(self, rc=0):
        self.calls, self.rc = [], rc

    def __call__(self, argv, env=None):
        self.calls.append((list(argv), env))
        return self.rc

    @property
    def argvs(self):
        return [c[0] for c in self.calls]


def have(*names):
    return lambda n: f"/bin/{n}" if n in names else None


def omz(home):
    (home / ".oh-my-zsh").mkdir()
    return home / ".oh-my-zsh"


@pytest.fixture(autouse=True)
def mac(monkeypatch):
    monkeypatch.setattr(ss.platform, "system", lambda: "Darwin")


# ---- managed block ----
def test_block_created_when_zshrc_missing(tmp_path):
    ss.ensure_zshrc_block(tmp_path, "k", ["A=1"])
    t = (tmp_path / ".zshrc").read_text()
    assert "# >>> superai-skills:k >>>\nA=1\n# <<< superai-skills:k <<<" in t


def test_block_idempotent_and_replaced_in_place(tmp_path):
    z = tmp_path / ".zshrc"
    z.write_text("top\nsource $ZSH/oh-my-zsh.sh\nbottom\n")
    ss.ensure_zshrc_block(tmp_path, "k", ["A=1"])
    once = z.read_text()
    ss.ensure_zshrc_block(tmp_path, "k", ["A=1"])
    assert z.read_text() == once
    ss.ensure_zshrc_block(tmp_path, "k", ["A=2"])
    t = z.read_text()
    assert t.count(">>> superai-skills:k") == 1 and "A=2" in t and "A=1" not in t


def test_backup_made_once_and_user_lines_untouched(tmp_path):
    z = tmp_path / ".zshrc"
    z.write_text(OMZ_TEMPLATE)
    ss.ensure_zshrc_block(tmp_path, "a", ["A=1"])
    ss.ensure_zshrc_block(tmp_path, "b", ["B=1"])
    ss.ensure_zshrc_block(tmp_path, "a", ["A=2"])
    backups = list(tmp_path.glob(".zshrc.superai-backup-*"))
    assert len(backups) == 1
    assert re.search(r"-\d{8}-\d{6}$", backups[0].name)
    assert backups[0].read_text() == OMZ_TEMPLATE
    stripped = re.sub(r"# >>> superai-skills:(\w) >>>.*?# <<< superai-skills:\1 <<<\n",
                      "", z.read_text(), flags=re.S)
    assert stripped == OMZ_TEMPLATE


def test_no_backup_when_nothing_changes(tmp_path):
    ss.ensure_zshrc_block(tmp_path, "k", ["A=1"])
    for b in tmp_path.glob(".zshrc.superai-backup-*"):
        b.unlink()
    ss.ensure_zshrc_block(tmp_path, "k", ["A=1"])
    assert not list(tmp_path.glob(".zshrc.superai-backup-*"))


def test_block_goes_before_source_line(tmp_path):
    (tmp_path / ".zshrc").write_text(OMZ_TEMPLATE)
    ss.ensure_zshrc_block(tmp_path, "k", ["A=1"])
    t = (tmp_path / ".zshrc").read_text()
    assert t.index("superai-skills:k >>>") > t.index("plugins=(git)")
    assert t.index("<<< superai-skills:k") < t.index("source $ZSH/oh-my-zsh.sh")


# ---- oh-my-zsh ----
def test_omz_skip_when_present(tmp_path):
    omz(tmp_path)
    r = Rec()
    res = ss.install_ohmyzsh(runner=r, home=tmp_path, which=have("git", "zsh"))
    assert res.status == "skip" and not r.calls


def test_omz_argv_and_env_exact(tmp_path):
    r = Rec()
    res = ss.install_ohmyzsh(runner=r, home=tmp_path, which=have("git", "zsh"))
    assert res.status == "ok"
    argv, env = r.calls[0]
    assert argv == ["sh", "-c",
                    'sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"']
    assert env["RUNZSH"] == "no" and env["CHSH"] == "no" and env["KEEP_ZSHRC"] == "yes"


@pytest.mark.parametrize("missing", ["git", "zsh"])
def test_omz_missing_tool_fails(tmp_path, missing):
    r = Rec()
    names = {"git", "zsh"} - {missing}
    res = ss.install_ohmyzsh(runner=r, home=tmp_path, which=have(*names))
    assert res.status == "fail" and missing in res.detail and not r.calls


def test_omz_installer_failure(tmp_path):
    res = ss.install_ohmyzsh(runner=Rec(1), home=tmp_path, which=have("git", "zsh"))
    assert res.status == "fail"


def test_omz_dry_run(tmp_path):
    r = Rec()
    res = ss.install_ohmyzsh(dry_run=True, runner=r, home=tmp_path, which=have())
    assert res.status == "dry-run" and not r.calls
    assert list(tmp_path.iterdir()) == []


# ---- powerlevel10k ----
P10K_DIR = ".oh-my-zsh/custom/themes/powerlevel10k"


def test_p10k_skip_when_present(tmp_path):
    (tmp_path / P10K_DIR).mkdir(parents=True)
    r = Rec()
    res = ss.install_powerlevel10k(runner=r, home=tmp_path, which=have("git", "brew"))
    assert res.status == "skip" and not r.calls


def test_p10k_clone_font_theme(tmp_path):
    omz(tmp_path)
    (tmp_path / ".zshrc").write_text(OMZ_TEMPLATE)
    r = Rec()
    # `brew list` rc=1 means font absent -> then install
    def runner(argv, env=None):
        r(argv, env)
        return 1 if argv[:3] == ["brew", "list", "--cask"] else 0
    res = ss.install_powerlevel10k(runner=runner, home=tmp_path, which=have("git", "brew"))
    assert res.status == "ok" and "p10k configure" in res.detail
    assert ["git", "clone", "--depth=1", "https://github.com/romkatv/powerlevel10k.git",
            str(tmp_path / P10K_DIR)] in r.argvs
    assert ["brew", "install", "--cask", "font-meslo-lg-nerd-font"] in r.argvs
    t = (tmp_path / ".zshrc").read_text()
    assert 'ZSH_THEME="powerlevel10k/powerlevel10k"' in t
    assert t.index("powerlevel10k/powerlevel10k") < t.index("source $ZSH/oh-my-zsh.sh")
    assert 'ZSH_THEME="robbyrussell"' in t  # user line untouched


def test_p10k_font_already_in_fonts_dir(tmp_path):
    omz(tmp_path)
    (tmp_path / "Library/Fonts").mkdir(parents=True)
    (tmp_path / "Library/Fonts/MesloLGSNerdFont-Regular.ttf").write_text("")
    r = Rec()
    ss.install_powerlevel10k(runner=r, home=tmp_path, which=have("git", "brew"))
    assert not any(a[0] == "brew" for a in r.argvs)


def test_p10k_font_already_via_brew(tmp_path):
    omz(tmp_path)
    r = Rec(0)
    ss.install_powerlevel10k(runner=r, home=tmp_path, which=have("git", "brew"))
    assert not any(a[:2] == ["brew", "install"] for a in r.argvs)


def test_p10k_existing_p10k_zsh_untouched(tmp_path):
    omz(tmp_path)
    (tmp_path / ".p10k.zsh").write_text("mine")
    ss.install_powerlevel10k(runner=Rec(0), home=tmp_path, which=have("git", "brew"))
    assert (tmp_path / ".p10k.zsh").read_text() == "mine"


def test_p10k_missing_git_fails(tmp_path):
    omz(tmp_path)
    r = Rec()
    res = ss.install_powerlevel10k(runner=r, home=tmp_path, which=have("brew"))
    assert res.status == "fail" and "git" in res.detail and not r.calls


def test_p10k_missing_brew_fails_on_mac(tmp_path):
    omz(tmp_path)
    r = Rec()
    res = ss.install_powerlevel10k(runner=r, home=tmp_path, which=have("git"))
    assert res.status == "fail" and "brew" in res.detail and not r.calls
    assert not (tmp_path / P10K_DIR).exists()


def test_p10k_no_brew_needed_off_mac(tmp_path, monkeypatch):
    monkeypatch.setattr(ss.platform, "system", lambda: "Linux")
    omz(tmp_path)
    res = ss.install_powerlevel10k(runner=Rec(), home=tmp_path, which=have("git"))
    assert res.status == "ok"


def test_p10k_needs_omz(tmp_path):
    res = ss.install_powerlevel10k(runner=Rec(), home=tmp_path, which=have("git", "brew"))
    assert res.status == "fail" and "oh-my-zsh" in res.detail


def test_p10k_clone_failure_writes_nothing(tmp_path):
    omz(tmp_path)
    res = ss.install_powerlevel10k(runner=Rec(1), home=tmp_path, which=have("git", "brew"))
    assert res.status == "fail" and not (tmp_path / ".zshrc").exists()


def test_p10k_dry_run(tmp_path):
    r = Rec()
    res = ss.install_powerlevel10k(dry_run=True, runner=r, home=tmp_path, which=have())
    assert res.status == "dry-run" and not r.calls and list(tmp_path.iterdir()) == []


# ---- plugins ----
def plugins_line(home):
    return re.findall(r"^plugins=\((.*?)\)", (home / ".zshrc").read_text(), re.M | re.S)


def test_plugins_clone_and_order_fresh_template(tmp_path):
    omz(tmp_path)
    (tmp_path / ".zshrc").write_text(OMZ_TEMPLATE)
    r = Rec()
    res = ss.install_zsh_plugins(runner=r, home=tmp_path, which=have("git"))
    assert res.status == "ok"
    base = tmp_path / ".oh-my-zsh/custom/plugins"
    assert ["git", "clone", "--depth=1", "https://github.com/zsh-users/zsh-autosuggestions.git",
            str(base / "zsh-autosuggestions")] in r.argvs
    assert ["git", "clone", "--depth=1", "https://github.com/zsh-users/zsh-syntax-highlighting.git",
            str(base / "zsh-syntax-highlighting")] in r.argvs
    t = (tmp_path / ".zshrc").read_text()
    assert "plugins=(git)" in t  # user line untouched
    last = plugins_line(tmp_path)[-1].split()
    assert last == ["git", "zsh-autosuggestions", "zsh-syntax-highlighting"]
    assert t.index("zsh-syntax-highlighting") < t.index("source $ZSH/oh-my-zsh.sh")


def test_plugins_custom_zshrc_keeps_existing_and_syntax_last(tmp_path):
    omz(tmp_path)
    (tmp_path / ".zshrc").write_text(
        "plugins=(\n  git\n  docker  # containers\n  zsh-syntax-highlighting\n  kubectl\n)\n"
        "source $ZSH/oh-my-zsh.sh\n")
    ss.install_zsh_plugins(runner=Rec(), home=tmp_path, which=have("git"))
    last = plugins_line(tmp_path)[-1].split()
    assert last == ["git", "docker", "kubectl", "zsh-autosuggestions", "zsh-syntax-highlighting"]
    assert "docker  # containers" in (tmp_path / ".zshrc").read_text()


def test_plugins_no_plugins_line_defaults_to_git(tmp_path):
    omz(tmp_path)
    (tmp_path / ".zshrc").write_text("export X=1\n")
    ss.install_zsh_plugins(runner=Rec(), home=tmp_path, which=have("git"))
    t = (tmp_path / ".zshrc").read_text()
    assert plugins_line(tmp_path)[-1].split() == ["git", "zsh-autosuggestions", "zsh-syntax-highlighting"]
    assert t.startswith("export X=1\n")  # appended, user content first


def test_plugins_idempotent_rerun(tmp_path):
    omz(tmp_path)
    (tmp_path / ".zshrc").write_text(OMZ_TEMPLATE)
    ss.install_zsh_plugins(runner=Rec(), home=tmp_path, which=have("git"))
    once = (tmp_path / ".zshrc").read_text()
    res = ss.install_zsh_plugins(runner=Rec(), home=tmp_path, which=have("git"))
    assert (tmp_path / ".zshrc").read_text() == once
    assert res.status == "skip" or res.status == "ok"


def test_plugins_skip_clone_when_present(tmp_path):
    base = omz(tmp_path) / "custom/plugins"
    (base / "zsh-autosuggestions").mkdir(parents=True)
    (base / "zsh-syntax-highlighting").mkdir()
    r = Rec()
    ss.install_zsh_plugins(runner=r, home=tmp_path, which=have("git"))
    assert not r.calls


def test_plugins_missing_git_fails(tmp_path):
    omz(tmp_path)
    res = ss.install_zsh_plugins(runner=Rec(), home=tmp_path, which=have())
    assert res.status == "fail" and "git" in res.detail


def test_plugins_needs_omz(tmp_path):
    res = ss.install_zsh_plugins(runner=Rec(), home=tmp_path, which=have("git"))
    assert res.status == "fail" and "oh-my-zsh" in res.detail


def test_plugins_clone_failure(tmp_path):
    omz(tmp_path)
    res = ss.install_zsh_plugins(runner=Rec(1), home=tmp_path, which=have("git"))
    assert res.status == "fail" and not (tmp_path / ".zshrc").exists()


def test_plugins_dry_run(tmp_path):
    r = Rec()
    res = ss.install_zsh_plugins(dry_run=True, runner=r, home=tmp_path, which=have())
    assert res.status == "dry-run" and not r.calls and list(tmp_path.iterdir()) == []
