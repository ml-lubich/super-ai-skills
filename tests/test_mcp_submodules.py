"""Regression guard: every *-mcp repo we own must be a submodule here.

Caught a real drift once (google-voice-mcp was built and never added) — this
pins the known set so a repeat is a test failure, not a silent gap.
"""

import os
import re

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
GITMODULES = os.path.join(ROOT_DIR, ".gitmodules")
PACKAGES_DIR = os.path.join(ROOT_DIR, "packages")

EXPECTED_MCP_SUBMODULES = {
    "imail-mcp",
    "imsg-mcp",
    "inotes-mcp",
    "jenkins-mcp",
    "linkedin-mcp",
    "railway-mcp",
    "vercel-mcp",
    "whatsapp-mcp",
    "google-voice-mcp",
}


def _submodule_paths():
    with open(GITMODULES) as f:
        content = f.read()
    return {
        os.path.basename(path)
        for path in re.findall(r"^\s*path\s*=\s*(.+)$", content, re.MULTILINE)
    }


def test_every_known_mcp_repo_is_a_submodule():
    paths = _submodule_paths()
    missing = EXPECTED_MCP_SUBMODULES - paths
    assert not missing, f"missing from .gitmodules: {missing}"


def test_every_mcp_submodule_has_a_checked_out_package_dir():
    for name in EXPECTED_MCP_SUBMODULES:
        pkg_path = os.path.join(PACKAGES_DIR, name)
        assert os.path.isdir(pkg_path), f"packages/{name} does not exist on disk"
