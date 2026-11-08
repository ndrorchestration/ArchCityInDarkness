"""Synthetic M010 source-guard regression tests. NOT native Unreal gameplay."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_m010_explicit_review_input import (
    ACTOR, CONFIG, GRAPH, HEADER, NATIVE_TEST, PLAYER, REQUIRED, ROOT,
    validate_m010,
)


class M010ExplicitInputSourceTests(unittest.TestCase):
    def setUp(self):
        self.source = {p: (ROOT / p).read_text(encoding="utf-8") for p in REQUIRED}

    def errors(self):
        return validate_m010(self.source)

    def mutate(self, path, old, new):
        self.assertIn(old, self.source[path], "Test fixture unexpectedly changed")
        self.source[path] = self.source[path].replace(old, new, 1)

    def mutate_in_fn(self, path, signature, old, new):
        original = self.source[path]
        start = original.index(signature)
        end = original.find("\n}\n", start)
        self.assertNotEqual(end, -1)
        body = original[start:end]
        self.assertIn(old, body, "Expected dispatch gate source missing")
        self.source[path] = original[:start] + body.replace(old, new, 1) + original[end:]

    def test_review_diagnostic_input_wiring(self):
        self.assertEqual([], self.errors())

    def test_missing_input_fails(self):
        self.source.pop(CONFIG)
        self.assertTrue(self.errors())

    def test_wrong_open_key_fails(self):
        self.mutate(CONFIG, 'Key=F)', 'Key=G)')
        self.assertTrue(self.errors())

    def test_duplicate_confirm_binding_fails(self):
        self.source[CONFIG] += '+ActionMappings=(ActionName="ReviewDialogueConfirm",Key=Enter)\n'
        self.assertTrue(self.errors())

    def test_confirmation_binding_missing_fails(self):
        self.mutate(PLAYER, 'BindAction(TEXT("ReviewDialogueConfirm")',
                    'BindAction(TEXT("WrongConfirm")')
        self.assertTrue(self.errors())

    def test_open_without_visibility_check_fails(self):
        self.mutate(PLAYER, "Nearest->CanReviewInteract(this)", "true")
        self.assertTrue(self.errors())

    def test_open_without_quest_phase_fails(self):
        self.mutate(PLAYER, "QuestLedger->GetPhase() != EACIDQuestPhase::Investigating", "false")
        self.assertTrue(self.errors())

    def test_wrong_pending_marker_ownership_fails(self):
        self.mutate(PLAYER, "ActiveReviewDialogueMarker.Get() == Marker", "true")
        self.assertTrue(self.errors())

    def test_confirm_without_single_use_reset_fails(self):
        start = self.source[PLAYER].index("void AACIDPreludeCharacter::ConfirmReviewDialogue()")
        end = self.source[PLAYER].index("void AACIDPreludeCharacter::CancelReviewDialogue()", start)
        part = self.source[PLAYER][start:end].replace("ActiveReviewDialogueMarker.Reset();", "")
        self.source[PLAYER] = self.source[PLAYER][:start] + part + self.source[PLAYER][end:]
        self.assertTrue(self.errors())

    def test_cancel_without_clear_fails(self):
        start = self.source[PLAYER].index("void AACIDPreludeCharacter::CancelReviewDialogue()")
        end = self.source[PLAYER].index("void AACIDPreludeCharacter::ShowStatus()", start)
        part = self.source[PLAYER][start:end].replace("ActiveReviewDialogueMarker.Reset();", "")
        self.source[PLAYER] = self.source[PLAYER][:start] + part + self.source[PLAYER][end:]
        self.assertTrue(self.errors())

    def test_world_e_not_canceling_fails(self):
        start = self.source[PLAYER].index("void AACIDPreludeCharacter::Interact()")
        end = self.source[PLAYER].index("bool AACIDPreludeCharacter::IsReviewDialogueActiveFor(", start)
        part = self.source[PLAYER][start:end].replace("ActiveReviewDialogueMarker.Reset();", "")
        self.source[PLAYER] = self.source[PLAYER][:start] + part + self.source[PLAYER][end:]
        self.assertTrue(self.errors())

    def test_dispatch_different_actor_fails(self):
        self.mutate(ACTOR, "Character->IsReviewDialogueActiveFor(this)", "true")
        self.assertTrue(self.errors())

    def test_dispatch_no_range_check_fails(self):
        self.mutate_in_fn(ACTOR, "bool AACIDPreludeInteractable::CanReviewInteract(",
                          "MaxDistanceCm = 275.0f", "MaxDistanceCm = 750.0f")
        self.assertTrue(self.errors())

    def test_dispatch_no_visibility_check_fails(self):
        self.mutate_in_fn(ACTOR, "bool AACIDPreludeInteractable::CanReviewInteract(",
                          "Target, ECC_Visibility, Params",
                          "Target, ECC_Camera, Params")
        self.assertTrue(self.errors())

    def test_wrong_route_choice_fails(self):
        self.mutate(ACTOR,
                    'CandidateAnchor == TEXT("mara_vale") && CandidateChoice == TEXT("mara_resolve")',
                    'CandidateAnchor == TEXT("mara_vale") && CandidateChoice == TEXT("nico_resolve")')
        self.assertTrue(self.errors())

    def test_unknown_choice_allowlist_expansion_fails(self):
        self.mutate(ACTOR, "return NAME_None;\n}", 'return FName(TEXT("unexpected"));\n}')
        self.assertTrue(self.errors())

    def test_graph_route_choice_drift_fails(self):
        graph = json.loads(self.source[GRAPH])
        for n in graph["nodes"]:
            for c in n["choices"]:
                if c.get("id") == "mara_resolve":
                    c["id"] = "mara_auto_commit"
        self.source[GRAPH] = json.dumps(graph)
        self.assertTrue(self.errors())

    def test_native_candidate_tests_required(self):
        # M011 appends another native assertion for the same choice ID; remove
        # every copy to prove the M010 requirement cannot be accidentally
        # satisfied by a newer duplicate source assertion.
        before = 'TEXT("etta_quill"), TEXT("etta_resolve")'
        self.assertIn(before, self.source[NATIVE_TEST])
        self.source[NATIVE_TEST] = self.source[NATIVE_TEST].replace(
            before, 'TEXT("etta_quill"), TEXT("unrelated_resolve")')
        self.assertTrue(self.errors())

    def test_review_session_must_be_weak(self):
        self.mutate(HEADER, "TWeakObjectPtr<AACIDPreludeInteractable>",
                    "TObjectPtr<AACIDPreludeInteractable>")
        self.assertTrue(self.errors())

    def test_no_unvalidated_raw_action_dispatch(self):
        self.mutate(ACTOR, "ReviewChoiceActionForAnchor(AnchorId, ChoiceId)",
                    "ChoiceId")
        self.assertTrue(self.errors())


if __name__ == "__main__":
    unittest.main()
