#!/usr/bin/env python3
"""Noncanonical, text-only Glassbend playthrough preview.

This portable Python program is NOT Unreal Engine gameplay, a built game, a
world-space interaction check, an approved story, or a UE SaveGame system. Optional local Python save files are not native persistence.
It uses existing version-1 quest, dialogue, and action contracts.
"""
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from glassbend_savegame import (
    default_save_path, load_preview_state, save_preview_state,
)
from typing import Optional

from validate_quest_prototype import load_quest, resolve, validate_quest
from validate_glassbend_layout import LAYOUT_PATH, load_json, validate_layout
from validate_interaction_bindings import (
    BINDINGS_PATH, BRIDGE_CPP_PATH, load as load_bindings, validate_bindings,
)
from validate_dialogue_contract import (
    DIALOGUE_PATH, load as load_dialogue, validate_dialogue,
)


@dataclass
class PreviewState:
    phase: str = "Investigating"
    clues: set[str] = field(default_factory=set)
    route: Optional[str] = None
    evidence: Optional[str] = None
    mara_trust: int = 0
    public_exposure: int = 0
    hunger: int = 25

    def summary(self) -> str:
        return (
            f"Phase: {self.phase} | Clues: {', '.join(sorted(self.clues)) or '(none)'}"
            f" | Route: {self.route or '(none)'} | Evidence: {self.evidence or '(none)'}"
            f" | Mara trust: {self.mara_trust:+d} | Exposure: {self.public_exposure}"
            f" | Hunger: {self.hunger}"
        )


@dataclass(frozen=True)
class ChoiceResult:
    action_id: Optional[str]
    action_succeeded: Optional[bool]
    next_node_id: Optional[str]
    closed: bool


class PreviewSession:
    """One in-memory single-player quest preview, with explicit source IDs."""

    def __init__(self, quest: dict, layout: dict, bindings: dict, dialogue: dict):
        problems = (
            validate_quest(quest)
            + validate_layout(layout, quest)
            + validate_bindings(bindings, quest, layout, BRIDGE_CPP_PATH.read_text(encoding="utf-8"))
            + validate_dialogue(dialogue, bindings, quest, layout)
        )
        if problems:
            raise ValueError("Refusing drifted/noncanonical preview contract: " + "; ".join(problems))
        self.quest = quest
        self.layout = layout
        self.bindings = bindings
        self.dialogue = dialogue
        self.state = PreviewState()
        self.nodes = {node["id"]: node for node in dialogue["nodes"]}
        self.actions = {action["id"]: action for action in bindings["actions"]}
        self.entrypoints = {(e["anchor_kind"], e["anchor_id"]): e["node_id"]
                            for e in dialogue["entrypoints"]}
        self.current_node_id: Optional[str] = None

    def start(self, anchor_kind: str, anchor_id: str) -> dict:
        """Open a source-defined dialogue/prop entrypoint. NOT a world target check."""
        key = (anchor_kind, anchor_id)
        if key not in self.entrypoints:
            raise ValueError(f"Unknown preview entrypoint: {anchor_kind}/{anchor_id}")
        self.current_node_id = self.entrypoints[key]
        return self.current_node()

    def current_node(self) -> dict:
        if self.current_node_id is None:
            raise ValueError("No open conversation")
        return self.nodes[self.current_node_id]

    def apply_action(self, action_id: str) -> bool:
        """Pure reference state. Does not invoke C++ or assert player proximity."""
        action = self.actions.get(action_id)
        if action is None or self.state.phase != "Investigating":
            return False
        if action["kind"] == "discover_clue":
            clue = action["clue_id"]
            if clue in self.state.clues:
                return False
            self.state.clues.add(clue)
            return True
        if action["kind"] != "resolve_route":
            return False
        reference_state = {
            "phase": self.state.phase,
            "mara_trust": self.state.mara_trust,
            "public_exposure": self.state.public_exposure,
            "hunger": self.state.hunger,
        }
        # Use the original quest reference transition; never invent a second
        # route/evidence/trust/exposure table in this preview.
        outcome = resolve(self.quest, reference_state, action["route_id"], set(self.state.clues))
        if outcome.get("phase") != "Resolved":
            return False
        self.state.phase = outcome["phase"]
        self.state.route = outcome["resolution_method"]
        self.state.evidence = outcome["evidence"]
        self.state.mara_trust = outcome["mara_trust"]
        self.state.public_exposure = outcome["public_exposure"]
        self.state.hunger = outcome["hunger"]
        return True

    def choose(self, choice_id: str) -> ChoiceResult:
        """Take a currently displayed choice; fail closed on unknown choice IDs."""
        node = self.current_node()
        choice = next((c for c in node["choices"] if c["id"] == choice_id), None)
        if choice is None:
            raise ValueError(f"Choice is not offered here: {choice_id}")
        action_id = choice["action_id"]
        outcome = None if action_id is None else self.apply_action(action_id)
        if choice["close"]:
            self.current_node_id = None
        else:
            self.current_node_id = (
                choice["on_success"] if outcome is not False else choice["on_failure"]
            )
        return ChoiceResult(action_id, outcome, self.current_node_id,
                            self.current_node_id is None)


def make_session() -> PreviewSession:
    return PreviewSession(
        load_quest(), load_json(LAYOUT_PATH), load_bindings(BINDINGS_PATH),
        load_dialogue(DIALOGUE_PATH),
    )


