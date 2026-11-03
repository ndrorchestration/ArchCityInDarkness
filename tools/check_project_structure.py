#!/usr/bin/env python3
"""Portable sanity check. This does NOT compile, run, or verify Unreal Engine."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    ".gitignore",
    "ArchCityInDarkness.uproject",
    "Source/ArchCityInDarkness.Target.cs",
    "Source/ArchCityInDarknessEditor.Target.cs",
    "Source/ArchCityInDarkness/ArchCityInDarkness.Build.cs",
    "Source/ArchCityInDarkness/Private/ArchCityInDarkness.cpp",
    "Source/ArchCityInDarkness/Public/ACIDHungerComponent.h",
    "Source/ArchCityInDarkness/Private/ACIDHungerComponent.cpp",
    "Source/ArchCityInDarkness/Private/Tests/ACIDHungerComponentTests.cpp",
    "docs/PROJECT_BRIEF.md",
    "docs/ORIGINALITY_AND_RIGHTS.md",
    "docs/VERTICAL_SLICE.md",
    "docs/TECHNICAL_ARCHITECTURE.md",
    "docs/VERIFICATION.md",
    "docs/NATIVE_VERIFICATION_RUNBOOK.md",
    "docs/FIRST_SCENE.md",
    "tools/Verify-UnrealNative.ps1",
    "tools/verify_automation_report.py",
    "tools/tests/test_verify_automation_report.py",
]
missing = [str(f) for f in REQUIRED if not (ROOT / f).is_file()]
assert not missing, f"Missing required files: {missing}"

project = json.loads((ROOT / "ArchCityInDarkness.uproject").read_text(encoding="utf-8"))
assert project["FileVersion"] == 3
assert project["EngineAssociation"] == "5.8"
assert any(m["Name"] == "ArchCityInDarkness" and m["Type"] == "Runtime" for m in project["Modules"])

header = (ROOT / "Source/ArchCityInDarkness/Public/ACIDHungerComponent.h").read_text(encoding="utf-8")
test_source = (ROOT / "Source/ArchCityInDarkness/Private/Tests/ACIDHungerComponentTests.cpp").read_text(encoding="utf-8")
assert "OnHungerChanged" in header
assert "IMPLEMENT_SIMPLE_AUTOMATION_TEST" in test_source
assert "ArchCityInDarkness.Survival.Hunger.Contract" in test_source

print("PASS: manifest, expected files, hunger test registration (static only; Unreal unverified)")
