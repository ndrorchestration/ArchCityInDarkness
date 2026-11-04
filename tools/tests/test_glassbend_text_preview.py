"""Source-only terminal preview regression suite; not native Unreal evidence."""
import contextlib
import io
import unittest
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from glassbend_text_preview import PreviewSession, make_session, run_demo, DEMO_PATHS


class GlassbendCLIContract(unittest.TestCase):
    def setUp(self):
        self.s = make_session()

    def choose(self, anchor, *choice_ids):
        self.s.start(*anchor)
        result = None
        for choice_id in choice_ids:
            result = self.s.choose(choice_id)
        return result

    def test_initial_state_is_unresolved(self):
        self.assertEqual(self.s.state.phase, "Investigating")
        self.assertEqual(self.s.state.hunger, 25)
        self.assertEqual(self.s.state.clues, set())
        self.assertIsNone(self.s.state.evidence)

    def test_five_source_entrypoints_exactly(self):
        self.assertEqual(len(self.s.entrypoints), 5)
        self.assertIn(("npc", "mara_vale"), self.s.entrypoints)

    def test_receipt_action_discovers_once(self):
        first = self.choose(("clue_spawn", "shift_receipt"), "receipt_inspect")
        self.assertTrue(first.action_succeeded)
        self.assertIn("shift_receipt", self.s.state.clues)
        self.s.choose("receipt_found_close")
        repeat = self.choose(("clue_spawn", "shift_receipt"), "receipt_inspect")
        self.assertFalse(repeat.action_succeeded)
        self.assertEqual(repeat.next_node_id, "receipt_seen")

    def test_mara_route_rejects_missing_clues(self):
        result = self.choose(("npc", "mara_vale"), "mara_resolve")
        self.assertFalse(result.action_succeeded)
        self.assertEqual(result.next_node_id, "mara_missing")
        self.assertIsNone(self.s.state.route)
        self.assertEqual(self.s.state.public_exposure, 0)

    def test_mara_route_completes_when_prepared(self):
        self.choose(("clue_spawn", "shift_receipt"), "receipt_inspect")
        self.choose(("npc", "mara_vale"), "mara_ask")
        result = self.choose(("npc", "mara_vale"), "mara_resolve")
        self.assertTrue(result.action_succeeded)
        self.assertEqual(self.s.state.route, "dialogue")
        self.assertEqual(self.s.state.evidence, "redacted_shift_log")
        self.assertEqual(self.s.state.mara_trust, 1)
        self.assertEqual(self.s.state.public_exposure, 0)
        self.assertEqual(self.s.state.hunger, 25)

    def test_nico_stealth_route_completes(self):
        self.choose(("npc", "nico_bell"), "nico_ask")
        result = self.choose(("npc", "nico_bell"), "nico_resolve")
        self.assertTrue(result.action_succeeded)
        self.assertEqual(self.s.state.route, "stealth")
        self.assertEqual(self.s.state.evidence, "timecard_photo")
        self.assertEqual(self.s.state.public_exposure, 12)
        self.assertEqual(self.s.state.mara_trust, 0)
        self.assertEqual(self.s.state.hunger, 25)

    def test_etta_confrontation_route_completes_without_feeding(self):
        self.choose(("clue_spawn", "annex_badge"), "badge_inspect")
        result = self.choose(("npc", "etta_quill"), "etta_resolve")
        self.assertTrue(result.action_succeeded)
        self.assertEqual(self.s.state.route, "confrontation")
        self.assertEqual(self.s.state.evidence, "discarded_register")
        self.assertEqual(self.s.state.public_exposure, 25)
        self.assertEqual(self.s.state.mara_trust, -1)
        self.assertEqual(self.s.state.hunger, 25)

    def test_resolved_quest_remains_immutable(self):
        self.choose(("npc", "nico_bell"), "nico_ask")
        self.choose(("npc", "nico_bell"), "nico_resolve")
        before = replace(self.s.state, clues=set(self.s.state.clues))
        self.assertFalse(self.s.apply_action("commit_confrontation"))
        self.assertFalse(self.s.apply_action("inspect_receipt"))
        self.assertEqual(self.s.state, before)

    def test_invalid_action_fails_without_mutation(self):
        before = replace(self.s.state, clues=set(self.s.state.clues))
        self.assertFalse(self.s.apply_action("forged_unverified_action"))
        self.assertEqual(self.s.state, before)

    def test_unknown_entrypoint_fails_without_mutation(self):
        before = replace(self.s.state, clues=set(self.s.state.clues))
        with self.assertRaises(ValueError):
            self.s.start("npc", "unknown_person")
        self.assertEqual(self.s.state, before)

    def test_choice_not_present_fails_closed(self):
        self.s.start("npc", "mara_vale")
        before = replace(self.s.state, clues=set(self.s.state.clues))
        with self.assertRaises(ValueError):
            self.s.choose("etta_resolve")
        self.assertEqual(self.s.state, before)
        self.assertEqual(self.s.current_node_id, "mara_start")

    def test_close_choice_changes_no_quest_state(self):
        result = self.choose(("npc", "mara_vale"), "mara_leave")
        self.assertTrue(result.closed)
        self.assertIsNone(result.action_id)
        self.assertIsNone(result.action_succeeded)
        self.assertIsNone(self.s.state.route)
        self.assertEqual(self.s.state.clues, set())

    def test_reference_demo_paths_all_terminate(self):
        for route, segments in DEMO_PATHS.items():
            session = make_session()
            for anchor, choices in segments:
                session.start(*anchor)
                for cid in choices:
                    session.choose(cid)
                self.assertIsNone(session.current_node_id)
            self.assertEqual(session.state.route, route)
            self.assertEqual(session.state.phase, "Resolved")
            self.assertEqual(session.state.hunger, 25)

    def test_printed_demo_has_clear_non_unreal_disclaimer(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = run_demo()
        self.assertEqual(status, 0)
        printed = out.getvalue()
        self.assertIn("Not Unreal gameplay or approved canon", printed)
        for route in ("dialogue", "stealth", "confrontation"):
            self.assertIn("Reference path: " + route, printed)
        self.assertEqual(printed.count("Phase: Resolved"), 3)

    def test_source_contract_drift_fails_previewer(self):
        import copy
        quest = copy.deepcopy(self.s.quest)
        quest["status"] = "APPROVED_CANON"
        with self.assertRaises(ValueError):
            PreviewSession(quest, self.s.layout, self.s.bindings, self.s.dialogue)

    def test_never_automatically_mutates_hunger(self):
        for action in self.s.actions:
            session = make_session()
            session.apply_action(action)
            self.assertEqual(session.state.hunger, 25)


if __name__ == "__main__":
    unittest.main()
