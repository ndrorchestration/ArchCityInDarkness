"""Opt-in local text-save tests. Not Unreal-native SaveGame proof."""
import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from glassbend_text_preview import make_session, run_interactive
from glassbend_savegame import (
    MAX_SAVE_BYTES, _canonical, _envelope, default_save_path,
    load_preview_state, save_preview_state, state_to_payload, validate_state,
)


class LocalPreviewSaveTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "private" / "save_v1.json"
        self.session = make_session()

    def save(self):
        save_preview_state(self.path, self.session.state, self.session.quest)

    def load(self):
        return load_preview_state(self.path, self.session.quest)

    def rewrite(self, envelope):
        self.path.write_bytes(_canonical(envelope) + b"\n")

    def forged(self, changes):
        payload = self.load()
        payload.update(changes)
        self.rewrite(_envelope(payload, self.session.quest))

    def test_no_file_until_save_explicit(self):
        self.assertFalse(self.path.exists())
        with patch("builtins.input", side_effect=["q"]), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(run_interactive(self.path), 0)
        self.assertFalse(self.path.exists())

    def test_opening_introduces_investigation_before_player_chooses(self):
        with patch("builtins.input", side_effect=["q"]), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(run_interactive(self.path), 0)
        opening = out.getvalue()
        self.assertLess(opening.index("THE UNCLAIMED HOUR"), opening.index("Inspect the shelter pay envelope"))
        self.assertIn("an hour that the schedule says never happened", opening)
        self.assertFalse(self.path.exists())

    def test_unresolved_roundtrip_and_stable_clue_order(self):
        self.session.apply_action("ask_nico_about_route")
        self.session.apply_action("inspect_receipt")
        self.save()
        payload = self.load()
        self.assertEqual(payload["phase"], "Investigating")
        self.assertEqual(payload["clues"], ["shift_receipt", "route_note"])
        self.assertEqual(payload["hunger"], 25)

    def test_three_distinct_resolved_saves(self):
        sequences = [
            (("inspect_receipt", "ask_mara_about_ledger", "commit_dialogue"),
             "dialogue", "redacted_shift_log", 1, 0),
            (("ask_nico_about_route", "commit_stealth"),
             "stealth", "timecard_photo", 0, 12),
            (("inspect_annex_badge", "commit_confrontation"),
             "confrontation", "discarded_register", -1, 25),
        ]
        for actions, route, evidence, trust, exposure in sequences:
            with self.subTest(route=route):
                self.session = make_session()
                for action in actions:
                    self.assertTrue(self.session.apply_action(action))
                self.save()
                payload = self.load()
                self.assertEqual(payload["phase"], "Resolved")
                self.assertEqual(payload["route"], route)
                self.assertEqual(payload["evidence"], evidence)
                self.assertEqual(payload["mara_trust"], trust)
                self.assertEqual(payload["public_exposure"], exposure)
                self.assertEqual(payload["hunger"], 25)

    def test_save_is_deterministic(self):
        self.session.apply_action("inspect_receipt")
        self.save()
        original = self.path.read_bytes()
        self.save()
        self.assertEqual(original, self.path.read_bytes())

    def test_reject_corrupted_checksum(self):
        self.save()
        encoded = self.path.read_bytes()
        self.path.write_bytes(encoded.replace(b"Investigating", b"Investigation", 1))
        with self.assertRaisesRegex(ValueError, "checksum"):
            self.load()

    def test_reject_unsupported_schema(self):
        self.save()
        envelope = json.loads(self.path.read_text(encoding="utf-8"))
        envelope["schema_version"] = 2
        self.rewrite(envelope)
        with self.assertRaisesRegex(ValueError, "schema"):
            self.load()

    def test_reject_wrong_quest(self):
        self.save()
        envelope = json.loads(self.path.read_text(encoding="utf-8"))
        envelope["quest_id"] = "unrelated"
        self.rewrite(envelope)
        with self.assertRaisesRegex(ValueError, "different quest"):
            self.load()

    def test_reject_valid_checksum_but_impossible_resolution(self):
        self.session.apply_action("inspect_receipt")
        self.session.apply_action("ask_mara_about_ledger")
        self.session.apply_action("commit_dialogue")
        self.save()
        self.forged({"public_exposure": 99})
        with self.assertRaisesRegex(ValueError, "contradicts"):
            self.load()

    def test_reject_missing_route_prerequisite(self):
        self.session.apply_action("inspect_receipt")
        self.session.apply_action("ask_mara_about_ledger")
        self.session.apply_action("commit_dialogue")
        self.save()
        self.forged({"clues": ["shift_receipt"]})
        with self.assertRaisesRegex(ValueError, "prerequisites"):
            self.load()

    def test_reject_resolution_field_in_investigation(self):
        self.save()
        self.forged({"evidence": "redacted_shift_log"})
        with self.assertRaisesRegex(ValueError, "resolved outcomes"):
            self.load()

    def test_reject_unknown_clue(self):
        self.save()
        self.forged({"clues": ["phantom_clue"]})
        with self.assertRaisesRegex(ValueError, "clue"):
            self.load()

    def test_reject_duplicate_clue(self):
        self.save()
        self.forged({"clues": ["shift_receipt", "shift_receipt"]})
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.load()

    def test_reject_unstable_clue_order(self):
        self.session.apply_action("ask_nico_about_route")
        self.session.apply_action("inspect_receipt")
        self.save()
        self.forged({"clues": ["route_note", "shift_receipt"]})
        with self.assertRaisesRegex(ValueError, "order"):
            self.load()

    def test_reject_bool_in_integer_fields(self):
        self.save()
        self.forged({"hunger": True})
        with self.assertRaisesRegex(ValueError, "Hunger"):
            self.load()

    def test_reject_unknown_state_field(self):
        self.save()
        self.forged({"admin": "true"})
        with self.assertRaisesRegex(ValueError, "exact"):
            self.load()

    def test_reject_unknown_envelope_field(self):
        self.save()
        envelope = json.loads(self.path.read_text(encoding="utf-8"))
        envelope["do_not_trust"] = True
        self.rewrite(envelope)
        with self.assertRaisesRegex(ValueError, "envelope"):
            self.load()

    def test_reject_repeated_json_object_key(self):
        self.save()
        raw = self.path.read_text(encoding="utf-8")
        self.path.write_text(raw.replace('"schema_version":1', '"schema_version":1,"schema_version":1'))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.load()

    def test_reject_oversize_file(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(b"x" * (MAX_SAVE_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "size"):
            self.load()

    def test_reject_nonfinite_json_number(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_bytes(b'{"state":NaN}')
        with self.assertRaisesRegex(ValueError, "Forbidden"):
            self.load()

    def test_reject_unknown_live_clue_without_writing(self):
        self.session.state.clues.add("unknown")
        with self.assertRaisesRegex(ValueError, "unknown clue"):
            self.save()
        self.assertFalse(self.path.exists())

    def test_failed_atomic_replace_preserves_previous_save(self):
        self.save()
        original = self.path.read_bytes()
        self.session.apply_action("inspect_receipt")
        with patch("glassbend_savegame.os.replace", side_effect=OSError("busy")):
            with self.assertRaises(OSError):
                self.save()
        self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.path.parent.glob(".glassbend-save-*.tmp")), [])

    def test_interactive_save_and_load_resume(self):
        with patch("builtins.input", side_effect=["1","1","1","s","q"]):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(run_interactive(self.path), 0)
        self.assertTrue(self.path.is_file())
        self.assertIn("Local preview saved", out.getvalue())
        with patch("builtins.input", side_effect=["l","q"]):
            with contextlib.redirect_stdout(io.StringIO()) as restored:
                self.assertEqual(run_interactive(self.path), 0)
        self.assertIn("Local preview loaded", restored.getvalue())
        self.assertIn("Clues: shift_receipt", restored.getvalue())

    def test_corrupted_load_preserves_current_session(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("invalid JSON", encoding="utf-8")
        with patch("builtins.input", side_effect=["1","1","1","l","q"]):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(run_interactive(self.path), 0)
        self.assertIn("Load rejected; current game remains unchanged", out.getvalue())
        self.assertIn("Clues: shift_receipt", out.getvalue())

    def test_non_ascii_checksum_is_rejected_without_losing_session(self):
        self.save()
        envelope = json.loads(self.path.read_text(encoding="utf-8"))
        envelope["sha256"] = "é" * 64
        self.rewrite(envelope)
        with patch("builtins.input", side_effect=["1", "1", "1", "l", "q"]):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(run_interactive(self.path), 0)
        self.assertIn("Load rejected; current game remains unchanged", out.getvalue())
        self.assertIn("Clues: shift_receipt", out.getvalue())

    def test_new_run_resets_progress_without_overwriting_save(self):
        with patch("builtins.input", side_effect=["1", "1", "1", "s", "n", "y", "q"]):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(run_interactive(self.path), 0)
        self.assertIn("New investigation started", out.getvalue())
        self.assertIn("Clues: (none)", out.getvalue().split("New investigation started")[-1])
        self.assertEqual(self.load()["clues"], ["shift_receipt"])

    def test_cancel_new_run_preserves_current_progress(self):
        with patch("builtins.input", side_effect=["1", "1", "1", "n", "n", "q"]):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(run_interactive(self.path), 0)
        self.assertIn("New investigation cancelled", out.getvalue())
        self.assertIn("Clues: shift_receipt", out.getvalue().split("New investigation cancelled")[-1])

    def test_new_run_after_ending_unlocks_investigation(self):
        inputs = ["3", "1", "2", "3", "2", "1", "n", "y", "q"]
        with patch("builtins.input", side_effect=inputs), contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(run_interactive(self.path), 0)
        self.assertIn("Phase: Resolved", out.getvalue())
        after_reset = out.getvalue().split("New investigation started", 1)
        self.assertEqual(len(after_reset), 2)
        self.assertIn("Phase: Investigating", after_reset[1])
        self.assertIn("Clues: (none)", after_reset[1])

    def test_default_save_path_is_not_a_repo_file(self):
        path = default_save_path()
        self.assertEqual(path.name, "save_v1.json")
        self.assertEqual(path.parent.name, "GlassbendPreview")
        self.assertEqual(path.parent.parent.name, "ArchCityInDarkness")


if __name__ == "__main__":
    unittest.main()
