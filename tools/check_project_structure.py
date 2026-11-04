#!/usr/bin/env python3
"""Portable sanity check. This does NOT compile, run, or verify Unreal Engine."""
import json
from pathlib import Path
from validate_glassbend_layout import LAYOUT_PATH, QUEST_PATH, load_json, validate_layout
from validate_interaction_bindings import BINDINGS_PATH, BRIDGE_CPP_PATH, load as load_bindings, validate_bindings
from validate_dialogue_contract import DIALOGUE_PATH, load as load_dialogue, validate_dialogue

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
    "Source/ArchCityInDarkness/Public/ACIDQuestLedgerComponent.h",
    "Source/ArchCityInDarkness/Private/ACIDQuestLedgerComponent.cpp",
    "Source/ArchCityInDarkness/Private/Tests/ACIDQuestLedgerComponentTests.cpp",
    "docs/QUEST_LEDGER_SOURCE_PROTOTYPE.md",
    "Prototypes/Glassbend/layout_v1.json",
    "tools/validate_glassbend_layout.py",
    "tools/tests/test_glassbend_layout.py",
    "docs/GLASSBEND_LAYOUT_CONTRACT.md",
    "Prototypes/Glassbend/interaction_bindings_v1.json",
    "Source/ArchCityInDarkness/Public/ACIDQuestInteractionBridge.h",
    "Source/ArchCityInDarkness/Private/ACIDQuestInteractionBridge.cpp",
    "Source/ArchCityInDarkness/Private/Tests/ACIDQuestInteractionBridgeTests.cpp",
    "tools/validate_interaction_bindings.py",
    "tools/tests/test_interaction_bindings.py",
    "docs/GLASSBEND_INTERACTION_BRIDGE.md",
    "Prototypes/Glassbend/dialogue_v1.json",
    "tools/validate_dialogue_contract.py",
    "tools/tests/test_dialogue_contract.py",
    "docs/GLASSBEND_DIALOGUE_CONTRACT.md",
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

quest_header = (ROOT / "Source/ArchCityInDarkness/Public/ACIDQuestLedgerComponent.h").read_text(encoding="utf-8")
quest_source = (ROOT / "Source/ArchCityInDarkness/Private/ACIDQuestLedgerComponent.cpp").read_text(encoding="utf-8")
quest_tests = (ROOT / "Source/ArchCityInDarkness/Private/Tests/ACIDQuestLedgerComponentTests.cpp").read_text(encoding="utf-8")
contract = json.loads((ROOT / "Prototypes/Glassbend/the_unclaimed_hour.json").read_text(encoding="utf-8"))
for clue in contract["clues"]:
    assert f'TEXT("{clue["id"]}")' in quest_source, f"Clue source drift: {clue['id']}"
for route in contract["routes"]:
    assert f'TEXT("{route["evidence"]}")' in quest_source, f"Evidence source drift: {route['id']}"
    assert route["id"].capitalize() in quest_header, f"Route enum drift: {route['id']}"
assert "TryRestoreSnapshot" in quest_header and "ValidateSnapshot" in quest_source
assert "ArchCityInDarkness.Quest.Glassbend.Contract" in quest_tests

layout_problems = validate_layout(load_json(LAYOUT_PATH), load_json(QUEST_PATH))
assert not layout_problems, "Source-only layout/quest drift: " + "; ".join(layout_problems)

binding_problems = validate_bindings(
    load_bindings(BINDINGS_PATH), load_json(QUEST_PATH), load_json(LAYOUT_PATH),
    BRIDGE_CPP_PATH.read_text(encoding="utf-8"),
)
assert not binding_problems, "Source-only action bridge drift: " + "; ".join(binding_problems)

interaction_test = (ROOT / "Source/ArchCityInDarkness/Private/Tests/ACIDQuestInteractionBridgeTests.cpp").read_text(encoding="utf-8")
assert "ArchCityInDarkness.Interaction.Glassbend.Contract" in interaction_test
assert "TryApplyAction" in (ROOT / "Source/ArchCityInDarkness/Public/ACIDQuestInteractionBridge.h").read_text(encoding="utf-8")
dialogue_problems = validate_dialogue(
    load_dialogue(DIALOGUE_PATH), load_bindings(BINDINGS_PATH),
    load_json(QUEST_PATH), load_json(LAYOUT_PATH),
)
assert not dialogue_problems, "Source-only dialogue/interaction drift: " + "; ".join(dialogue_problems)

print("PASS: manifest, quest, layout, interaction and original dialogue parity (source only; Unreal unverified)")
