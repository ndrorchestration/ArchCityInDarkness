"""Offline M009 contract regressions; synthetic mutations are NOT Unreal tests."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_m009_dialogue_world_contract import (
    BINDINGS, BRIDGE_CPP, CHAR_CPP, GRAPH, INPUT, LAYOUT, MARKER_CPP, QUEST,
    REQUIRED, ROOT, validate_world_dialogue,
)


class M009DialogueWorldContractTests(unittest.TestCase):
    def setUp(self):
        self.sources = {p: (ROOT / p).read_text(encoding="utf-8") for p in REQUIRED}

    def check(self):
        return validate_world_dialogue(self.sources)

    def test_current_graph_and_world_source_contract(self):
        self.assertEqual(self.check(), [])

    def test_missing_source_fails_closed(self):
        self.sources.pop(MARKER_CPP)
        self.assertTrue(self.check())

    def test_malformed_graph_fails_closed(self):
        self.sources[GRAPH] = '{"nodes":'
        self.assertTrue(self.check())

    def test_wrong_dialogue_anchor_fails_closed(self):
        graph = json.loads(self.sources[GRAPH])
        graph["entrypoints"][0]["anchor_id"] = "unknown_receipt"
        self.sources[GRAPH] = json.dumps(graph)
        self.assertTrue(self.check())

    def test_actor_allowlist_drift_fails_closed(self):
        self.sources[MARKER_CPP] = self.sources[MARKER_CPP].replace(
            'Candidate == TEXT("mara_vale")', 'Candidate == TEXT("unknown_vale")', 1)
        self.assertTrue(self.check())

    def test_implicit_mara_resolution_rejected(self):
        self.sources[MARKER_CPP] = self.sources[MARKER_CPP].replace(
            'Ledger->HasClue(TEXT("ledger_gap")) ? NAME_None :',
            'Ledger->HasClue(TEXT("ledger_gap")) ? FName(TEXT("commit_dialogue")) :', 1)
        self.assertTrue(self.check())

    def test_implicit_nico_resolution_rejected(self):
        self.sources[MARKER_CPP] = self.sources[MARKER_CPP].replace(
            'Ledger->HasClue(TEXT("route_note")) ? NAME_None :',
            'Ledger->HasClue(TEXT("route_note")) ? FName(TEXT("commit_stealth")) :', 1)
        self.assertTrue(self.check())

    def test_implicit_etta_resolution_rejected(self):
        self.sources[MARKER_CPP] = self.sources[MARKER_CPP].replace(
            'if (AnchorId == TEXT("etta_quill"))\n        return NAME_None;',
            'if (AnchorId == TEXT("etta_quill"))\n        return FName(TEXT("commit_confrontation"));', 1)
        self.assertTrue(self.check())

    def test_missing_route_choice_rejected(self):
        graph = json.loads(self.sources[GRAPH])
        for node in graph["nodes"]:
            for c in node["choices"]:
                if c.get("action_id") == "commit_stealth":
                    c["action_id"] = "commit_dialogue"
        self.sources[GRAPH] = json.dumps(graph)
        self.assertTrue(self.check())

    def test_missing_bridge_action_rejected(self):
        self.sources[BRIDGE_CPP] = self.sources[BRIDGE_CPP].replace(
            'FName(TEXT("commit_stealth"))', 'FName(TEXT("unknown_route"))', 1)
        self.assertTrue(self.check())

    def test_forced_feeding_rejected(self):
        q = json.loads(self.sources[QUEST])
        q["routes"][0]["hunger_delta"] = -10
        self.sources[QUEST] = json.dumps(q)
        self.assertTrue(self.check())

    def test_world_dispatch_drift_rejected(self):
        self.sources[MARKER_CPP] = self.sources[MARKER_CPP].replace(
            'UACIDQuestInteractionBridge::TryApplyAction(Character->GetQuestLedger(), Action)',
            'true', 1)
        self.assertTrue(self.check())

    def test_missing_player_input_rejected(self):
        self.sources[CHAR_CPP] = self.sources[CHAR_CPP].replace(
            'BindAction(TEXT("Interact")', 'BindAction(TEXT("Talk")', 1)
        self.assertTrue(self.check())

    def test_no_extra_auto_action_rejected(self):
        self.sources[MARKER_CPP] = self.sources[MARKER_CPP].replace(
            'return NAME_None;\n    return NAME_None;\n}',
            'return FName(TEXT("commit_confrontation"));\n    return NAME_None;\n}', 1)
        self.assertTrue(self.check())


if __name__ == "__main__":
    unittest.main()
