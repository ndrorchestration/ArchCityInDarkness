#!/usr/bin/env python3
"""Read-only public README boundary checks for the pre-release Arch City repo.

A PASS means documentation consistency only; it does not establish native Unreal
verification, art licensing, production readiness, or approved world canon.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

PR_LINK_RE = re.compile(
    r"https://github\.com/ndrorchestration/ArchCityInDarkness/pull/(\d+)"
)
GITHUB_LINK_RE = re.compile(r"https://github\.com/[^)\s]+")

# These are intentionally explicit pre-release public claims: any release
# promotion should update this contract with independently accepted evidence.
REQUIRED_CLAIMS = {
    "pre-release status": "Status: Incubating",
    "target engine": "Unreal Engine 5.8.4",
    "draft provenance": "draft, unmerged",
    "native-vs-text-preview boundary": "not a native 3D Unreal game or Unreal SaveGame",
    "rights boundary": "rights clearance",
    "creative/IP boundary": "third-party fictional settings",
    "verification limitation": "not proof of a playable, approved release",
}


def check(text: str) -> list[str]:
    failures: list[str] = []
    if not text.startswith("# Arch City in Darkness\n"):
        failures.append("public README must have the canonical project heading")
    lowered = text.lower()
    for name, needle in REQUIRED_CLAIMS.items():
        if needle.lower() not in lowered:
            failures.append(f"missing required {name} qualifier: {needle!r}")
    ids = PR_LINK_RE.findall(text)
    if not ids:
        failures.append("no source review PR links documented")
    if len(ids) != len(set(ids)):
        failures.append("duplicate source review PR links")
    for link in GITHUB_LINK_RE.findall(text):
        if "/ndrorchestration/ArchCityInDarkness/pull/" not in link:
            failures.append(f"unexpected external repository link: {link}")
    return failures


def self_test() -> None:
    assert check("# Some Other Game\n")
    assert not PR_LINK_RE.findall("https://example.com/ndrorchestration/ArchCityInDarkness/pull/1")
    assert PR_LINK_RE.findall("https://github.com/ndrorchestration/ArchCityInDarkness/pull/7") == ["7"]
    print("PASS: documentation contract self-tests")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    path = Path(__file__).resolve().parent.parent / "README.md"
    problems = check(path.read_text(encoding="utf-8"))
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        sys.exit(1)
    print("PASS: public README preserves pre-release, native, rights and PR provenance boundaries")
    print("NOTE: this does not verify any engine build, playable scene, asset license or release")
