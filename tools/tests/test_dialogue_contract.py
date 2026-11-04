"""Static dialogue and pure reference outcome checks. No Unreal execution is performed."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_dialogue_contract import (
    DIALOGUE_PATH, BINDINGS_PATH, QUEST_PATH, LAYOUT_PATH, load, validate_dialogue
)


def apply_reference(state, action_id, bindings, quest):
    """Non-engine model to check the narrative action sequence; NOT gameplay proof."""
    action = next((a for a in bindings["actions"] if a["id"] == action_id), None)
    before = (state["phase"], frozenset(state["clues"]), state["route"],
              state["evidence"], state["exposure"], state["hunger"])
    if action is None or state["phase"] == "Resolved":
        return False, before
    if action["kind"] == "discover_clue":
        clue = action["clue_id"]
        if clue in state["clues"]:
            return False, before
        state["clues"].add(clue)
        return True, before
    route = next(r for r in quest["routes"] if r["id"] == action["route_id"])
    if not set(route["requires"]).issubset(state["clues"]):
        return False, before
    state["route"] = route["id"]
    state["phase"] = "Resolved"
    state["evidence"] = route["evidence"]
    state["exposure"] = route["exposure_delta"]
    return True, before


class DialogueContract(unittest.TestCase):
    def setUp(self):
        self.dialogue = copy.deepcopy(load(DIALOGUE_PATH))
        self.bindings = copy.deepcopy(load(BINDINGS_PATH))
        self.quest = copy.deepcopy(load(QUEST_PATH))
        self.layout = copy.deepcopy(load(LAYOUT_PATH))

    def errors(self):
        return validate_dialogue(self.dialogue, self.bindings, self.quest, self.layout)

    def test_valid_original_dialogue(self):
        self.assertEqual(self.errors(), [])

    def test_dialogue_must_remain_noncanonical(self):
        self.dialogue["status"] = "APPROVED_CANON"
        self.assertTrue(self.errors())

    def test_world_interaction_must_not_be_claimed(self):
        self.dialogue["runtime_status"] = "RUNNING_IN_ENGINE"
        self.assertTrue(self.errors())

    def test_missing_entrypoint_rejected(self):
        self.dialogue["entrypoints"].pop()
        self.assertTrue(self.errors())

    def test_duplicate_entrypoint_rejected(self):
        self.dialogue["entrypoints"][0] = copy.deepcopy(self.dialogue["entrypoints"][1])
        self.assertTrue(self.errors())

    def test_cross_actor_branch_rejected(self):
        node = next(n for n in self.dialogue["nodes"] if n["id"] == "mara_start")
        node["choices"][0]["on_success"] = "nico_route"
        self.assertTrue(self.errors())

    def test_missing_action_binding_rejected(self):
        node = next(n for n in self.dialogue["nodes"] if n["id"] == "nico_start")
        node["choices"][0]["action_id"] = "unknown_action"
        self.assertTrue(self.errors())

    def test_missing_failure_branch_rejected(self):
        node = next(n for n in self.dialogue["nodes"] if n["id"] == "etta_start")
        node["choices"][0]["on_failure"] = None
        self.assertTrue(self.errors())

    def test_identical_success_and_failure_rejected(self):
        node = next(n for n in self.dialogue["nodes"] if n["id"] == "mara_start")
        node["choices"][0]["on_failure"] = "mara_ledger"
        self.assertTrue(self.errors())

    def test_dangling_target_rejected(self):
        node = next(n for n in self.dialogue["nodes"] if n["id"] == "mara_start")
        node["choices"][0]["on_success"] = "missing_node"
        self.assertTrue(self.errors())

    def test_unreachable_node_rejected(self):
        self.dialogue["nodes"].append({
            "id":"orphan", "anchor_id":"mara_vale", "speaker_id":"mara_vale",
            "line":"This is deliberately unreachable dialogue for a test case.",
            "choices":[{"id":"orphan_close","player_text":"Close the conversation.",
                        "action_id":None,"on_success":None,"on_failure":None,"close":True}]
        })
        self.assertTrue(self.errors())

    def test_duplicate_choice_rejected(self):
        self.dialogue["nodes"][1]["choices"][0]["id"] = self.dialogue["nodes"][0]["choices"][0]["id"]
        self.assertTrue(self.errors())

    def test_caption_length_rejected(self):
        self.dialogue["nodes"][0]["line"] = "short"
        self.assertTrue(self.errors())

    def test_invalid_speaker_rejected(self):
        self.dialogue["nodes"][0]["speaker_id"] = "fictional_ghost"
        self.assertTrue(self.errors())

    def test_forced_feeding_claim_rejected(self):
        self.dialogue["constraints"]["no_forced_feeding"] = False
        self.assertTrue(self.errors())

    def test_entrypoint_exit_required(self):
        node = next(n for n in self.dialogue["nodes"] if n["id"] == "etta_start")
        node["choices"] = [
            {"id":"etta_infinite","player_text":"Stay here forever.",
             "action_id":None,"on_success":"etta_start","on_failure":None,"close":False}
        ]
        self.assertTrue(self.errors())

    def test_three_nonviolent_reference_routes(self):
        sequences = (
            (["inspect_receipt", "ask_mara_about_ledger", "commit_dialogue"],
             "dialogue", "redacted_shift_log", 0),
            (["ask_nico_about_route", "commit_stealth"],
             "stealth", "timecard_photo", 12),
            (["inspect_annex_badge", "commit_confrontation"],
             "confrontation", "discarded_register", 25),
        )
        for actions, route_id, evidence, exposure in sequences:
            state = {"phase":"Investigating", "clues":set(), "route":None,
                     "evidence":None, "exposure":0, "hunger":25}
            for action in actions:
                success, _ = apply_reference(state, action, self.bindings, self.quest)
                self.assertTrue(success, action)
            self.assertEqual(state["route"], route_id)
            self.assertEqual(state["evidence"], evidence)
            self.assertEqual(state["exposure"], exposure)
            self.assertEqual(state["hunger"], 25)
            final = copy.deepcopy(state)
            success, _ = apply_reference(state, "commit_confrontation", self.bindings, self.quest)
            self.assertFalse(success)
            self.assertEqual(state, final)

    def test_failed_route_is_retryable_in_reference_model(self):
        state = {"phase":"Investigating", "clues":set(), "route":None,
                 "evidence":None, "exposure":0, "hunger":25}
        ok, before = apply_reference(state, "commit_dialogue", self.bindings, self.quest)
        self.assertFalse(ok)
        self.assertEqual(state["phase"], before[0])
        self.assertEqual(state["clues"], set())
        for action in ("inspect_receipt", "ask_mara_about_ledger", "commit_dialogue"):
            ok, _ = apply_reference(state, action, self.bindings, self.quest)
            self.assertTrue(ok)
        self.assertEqual(state["route"], "dialogue")


if __name__ == "__main__":
    unittest.main()
