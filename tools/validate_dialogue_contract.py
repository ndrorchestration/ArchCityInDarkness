#!/usr/bin/env python3
"""Portable original dialogue graph contract. This is NOT an Unreal UI or gameplay test."""
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIALOGUE_PATH = ROOT / "Prototypes/Glassbend/dialogue_v1.json"
BINDINGS_PATH = ROOT / "Prototypes/Glassbend/interaction_bindings_v1.json"
QUEST_PATH = ROOT / "Prototypes/Glassbend/the_unclaimed_hour.json"
LAYOUT_PATH = ROOT / "Prototypes/Glassbend/layout_v1.json"

REQUIRED_CONSTRAINTS = {
    "original_dialogue_only": True,
    "all_routes_nonlethal": True,
    "no_forced_feeding": True,
    "all_lines_captionable": True,
    "no_voice_asset_claim": True,
    "no_player_world_gate_claim": True,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_dialogue(dialogue: dict, bindings: dict, quest: dict, layout: dict) -> list[str]:
    errors = []
    if any(not isinstance(v, dict) for v in (dialogue, bindings, quest, layout)):
        return ["All contracts must be JSON objects"]
    if dialogue.get("schema_version") != 1 or dialogue.get("status") != "PROTOTYPE_NOT_CANON":
        errors.append("Dialogue schema and noncanonical status drifted")
    if dialogue.get("quest_id") != quest.get("quest_id") or (
        dialogue.get("layout_id") != layout.get("scene_id")
    ):
        errors.append("Dialogue must match exact quest and layout IDs")
    if dialogue.get("interaction_model") != "EXPLICIT_ACTION_IDS_ONLY" or (
        dialogue.get("runtime_status") != "NOT_IMPLEMENTED"
    ):
        errors.append("World/UI/runtime claims must remain unimplemented")
    if dialogue.get("localization_source_language") != "en-US" or (
        dialogue.get("constraints") != REQUIRED_CONSTRAINTS
    ):
        errors.append("Localization/caption and safe-route contract drifted")

    binding_actions = bindings.get("actions")
    if not isinstance(binding_actions, list) or any(not isinstance(a, dict) for a in binding_actions):
        return errors + ["Binding actions malformed"]
    action_ids = {a.get("id") for a in binding_actions if isinstance(a.get("id"), str)}
    anchor_pairs = {(a.get("anchor_kind"), a.get("anchor_id")) for a in binding_actions if (
        isinstance(a.get("anchor_kind"), str) and isinstance(a.get("anchor_id"), str)
    )}
    actor_ids = {a.get("id") for a in quest.get("actors", []) if isinstance(a, dict)}
    spawn_ids = {a.get("id") for a in layout.get("clue_spawns", []) if isinstance(a, dict)}

    nodes_data = dialogue.get("nodes")
    if not isinstance(nodes_data, list) or any(not isinstance(n, dict) for n in nodes_data):
        return errors + ["Dialogue nodes must be a list of objects"]
    if len(nodes_data) == 0:
        return errors + ["Dialogue must contain at least one node"]
    ids = [n.get("id") for n in nodes_data]
    if any(not isinstance(v, str) or not v for v in ids):
        return errors + ["Node IDs must be nonempty strings"]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate dialogue node ID")
    nodes = {n["id"]: n for n in nodes_data}
    all_choice_ids = set()
    used_actions = set()
    edges = {n: set() for n in nodes}
    closable_nodes = set()
    for node in nodes_data:
        nid = node["id"]
        anchor_id = node.get("anchor_id")
        if not isinstance(anchor_id, str) or anchor_id not in actor_ids | spawn_ids:
            errors.append(f"{nid}: invalid or unknown source anchor")
        speaker = node.get("speaker_id")
        if speaker != "narrator" and speaker not in actor_ids:
            errors.append(f"{nid}: invalid speaker")
        line = node.get("line")
        if not isinstance(line, str) or not (15 <= len(line) <= 320):
            errors.append(f"{nid}: captionable original line must be 15-320 chars")
        choices = node.get("choices")
        if not isinstance(choices, list) or not choices:
            errors.append(f"{nid}: no interaction or close choices")
            continue
        for choice in choices:
            if not isinstance(choice, dict):
                errors.append(f"{nid}: malformed choice")
                continue
            cid = choice.get("id")
            if not isinstance(cid, str) or not cid or cid in all_choice_ids:
                errors.append(f"{nid}: duplicate/invalid choice ID")
            else:
                all_choice_ids.add(cid)
            text = choice.get("player_text")
            if not isinstance(text, str) or not (4 <= len(text) <= 160):
                errors.append(f"{nid}:{cid}: choice caption must be 4-160 chars")
            action = choice.get("action_id")
            success = choice.get("on_success")
            failure = choice.get("on_failure")
            close = choice.get("close")
            if type(close) is not bool:
                errors.append(f"{nid}:{cid}: close must be boolean")
                continue
            if action is None:
                if failure is not None or (close and success is not None) or (
                    not close and success is None
                ):
                    errors.append(f"{nid}:{cid}: invalid no-action navigation")
            elif not isinstance(action, str) or action not in action_ids or (
                close or not isinstance(success, str) or not isinstance(failure, str)
            ) or success == failure:
                errors.append(f"{nid}:{cid}: action binding/branches invalid")
            else:
                used_actions.add(action)
            for target in (success, failure):
                if target is None:
                    continue
                if not isinstance(target, str) or target not in nodes:
                    errors.append(f"{nid}:{cid}: dangling branch {target!r}")
                else:
                    edges[nid].add(target)
                    if nodes[target].get("anchor_id") != anchor_id:
                        errors.append(f"{nid}:{cid}: cross-actor dialogue transition")
            if close:
                closable_nodes.add(nid)
    if used_actions != action_ids:
        errors.append("Dialogue has missing or unexpected action ID coverage")

    entrypoints = dialogue.get("entrypoints")
    if not isinstance(entrypoints, list) or any(not isinstance(e, dict) for e in entrypoints):
        return errors + ["Entrypoints malformed"]
    entry_pairs = []
    roots = []
    for entry in entrypoints:
        pair = (entry.get("anchor_kind"), entry.get("anchor_id"))
        entry_pairs.append(pair)
        if pair not in anchor_pairs:
            errors.append(f"Entrypoint has unbound source anchor {pair}")
        if pair[0] == "npc" and pair[1] not in actor_ids:
            errors.append("Entrypoint references missing NPC")
        if pair[0] == "clue_spawn" and pair[1] not in spawn_ids:
            errors.append("Entrypoint references missing clue prop")
        node_id = entry.get("node_id")
        if node_id not in nodes:
            errors.append("Entrypoint node missing")
        else:
            roots.append(node_id)
            if nodes[node_id].get("anchor_id") != pair[1]:
                errors.append(f"Entrypoint anchor doesn't match node {node_id}")
    if len(entry_pairs) != len(anchor_pairs) or len(set(entry_pairs)) != len(entry_pairs) or (
        set(entry_pairs) != anchor_pairs
    ):
        errors.append("All and only the five original interaction anchors need entrypoints")

    reachable = set()
    frontier = deque(roots)
    while frontier:
        n = frontier.popleft()
        if n in reachable:
            continue
        reachable.add(n)
        frontier.extend(edges[n] - reachable)
    if reachable != set(nodes):
        errors.append("Unreachable dialogue nodes")

    for root in roots:
        seen = set()
        frontier = deque([root])
        found_close = False
        while frontier:
            n = frontier.popleft()
            if n in seen:
                continue
            seen.add(n)
            if n in closable_nodes:
                found_close = True
                break
            frontier.extend(edges[n] - seen)
        if not found_close:
            errors.append(f"{root}: cannot exit dialogue")
    return errors


def main() -> int:
    errors = validate_dialogue(load(DIALOGUE_PATH), load(BINDINGS_PATH),
                               load(QUEST_PATH), load(LAYOUT_PATH))
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: original dialogue graph, five entrypoints, seven action bindings, no dead ends (static only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
