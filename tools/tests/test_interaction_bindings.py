"""Synthetic binding fixtures; never used as evidence of a native Unreal execution."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_interaction_bindings import (
    BINDINGS_PATH, QUEST_PATH, LAYOUT_PATH, BRIDGE_CPP_PATH, load, validate_bindings
)


class GlassbendBindingContract(unittest.TestCase):
    def setUp(self):
        self.bindings = copy.deepcopy(load(BINDINGS_PATH))
        self.quest = copy.deepcopy(load(QUEST_PATH))
        self.layout = copy.deepcopy(load(LAYOUT_PATH))
        self.cpp = BRIDGE_CPP_PATH.read_text(encoding="utf-8")

    def validate(self):
        return validate_bindings(self.bindings, self.quest, self.layout, self.cpp)

    def test_valid_original_interaction_bridge(self):
        self.assertEqual(self.validate(), [])

    def test_unknown_action_rejected(self):
        self.bindings["actions"][0]["id"] = "interact_anywhere"
        self.assertTrue(self.validate())

    def test_duplicate_action_rejected(self):
        self.bindings["actions"][1]["id"] = self.bindings["actions"][0]["id"]
        self.assertTrue(self.validate())

    def test_mismatched_quest_id_rejected(self):
        self.bindings["quest_id"] = "other_scene"
        self.assertTrue(self.validate())

    def test_mismatched_layout_id_rejected(self):
        self.bindings["layout_id"] = "another_layout"
        self.assertTrue(self.validate())

    def test_proximity_claim_rejected(self):
        self.bindings["world_interaction_gate"] = "PASS"
        self.assertTrue(self.validate())

    def test_automatic_feeding_claim_rejected(self):
        self.bindings["constraints"]["no_automatic_feeding"] = False
        self.assertTrue(self.validate())

    def test_missing_npc_anchor_rejected(self):
        self.layout["actors"] = [a for a in self.layout["actors"] if a["id"] != "nico_bell"]
        self.assertTrue(self.validate())

    def test_wrong_clue_rejected(self):
        self.bindings["actions"][0]["clue_id"] = "annex_badge"
        self.assertTrue(self.validate())

    def test_wrong_route_rejected(self):
        self.bindings["actions"][-1]["route_id"] = "dialogue"
        self.assertTrue(self.validate())

    def test_extra_action_rejected(self):
        self.bindings["actions"].append(copy.deepcopy(self.bindings["actions"][0]))
        self.assertTrue(self.validate())

    def test_unexpected_route_field_on_clue_rejected(self):
        self.bindings["actions"][0]["route_id"] = "dialogue"
        self.assertTrue(self.validate())

    def test_cpp_action_mismatch_rejected(self):
        self.cpp = self.cpp.replace('"commit_stealth"', '"commit_observe"', 1)
        self.assertTrue(self.validate())

    def test_cpp_clue_mismatch_rejected(self):
        self.cpp = self.cpp.replace(
            'DiscoverClue(FName(TEXT("shift_receipt")))',
            'DiscoverClue(FName(TEXT("annex_badge")))', 1,
        )
        self.assertTrue(self.validate())

    def test_cpp_route_mismatch_rejected(self):
        self.cpp = self.cpp.replace(
            'TryResolve(EACIDResolutionRoute::Confrontation)',
            'TryResolve(EACIDResolutionRoute::Dialogue)', 1,
        )
        self.assertTrue(self.validate())

    def test_malformed_nonstring_action_id_rejected(self):
        self.bindings["actions"][0]["id"] = {"not": "an identifier"}
        self.assertTrue(self.validate())

    def test_direct_hunger_mutation_rejected(self):
        self.cpp = self.cpp.replace(
            'return false;\n}',
            'QuestLedger->Feed(10);\n    return false;\n}', 1,
        )
        self.assertTrue(self.validate())

    def test_cpp_duplicate_dispatch_rejected(self):
        start = self.cpp.index('    if (ActionId == FName(TEXT("inspect_receipt")))')
        end = self.cpp.index('    if (ActionId == FName(TEXT("ask_mara_about_ledger")))')
        self.cpp = self.cpp[:end] + self.cpp[start:end] + self.cpp[end:]
        self.assertTrue(self.validate())


if __name__ == "__main__":
    unittest.main()
