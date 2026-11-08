#!/usr/bin/env python3
"""M009 source-only contract: dialogue entrypoints match world markers.

This file never executes Unreal. It checks that the preview review pawn's
automatic E interaction cannot commit a route without an explicit choice UI.
The M005 dialogue graph is a proposed data contract, NOT an implemented widget.
"""
from pathlib import Path
import json
import re
from validate_dialogue_contract import validate_dialogue

ROOT = Path(__file__).resolve().parents[1]
GRAPH = "Prototypes/Glassbend/dialogue_v1.json"
BINDINGS = "Prototypes/Glassbend/interaction_bindings_v1.json"
QUEST = "Prototypes/Glassbend/the_unclaimed_hour.json"
LAYOUT = "Prototypes/Glassbend/layout_v1.json"
MARKER_CPP = "Source/ArchCityInDarkness/Private/ACIDPreludeInteractable.cpp"
CHAR_CPP = "Source/ArchCityInDarkness/Private/ACIDPreludeCharacter.cpp"
BRIDGE_CPP = "Source/ArchCityInDarkness/Private/ACIDQuestInteractionBridge.cpp"
INPUT = "Config/DefaultInput.ini"
REQUIRED = (GRAPH, BINDINGS, QUEST, LAYOUT, MARKER_CPP, CHAR_CPP, BRIDGE_CPP, INPUT)
EXPECTED_WORLD_ANCHORS = {
    "shift_receipt", "annex_badge", "mara_vale", "nico_bell", "etta_quill"
}
EXPECTED_AUTO_ACTIONS = {
    "inspect_receipt", "inspect_annex_badge",
    "ask_mara_about_ledger", "ask_nico_about_route"
}
REQUIRED_EXPLICIT_ACTIONS = {
    "commit_dialogue", "commit_stealth", "commit_confrontation"
}


def validate_world_dialogue(source: dict[str, str]) -> list[str]:
    missing = [path for path in REQUIRED if path not in source]
    if missing:
        return ["Missing contract/source: " + p for p in missing]
    try:
        graph, bindings, quest, layout = (
            json.loads(source[p]) for p in (GRAPH, BINDINGS, QUEST, LAYOUT)
        )
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        return ["Malformed JSON: " + str(exc)]
    failures = validate_dialogue(graph, bindings, quest, layout)
    marker, character, bridge, config = (
        source[p] for p in (MARKER_CPP, CHAR_CPP, BRIDGE_CPP, INPUT)
    )
    entrypoints = {e["anchor_id"] for e in graph["entrypoints"]
                   if isinstance(e.get("anchor_id"), str)}
    if entrypoints != EXPECTED_WORLD_ANCHORS:
        failures.append("Graph entrypoints drift from five approved review markers")
    known_fn = marker.split("bool AACIDPreludeInteractable::IsKnownAnchor(", 1)
    if len(known_fn) != 2:
        failures.append("Missing world marker allowlist function")
    else:
        allowlist = known_fn[1].split("FName AACIDPreludeInteractable::SelectAction(", 1)[0]
        known_ids = set(re.findall(r'Candidate == TEXT\("([a-z_]+)"\)', allowlist))
        if known_ids != entrypoints:
            failures.append("Native known marker IDs drift from dialogue entrypoints")
    select_fn = marker.split("FName AACIDPreludeInteractable::SelectAction(", 1)
    if len(select_fn) != 2:
        return failures + ["Missing world E-action selector"]
    selected_section = select_fn[1].split("bool AACIDPreludeInteractable::TryInteract(", 1)[0]
    auto_actions = set(re.findall(r'FName\(TEXT\("([a-z_]+)"\)\)', selected_section))
    if auto_actions != EXPECTED_AUTO_ACTIONS:
        failures.append("World E key must perform clue collection ONLY, not route commits")
    if any(action in selected_section for action in REQUIRED_EXPLICIT_ACTIONS):
        failures.append("Implicit irreversible route action found in E selector")
    if not re.search(
        r'if\s*\(AnchorId == TEXT\("etta_quill"\)\)\s*return NAME_None\s*;',
        selected_section,
    ):
        failures.append("Etta's final route must not auto-commit with E")
    if not re.search(
        r'Ledger->HasClue\(TEXT\("ledger_gap"\)\)\s*\?\s*NAME_None\s*:',
        selected_section,
    ):
        failures.append("Mara second E must not commit a route")
    if not re.search(
        r'Ledger->HasClue\(TEXT\("route_note"\)\)\s*\?\s*NAME_None\s*:',
        selected_section,
    ):
        failures.append("Nico second E must not commit a route")
    graph_actions = {choice["action_id"] for n in graph["nodes"]
                     for choice in n["choices"] if choice.get("action_id") is not None}
    if not REQUIRED_EXPLICIT_ACTIONS.issubset(graph_actions):
        failures.append("Dialogue graph missing explicit route choice action(s)")
    for action in REQUIRED_EXPLICIT_ACTIONS:
        if bridge.count(f'FName(TEXT("{action}"))') != 1:
            failures.append(f"Quest bridge route action missing/ambiguous: {action}")
    if 'BindAction(TEXT("Interact")' not in character or 'Key=E)' not in config:
        failures.append("Player E source input missing")
    if 'UACIDQuestInteractionBridge::TryApplyAction(Character->GetQuestLedger(), Action)' not in marker:
        failures.append("Marker dispatch must remain guarded")
    if any(r.get("forced_feeding") is not False
           or r.get("requires_violence") is not False
           or r.get("hunger_delta") != 0 for r in quest.get("routes", [])):
        failures.append("Quest route must remain nonlethal and never force feeding")
    return failures


def main() -> int:
    source = {p: (ROOT / p).read_text(encoding="utf-8")
              for p in REQUIRED if (ROOT / p).is_file()}
    failures = validate_world_dialogue(source)
    if failures:
        for failure in failures:
            print("M009 SOURCE GATE FAIL:", failure)
        return 1
    print("M009 SOURCE GATE PASS: 5 graph/world anchors; 4 clue-only E actions; 3 explicit route choices")
    print("NOT VERIFIED: native C++ build, PIE input, UMG UI, dialogue runtime, GPU rendering or creator canon")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
