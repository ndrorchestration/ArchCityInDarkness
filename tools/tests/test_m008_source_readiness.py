"""Synthetic M008 source drift tests only. Not native Unreal/PIE evidence."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_m008_source_readiness import (
    INPUT, MAP, MARKERS, MODE, PAWN, BRIDGE, LEDGER, ROOT, SOURCE_PATHS,
    check_sources,
)


class M008SourceReadinessTests(unittest.TestCase):
    def setUp(self):
        self.contents = {
            path: (ROOT / path).read_text(encoding="utf-8")
            for path in SOURCE_PATHS
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

    def test_duplicate_input_mapping_fails_closed(self):
        self.contents[INPUT] += '\n+ActionMappings=(ActionName="Interact",Key=E)\n'
        self.assertTrue(self.check())

    def test_missing_pawn_dispatch_fails_closed(self):
        self.contents[PAWN] = self.contents[PAWN].replace(
            "Nearest->TryInteract(this)", "false", 1
        )
        self.assertTrue(self.check())

    def test_duplicate_pawn_binding_fails_closed(self):
        anchor = 'BindAction(TEXT("Interact")'
        self.contents[PAWN] += f"\n// {anchor}\n"
        self.assertTrue(self.check())

    def test_missing_receipt_anchor_fails_closed(self):
        self.contents[MARKERS] = self.contents[MARKERS].replace(
            'Candidate == TEXT("shift_receipt")',
            'Candidate == TEXT("other_receipt")', 1
        )
        self.assertTrue(self.check())

    def test_wrong_receipt_selection_fails_closed(self):
        self.contents[MARKERS] = self.contents[MARKERS].replace(
            'FName(TEXT("inspect_receipt"))',
            'FName(TEXT("inspect_annex_badge"))', 1
        )
        self.assertTrue(self.check())

    def test_wrong_action_bridge_fails_closed(self):
        self.contents[BRIDGE] = self.contents[BRIDGE].replace(
            'return QuestLedger->DiscoverClue(FName(TEXT("shift_receipt")));',
            'return QuestLedger->DiscoverClue(FName(TEXT("annex_badge")));', 1
        )
        self.assertTrue(self.check())

    def test_missing_ledger_duplicate_guard_fails_closed(self):
        self.contents[LEDGER] = self.contents[LEDGER].replace(
            'DiscoveredClues.Contains(ClueId)', 'false'
        )
        self.assertTrue(self.check())

    def test_missing_quest_dispatch_fails_closed(self):
        self.contents[MARKERS] = self.contents[MARKERS].replace(
            "UACIDQuestInteractionBridge::TryApplyAction(Character->GetQuestLedger(), Action)",
            "true", 1
        )
        self.assertTrue(self.check())

    def test_direct_hunger_mutation_fails_closed(self):
        self.contents[MARKERS] += "\n// test injection: Hunger->Feed(2);\n"
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
