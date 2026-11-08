"""Synthetic tests for M008 static wiring; do not claim native PIE success."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_m008_source_readiness import (
    INPUT, MAP, MARKERS, MODE, PAWN, ROOT, check_sources,
)


class M008SourceReadinessTests(unittest.TestCase):
    def setUp(self):
        self.contents = {
            path: (ROOT / path).read_text(encoding="utf-8")
            for path in (INPUT, PAWN, MARKERS, MODE)
        }

    def check(self, map_present=True):
        return check_sources(self.contents, map_present)

    def test_review_source_wiring_is_present(self):
        self.assertTrue((ROOT / MAP).is_file())
        self.assertEqual(self.check(), [])

    def test_missing_map_fails_closed(self):
        self.assertTrue(self.check(map_present=False))

    def test_missing_input_key_fails_closed(self):
        self.contents[INPUT] = self.contents[INPUT].replace('Key=E)', 'Key=F)', 1)
        self.assertTrue(self.check())

    def test_missing_pawn_dispatch_fails_closed(self):
        self.contents[PAWN] = self.contents[PAWN].replace(
            "Nearest->TryInteract(this)", "false", 1
        )
        self.assertTrue(self.check())

    def test_missing_receipt_anchor_fails_closed(self):
        self.contents[MARKERS] = self.contents[MARKERS].replace(
            'Candidate == TEXT("shift_receipt")', 'Candidate == TEXT("other_receipt")', 1
        )
        self.assertTrue(self.check())

    def test_missing_visibility_gate_fails_closed(self):
        self.contents[MARKERS] = self.contents[MARKERS].replace(
            "LineTraceSingleByChannel(Hit, Eyes, Target, ECC_Visibility",
            "LineTraceSingleByChannel(Hit, Eyes, Target, ECC_Camera", 1
        )
        self.assertTrue(self.check())

    def test_missing_player_authorization_fails_closed(self):
        self.contents[MARKERS] = self.contents[MARKERS].replace(
            "Character->IsPlayerControlled()", "true", 1
        )
        self.assertTrue(self.check())

    def test_range_drift_fails_closed(self):
        self.contents[MARKERS] = self.contents[MARKERS].replace(
            "MaxDistanceCm = 275.0f", "MaxDistanceCm = 1500.0f", 1
        )
        self.assertTrue(self.check())

    def test_missing_review_pawn_fails_closed(self):
        self.contents[MODE] = self.contents[MODE].replace(
            "DefaultPawnClass = AACIDPreludeCharacter::StaticClass()",
            "DefaultPawnClass = nullptr", 1
        )
        self.assertTrue(self.check())

    def test_missing_source_fails_closed(self):
        self.contents.pop(PAWN)
        self.assertTrue(self.check())


if __name__ == "__main__":
    unittest.main()
