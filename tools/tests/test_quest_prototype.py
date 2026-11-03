"""Tests are for the portable quest *proposal*, not the Unreal game."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_quest_prototype import load_quest, validate_quest, resolve


class QuestPrototypeTests(unittest.TestCase):
    def setUp(self):
        self.data = load_quest()
        self.initial = {"phase": "Investigating", "mara_trust": 0, "public_exposure": 0, "hunger": 25}

    def test_valid_original_prototype(self):
        self.assertEqual(validate_quest(self.data), [])

    def test_every_route_can_complete_from_obtainable_clues(self):
        available = {c["id"] for c in self.data["clues"] if not c["requires"]}
        for route in self.data["routes"]:
            with self.subTest(route=route["id"]):
                after = resolve(self.data, self.initial, route["id"], available)
                self.assertEqual(after["phase"], "Resolved")
                self.assertTrue(after["evidence_acquired"])
                self.assertEqual(after["resolution_method"], route["id"])
                self.assertEqual(after["hunger"], 25)

    def test_missing_clues_are_retryable(self):
        before = copy.deepcopy(self.initial)
        self.assertEqual(resolve(self.data, before, "dialogue", set()), before)

    def test_resolution_is_idempotent_and_cannot_be_overwritten(self):
        state = resolve(self.data, self.initial, "dialogue", {"shift_receipt", "ledger_gap"})
        again = resolve(self.data, state, "confrontation", {"annex_badge"})
        self.assertEqual(again, state)

    def test_invalid_route_fails(self):
        with self.assertRaises(ValueError):
            resolve(self.data, self.initial, "nonexistent", set())

    def test_route_requires_known_clue(self):
        bad = copy.deepcopy(self.data)
        bad["routes"][0]["requires"].append("imaginary_clue")
        self.assertTrue(validate_quest(bad))

    def test_violence_or_feeding_fails_contract(self):
        bad = copy.deepcopy(self.data)
        bad["routes"][0]["forced_feeding"] = True
        self.assertTrue(validate_quest(bad))

    def test_duplicate_route_rejected(self):
        bad = copy.deepcopy(self.data)
        bad["routes"][0]["id"] = bad["routes"][1]["id"]
        self.assertTrue(validate_quest(bad))

    def test_trust_exposure_are_distinct_by_route(self):
        available = {c["id"] for c in self.data["clues"]}
        states = [resolve(self.data, self.initial, route["id"], available) for route in self.data["routes"]]
        self.assertEqual(len({(x["mara_trust"], x["public_exposure"], x["evidence"]) for x in states}), 3)


if __name__ == "__main__":
    unittest.main()
