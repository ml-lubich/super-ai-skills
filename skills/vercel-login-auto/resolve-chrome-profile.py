#!/usr/bin/env python3
"""Map a Google Chrome account email to its profile DIRECTORY name.

Chrome's profile directories are `Default`, `Profile 1`, `Profile 2`, ... and
the number has nothing to do with the account signed into it. The mapping lives
in each profile's `Preferences` JSON under `account_info`.

This matters more than convenience here: on this machine `Default` is a
personal account and `Profile 2` is a CLIENT account (eriaevents.co). Opening an
auth flow in the wrong one signs a client's org into a personal tool, or the
reverse. Guessing the directory is not acceptable; look it up.

Usage:
    resolve-chrome-profile.py                      # list every profile
    resolve-chrome-profile.py you@example.com      # print its directory name
"""
from __future__ import annotations

import json
import pathlib
import sys

CHROME = pathlib.Path.home() / "Library/Application Support/Google/Chrome"


def profiles() -> list[tuple[str, str, list[str]]]:
    """(directory, display name, emails) for every profile that has Preferences."""
    out: list[tuple[str, str, list[str]]] = []
    candidates = [CHROME / "Default", *sorted(CHROME.glob("Profile *"))]
    for path in candidates:
        prefs = path / "Preferences"
        if not prefs.is_file():
            continue
        try:
            data = json.loads(prefs.read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            continue
        emails = [a.get("email", "") for a in (data.get("account_info") or [])]
        name = (data.get("profile") or {}).get("name", "?")
        out.append((path.name, name, [e for e in emails if e]))
    return out


def resolve(email: str) -> str | None:
    """The directory whose PRIMARY account is `email`.

    Primary, not "appears anywhere": a work profile commonly lists a personal
    address as a secondary account, so a substring match over all emails would
    happily hand back the client profile for a personal address.
    """
    wanted = email.strip().lower()
    for directory, _name, emails in profiles():
        if emails and emails[0].lower() == wanted:
            return directory
    return None


def main() -> int:
    if len(sys.argv) < 2:
        for directory, name, emails in profiles():
            print(f"{directory:12} {name:24} {', '.join(emails) or '(no account)'}")
        return 0
    found = resolve(sys.argv[1])
    if not found:
        print(f"no Chrome profile whose primary account is {sys.argv[1]!r}", file=sys.stderr)
        print("known profiles:", file=sys.stderr)
        for directory, name, emails in profiles():
            print(f"  {directory:12} {name:24} {', '.join(emails)}", file=sys.stderr)
        return 1
    print(found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