ENTRY_LABELS = {
    ("clue_spawn", "shift_receipt"): "Inspect the shelter pay envelope",
    ("npc", "mara_vale"): "Speak with Mara, the night archivist",
    ("npc", "nico_bell"): "Speak with Nico, the courier",
    ("clue_spawn", "annex_badge"): "Inspect the transit-annex visitor badge",
    ("npc", "etta_quill"): "Speak with Etta, the annex manager",
}
DEMO_PATHS = {
    "dialogue": [
        (("clue_spawn", "shift_receipt"), ("receipt_inspect", "receipt_found_close")),
        (("npc", "mara_vale"), ("mara_ask", "mara_ledger_close")),
        (("npc", "mara_vale"), ("mara_resolve", "mara_resolved_close")),
    ],
    "stealth": [
        (("npc", "nico_bell"), ("nico_ask", "nico_route_close")),
        (("npc", "nico_bell"), ("nico_resolve", "nico_resolved_close")),
    ],
    "confrontation": [
        (("clue_spawn", "annex_badge"), ("badge_inspect", "badge_found_close")),
        (("npc", "etta_quill"), ("etta_resolve", "etta_resolved_close")),
    ],
}


def run_demo() -> int:
    print("GLASSBEND: SOURCE-ONLY TEXT PREVIEW. Not Unreal gameplay or approved canon.")
    for name, segments in DEMO_PATHS.items():
        session = make_session()
        print(f"\n=== Reference path: {name} ===")
        for (anchor_kind, anchor_id), choices in segments:
            node = session.start(anchor_kind, anchor_id)
            print(f"[{anchor_id}] {node['line']}")
            for choice_id in choices:
                chosen = next(c for c in session.current_node()["choices"] if c["id"] == choice_id)
                print(f"> {chosen['player_text']}")
                result = session.choose(choice_id)
                if result.action_id is not None:
                    print(f"  [{result.action_id}: {'accepted' if result.action_succeeded else 'rejected'}]")
                if result.next_node_id:
                    print(f"  {session.current_node()['line']}")
        print(session.state.summary())
        if session.state.route != name:
            raise ValueError(f"Demo route did not resolve as expected: {name}")
    return 0


def show_prelude() -> None:
    print("\nARCH CITY IN DARKNESS — THE UNCLAIMED HOUR")
    print("Glassbend, Columbus. After midnight.\n")
    print("Rain threads through the shelter lights. Across the street, the archive is still open; "
          "farther down, a bicycle lamp disappears toward the river.")
    print("Hunger presses at the edge of your attention. The people sheltering nearby "
          "have their own reasons to be out tonight; none owes you an answer.")
    print("A pay envelope left beneath the timetable points to an hour that the schedule says never happened. "
          "A worker is missing, and somebody may know why.")
    print("Where you begin is up to you.\n")


def run_interactive(save_file: Optional[Path] = None) -> int:
    session = make_session()
    save_file = Path(save_file) if save_file is not None else default_save_path()
    print("GLASSBEND: SOURCE-ONLY TEXT PREVIEW; noncanonical and NOT playable Unreal.")
    print("Choose a location/choice number; at the street menu, n=new, s=save, l=load, q=quit.")
    print("Local saves are opt-in; files are outside the public repository.")
    show_prelude()
    anchors = list(ENTRY_LABELS.items())
    while True:
        print("\n" + session.state.summary())
        resolved = session.state.phase == "Resolved"
        if resolved:
            print("This investigation is resolved. Further quest changes are locked.")
        else:
            for i, (_, label) in enumerate(anchors, 1):
                print(f"  {i}. {label}")
        selection = input("Visit (1-5, n=new, s=save, l=load, q=quit): ").strip().lower()
        if selection == "q":
            return 0
        if selection == "n":
            confirmation = input("Start a new investigation? Unsaved progress will be lost (y/N): ").strip().lower()
            if confirmation == "y":
                session = make_session()
                print("New investigation started. Your saved file was not changed.")
                show_prelude()
            else:
                print("New investigation cancelled; current progress is unchanged.")
            continue
        if selection == "s":
            try:
                save_preview_state(save_file, session.state, session.quest)
                print(f"Local preview saved: {save_file}")
            except (OSError, ValueError) as exc:
                print(f"Save rejected; previous file remains unchanged: {exc}")
            continue
        if selection == "l":
            try:
                # Read/validate first and only swap the active session on success.
                payload = load_preview_state(save_file, session.quest)
                new_session = make_session()
                new_session.state = PreviewState(
                    **{**payload, "clues": set(payload["clues"])}
                )
                session = new_session
                print(f"Local preview loaded: {save_file}")
            except (OSError, ValueError) as exc:
                print(f"Load rejected; current game remains unchanged: {exc}")
            continue
        if resolved:
            print("This investigation is already resolved; start a new run to choose again.")
            continue
        if not selection.isdecimal() or not 1 <= int(selection) <= len(anchors):
            print("Invalid location; no changes made.")
            continue
        (anchor_kind, anchor_id), _ = anchors[int(selection) - 1]
        session.start(anchor_kind, anchor_id)
        while session.current_node_id is not None:
            node = session.current_node()
            print(f"\n{node['speaker_id']}: {node['line']}")
            for i, c in enumerate(node["choices"], 1):
                print(f"  {i}. {c['player_text']}")
            response = input("Choose (number; q ends preview): ").strip().lower()
            if response == "q":
                return 0
            if not response.isdecimal() or not 1 <= int(response) <= len(node["choices"]):
                print("Invalid choice; no changes made.")
                continue
            result = session.choose(node["choices"][int(response) - 1]["id"])
            if result.action_id is not None and not result.action_succeeded:
                print("That action did not meet its quest prerequisites (or was already used).")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true",
                        help="Run the three deterministic text-only quest demonstrations")
    parser.add_argument("--save-file", type=Path, default=None,
                        help="Optional local save path (only written after an explicit s command)")
    args = parser.parse_args()
    return run_demo() if args.demo else run_interactive(args.save_file)


if __name__ == "__main__":
    raise SystemExit(main())
