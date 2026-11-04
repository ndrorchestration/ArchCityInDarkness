#!/usr/bin/env python3
"""Static ID/provenance drift audit for the source-only Glassbend interaction bridge.

This never runs native Unreal, validates player distance, or approves gameplay.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINDINGS_PATH = ROOT / "Prototypes/Glassbend/interaction_bindings_v1.json"
QUEST_PATH = ROOT / "Prototypes/Glassbend/the_unclaimed_hour.json"
LAYOUT_PATH = ROOT / "Prototypes/Glassbend/layout_v1.json"
BRIDGE_CPP_PATH = ROOT / "Source/ArchCityInDarkness/Private/ACIDQuestInteractionBridge.cpp"

EXPECTED = {
    "inspect_receipt": ("discover_clue", "shift_receipt", "clue_spawn", "shift_receipt"),
    "ask_mara_about_ledger": ("discover_clue", "ledger_gap", "npc", "mara_vale"),
    "ask_nico_about_route": ("discover_clue", "route_note", "npc", "nico_bell"),
    "inspect_annex_badge": ("discover_clue", "annex_badge", "clue_spawn", "annex_badge"),
    "commit_dialogue": ("resolve_route", "dialogue", "npc", "mara_vale"),
    "commit_stealth": ("resolve_route", "stealth", "npc", "nico_bell"),
    "commit_confrontation": ("resolve_route", "confrontation", "npc", "etta_quill"),
}
REQUIRED_CONSTRAINTS = {
    "no_player_proximity_claim": True, "no_actor_spawn_claim": True,
    "no_input_binding_claim": True, "no_automatic_feeding": True,
    "no_quest_overwrite": True, "invalid_action_no_op": True,
}
ACTION_PATTERN = re.compile(
    r'if\s*\(ActionId\s*==\s*FName\(TEXT\("([^"]+)"\)\)\)\s*'
    r'\{\s*return\s+QuestLedger->(DiscoverClue|TryResolve)\((.*?)\);\s*\}',
    flags=re.DOTALL,
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_bindings(bindings: dict, quest: dict, layout: dict, cpp: str) -> list[str]:
    errors = []
    if any(not isinstance(x, dict) for x in (bindings, quest, layout)):
        return ["Bindings, quest and layout must be JSON objects"]
    if bindings.get("schema_version") != 1 or bindings.get("status") != "PROTOTYPE_NOT_CANON":
        errors.append("Bindings must remain schema v1 noncanonical")
    if bindings.get("quest_id") != quest.get("quest_id") or (
        bindings.get("layout_id") != layout.get("scene_id")
    ):
        errors.append("Bindings must refer to the reviewed original quest and spatial layout")
    if bindings.get("world_interaction_gate") != "NOT_IMPLEMENTED" or (
        bindings.get("interaction_model") != "EXPLICIT_ACTION_IDS_ONLY"
    ):
        errors.append("Do not claim implemented world input, range checks or actor interaction")
    if bindings.get("constraints") != REQUIRED_CONSTRAINTS:
        errors.append("Required nonviolent, noncanonical and fail-closed constraints drifted")

    actions = bindings.get("actions")
    if not isinstance(actions, list) or any(not isinstance(a, dict) for a in actions):
        return errors + ["Action list must contain objects"]
    names = [a.get("id") for a in actions]
    if any(not isinstance(name, str) for name in names):
        return errors + ["All action IDs must be strings"]
    if len(names) != len(EXPECTED) or len(set(names)) != len(names) or (
        set(names) != set(EXPECTED)
    ):
        errors.append("Action IDs missing, duplicated or unexpected")
    quest_clues = {a.get("id") for a in quest.get("clues", []) if isinstance(a, dict)}
    quest_routes = {a.get("id") for a in quest.get("routes", []) if isinstance(a, dict)}
    quest_actors = {a.get("id") for a in quest.get("actors", []) if isinstance(a, dict)}
    layout_clues = {a.get("id") for a in layout.get("clue_spawns", []) if isinstance(a, dict)}
    layout_actors = {a.get("id") for a in layout.get("actors", []) if isinstance(a, dict)}
    seen_clues = set()
    seen_routes = set()

    for action in actions:
        action_id = action.get("id")
        if action_id not in EXPECTED:
            continue
        expected_kind, expected_target, expected_anchor_kind, expected_anchor_id = EXPECTED[action_id]
        kind = action.get("kind")
        if kind != expected_kind or action.get("anchor_kind") != expected_anchor_kind or (
            action.get("anchor_id") != expected_anchor_id
        ):
            errors.append(f"{action_id}: ID/kind/anchor contract mismatch")
        if kind == "discover_clue":
            target = action.get("clue_id")
            if target != expected_target or target not in quest_clues:
                errors.append(f"{action_id}: unknown or incorrect clue")
            if "route_id" in action:
                errors.append(f"{action_id}: clue actions cannot contain route_id")
            seen_clues.add(target)
        elif kind == "resolve_route":
            target = action.get("route_id")
            if target != expected_target or target not in quest_routes:
                errors.append(f"{action_id}: unknown or incorrect route")
            if "clue_id" in action:
                errors.append(f"{action_id}: route actions cannot contain clue_id")
            seen_routes.add(target)
        else:
            errors.append(f"{action_id}: unsupported action kind")
        anchor = action.get("anchor_id")
        if action.get("anchor_kind") == "npc":
            if anchor not in quest_actors or anchor not in layout_actors:
                errors.append(f"{action_id}: missing source NPC anchor")
        elif action.get("anchor_kind") == "clue_spawn":
            if anchor not in quest_clues or anchor not in layout_clues:
                errors.append(f"{action_id}: missing clue spawn anchor")
        else:
            errors.append(f"{action_id}: unsupported anchor type")

    if seen_clues != quest_clues or seen_routes != quest_routes:
        errors.append("Action coverage does not match quest clues/routes")

    matched = ACTION_PATTERN.findall(cpp)
    cpp_map = {}
    for action_id, function_name, arguments in matched:
        if action_id in cpp_map:
            errors.append(f"Duplicate source dispatch case: {action_id}")
        cpp_map[action_id] = (function_name, re.sub(r"\s+", "", arguments))
    if set(cpp_map) != set(EXPECTED):
        errors.append("C++ bridge action identifiers differ from the manifest")
    for action_id, (kind, target, _, _) in EXPECTED.items():
        desired = (
            ("DiscoverClue", f'FName(TEXT("{target}"))')
            if kind == "discover_clue"
            else ("TryResolve", f"EACIDResolutionRoute::{target.capitalize()}")
        )
        if cpp_map.get(action_id) != desired:
            errors.append(f"C++ dispatch drift for {action_id}")
    if "return false;" not in cpp or "IsValid(QuestLedger)" not in cpp:
        errors.append("C++ bridge must reject invalid inputs")
    # A source-only guard against directly coupling player actions to feeding mechanics.
    # This is a text-level check, not a proof of runtime call-graph purity.
    if any(token in cpp for token in ("HungerComponent", "->Feed(", "->AccrueHunger(", "->SetHunger(")):
        errors.append("Interaction bridge must not directly mutate hunger")
    return errors


def main() -> int:
    errors = validate_bindings(load(BINDINGS_PATH), load(QUEST_PATH), load(LAYOUT_PATH),
                               BRIDGE_CPP_PATH.read_text(encoding="utf-8"))
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: manifest/quest/layout/C++ action ID and route parity (static only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
