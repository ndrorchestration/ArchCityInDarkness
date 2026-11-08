"""Portable M011 source regression checks only; no Unreal compilation/rendering."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_m011_captioned_widget import (
    ACTOR_CPP, BUILD, CONFIG, GRAPH, NATIVE_TEST, PLAYER_CPP, REQUIRED,
    ROOT, WIDGET_CPP, WIDGET_H, validate_m011,
)


class M011CaptionedWidgetContractTests(unittest.TestCase):
    def setUp(self):
        self.source = {p: (ROOT / p).read_text(encoding="utf-8") for p in REQUIRED}

    def errors(self):
        return validate_m011(self.source)

    def mutate(self, path, before, after):
        self.assertIn(before, self.source[path])
        self.source[path] = self.source[path].replace(before, after, 1)

    def test_original_source_graph_widget_contract(self):
        self.assertEqual(self.errors(), [])

    def test_missing_umg_header_rejected(self):
        self.source.pop(WIDGET_H)
        self.assertTrue(self.errors())

    def test_graph_unknown_route_choice_rejected(self):
        data = json.loads(self.source[GRAPH])
        for node in data["nodes"]:
            for choice in node["choices"]:
                if choice.get("action_id") == "commit_dialogue":
                    choice["id"] = "mara_instant_resolution"
        self.source[GRAPH] = json.dumps(data)
        self.assertTrue(self.errors())

    def test_actor_choice_mapping_drift_rejected(self):
        self.mutate(ACTOR_CPP,
                    'CandidateAnchor == TEXT("mara_vale") && ChoiceId == TEXT("mara_resolve")',
                    'CandidateAnchor == TEXT("nico_bell") && ChoiceId == TEXT("mara_resolve")')
        self.assertTrue(self.errors())

    def test_additional_unapproved_action_rejected(self):
        self.mutate(ACTOR_CPP,
                    'return NAME_None;\n}',
                    'return FName(TEXT("unapproved_action"));\n}')
        self.assertTrue(self.errors())

    def test_dispatch_without_session_binding_rejected(self):
        self.mutate(ACTOR_CPP, "Character->IsReviewDialogueActiveFor(this)", "true")
        self.assertTrue(self.errors())

    def test_missing_umg_dependency_rejected(self):
        self.mutate(BUILD, '"UMG"', '"OtherModule"')
        self.assertTrue(self.errors())

    def test_missing_g_key_rejected(self):
        self.mutate(CONFIG,
                    '+ActionMappings=(ActionName="ReviewGraphOpen",Key=G)',
                    '+ActionMappings=(ActionName="ReviewGraphOpen",Key=H)')
        self.assertTrue(self.errors())

    def test_missing_widget_open_gate_rejected(self):
        self.mutate(WIDGET_CPP,
                    "Character->IsReviewDialogueActiveFor(Marker)",
                    "true")
        self.assertTrue(self.errors())

    def test_graph_missing_project_status_rejected(self):
        self.mutate(WIDGET_CPP, 'TEXT("PROTOTYPE_NOT_CANON")',
                    'TEXT("APPROVED_CANON")')
        self.assertTrue(self.errors())

    def test_caption_line_missing_rejected(self):
        self.mutate(WIDGET_CPP, 'TEXT("line")',
                    'TEXT("not_a_real_line")')
        self.assertTrue(self.errors())

    def test_button_choice_binding_removed_rejected(self):
        self.mutate(WIDGET_CPP, "Button->BindReviewChoice(this, FName(*Id))",
                    "Button->BindReviewChoice(this, NAME_None)")
        self.assertTrue(self.errors())

    def test_current_node_validation_removed_rejected(self):
        self.mutate(WIDGET_CPP, "FindSourceNode(CurrentNodeId)",
                    "FindSourceNode(TEXT(\"mara_start\"))")
        self.assertTrue(self.errors())

    def test_arbitrary_action_dispatch_rejected(self):
        self.mutate(WIDGET_CPP, "Expected != FName(*ActionId)",
                    "false")
        self.assertTrue(self.errors())

    def test_actor_execution_bypassed_rejected(self):
        self.mutate(WIDGET_CPP, "Marker->TryApplyReviewDialogueChoice(Character, ChoiceId)",
                    "true")
        self.assertTrue(self.errors())

    def test_input_focus_wiring_missing_rejected(self):
        self.mutate(PLAYER_CPP, "FInputModeUIOnly", "FInputModeGameOnly")
        self.assertTrue(self.errors())

    def test_escape_close_missing_rejected(self):
        self.mutate(WIDGET_CPP, "InKeyEvent.GetKey() == EKeys::Escape",
                    "false")
        self.assertTrue(self.errors())

    def test_teardown_restores_game_input_rejected(self):
        self.mutate(WIDGET_CPP, "Character->EndGraphDialogue(this)",
                    "true")
        self.assertTrue(self.errors())

    def test_first_response_keyboard_focus_required(self):
        self.mutate(WIDGET_CPP, "FirstChoiceButton->SetKeyboardFocus()",
                    "FirstChoiceButton->SetToolTipText(FText::GetEmpty())")
        self.assertTrue(self.errors())

    def test_scrollable_response_list_required(self):
        self.mutate(WIDGET_CPP, "ChoiceScroll->AddChild(ChoiceList)",
                    "Column->AddChildToVerticalBox(ChoiceList)")
        self.assertTrue(self.errors())

    def test_keyboard_focus_must_leave_parent_panel(self):
        self.mutate(PLAYER_CPP, "Widget->FocusCurrentChoice()",
                    "Widget->SetKeyboardFocus()")
        self.assertTrue(self.errors())

    def test_dialogue_frame_padding_required(self):
        self.mutate(WIDGET_CPP, "Frame->SetPadding(", "Frame->SetUnrelatedPadding(")
        self.assertTrue(self.errors())

    def test_native_source_choice_assertions_required(self):
        self.mutate(NATIVE_TEST,
                    'TEXT("nico_bell"), TEXT("nico_ask")',
                    'TEXT("nico_bell"), TEXT("irrelevant")')
        self.assertTrue(self.errors())


if __name__ == "__main__":
    unittest.main()
