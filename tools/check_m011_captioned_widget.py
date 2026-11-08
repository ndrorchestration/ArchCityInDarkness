#!/usr/bin/env python3
"""M011 source integrity guard for the provisional captioned Unreal UMG UI.

Never compiles C++, executes UMG, verifies input focus, captures GPU frames,
or establishes playable/canon-approved dialogue. Fail-closed source checks only.
"""
import json
import re
from pathlib import Path
from check_m010_explicit_review_input import (
    validate_m010, REQUIRED as M010_REQUIRED
)

ROOT = Path(__file__).resolve().parents[1]
GRAPH = "Prototypes/Glassbend/dialogue_v1.json"
ACTOR_CPP = "Source/ArchCityInDarkness/Private/ACIDPreludeInteractable.cpp"
ACTOR_H = "Source/ArchCityInDarkness/Public/ACIDPreludeInteractable.h"
PLAYER_CPP = "Source/ArchCityInDarkness/Private/ACIDPreludeCharacter.cpp"
PLAYER_H = "Source/ArchCityInDarkness/Public/ACIDPreludeCharacter.h"
WIDGET_H = "Source/ArchCityInDarkness/Public/ACIDReviewDialogueWidget.h"
WIDGET_CPP = "Source/ArchCityInDarkness/Private/ACIDReviewDialogueWidget.cpp"
BUILD = "Source/ArchCityInDarkness/ArchCityInDarkness.Build.cs"
CONFIG = "Config/DefaultInput.ini"
NATIVE_TEST = "Source/ArchCityInDarkness/Private/Tests/ACIDPreludeContractTests.cpp"
REQUIRED = tuple(dict.fromkeys((*M010_REQUIRED, WIDGET_H, WIDGET_CPP, BUILD)))
EXPECTED_CHOICES = {
    ("shift_receipt", "receipt_inspect"): "inspect_receipt",
    ("annex_badge", "badge_inspect"): "inspect_annex_badge",
    ("mara_vale", "mara_ask"): "ask_mara_about_ledger",
    ("mara_vale", "mara_resolve"): "commit_dialogue",
    ("nico_bell", "nico_ask"): "ask_nico_about_route",
    ("nico_bell", "nico_resolve"): "commit_stealth",
    ("etta_quill", "etta_resolve"): "commit_confrontation",
}


def section(source: str, signature: str) -> str:
    start = source.find(signature)
    if start < 0:
        return ""
    opening = source.find("{", start)
    if opening < 0:
        return ""
    depth = 0
    for i in range(opening, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[opening:i + 1]
    return ""


def validate_m011(source: dict[str, str]) -> list[str]:
    missing = [p for p in REQUIRED if p not in source]
    if missing:
        return [f"M011 missing required source: {p}" for p in missing]
    issues = validate_m010(source)
    actor = source[ACTOR_CPP]
    wcpp, wh = source[WIDGET_CPP], source[WIDGET_H]
    player, ph, build, ini, native = (
        source[PLAYER_CPP], source[PLAYER_H], source[BUILD], source[CONFIG],
        source[NATIVE_TEST]
    )
    graph = json.loads(source[GRAPH])
    graph_pairs = {(node["anchor_id"], choice["id"]): choice["action_id"]
                   for node in graph["nodes"] for choice in node["choices"]
                   if choice.get("action_id") is not None}
    if graph_pairs != EXPECTED_CHOICES:
        issues.append("Graph actions differ from original M005 seven explicit choice bindings")

    mapping = section(actor, "FName AACIDPreludeInteractable::ActionForDialogueChoice(")
    if not mapping or mapping.count("return FName(TEXT(") != 7 or "return NAME_None;" not in mapping:
        issues.append("Actor fixed source graph action allowlist missing or widened")
    for (anchor, choice), action in EXPECTED_CHOICES.items():
        matched = re.search(
            r'CandidateAnchor == TEXT\("' + re.escape(anchor) +
            r'"\)\s*&&\s*ChoiceId == TEXT\("' + re.escape(choice) +
            r'"\)\s*\)\s*return FName\(TEXT\("' + re.escape(action) + r'"\)\)',
            mapping,
        )
        if not matched:
            issues.append(f"Missing exact actor/choice action binding: {anchor}/{choice}")
        if f'TEXT("{anchor}"), TEXT("{choice}")' not in native:
            issues.append(f"Unreal test source missing graph choice: {anchor}/{choice}")

    dispatch = section(actor, "bool AACIDPreludeInteractable::TryApplyReviewDialogueChoice(")
    for required in (
        "CanReviewInteract(Character)",
        "Character->IsReviewDialogueActiveFor(this)",
        "Ledger->GetPhase() != EACIDQuestPhase::Investigating",
        "ActionForDialogueChoice(AnchorId, ChoiceId)",
        "UACIDQuestInteractionBridge::TryApplyAction(Ledger, Action)",
    ):
        if required not in dispatch:
            issues.append("World choice dispatch gate missing: " + required)

    for module in ('"UMG"', '"Slate"', '"SlateCore"', '"Json"'):
        if module not in build:
            issues.append("Missing native Unreal module dependency: " + module)
    if ini.count('+ActionMappings=(ActionName="ReviewGraphOpen",Key=G)') != 1:
        issues.append("G captioned dialogue mapping missing or duplicated")
    if player.count('BindAction(TEXT("ReviewGraphOpen"), IE_Pressed, this, &AACIDPreludeCharacter::OpenGraphDialogue)') != 1:
        issues.append("Player G captioned dialogue input not bound")
    if "TObjectPtr<UACIDReviewDialogueWidget> ActiveGraphWidget" not in ph or "void EndGraphDialogue(" not in ph:
        issues.append("Player must own and close widget session")

    opening = section(player, "void AACIDPreludeCharacter::OpenGraphDialogue()")
    for required in (
        "ActiveReviewDialogueMarker = Nearest",
        "Nearest->CanReviewInteract(this)",
        "CreateWidget<UACIDReviewDialogueWidget>",
        "Widget->OpenFor(this, Nearest)",
        "FInputModeUIOnly",
        "PC->SetInputMode(UIInput)",
    ):
        if required not in opening:
            issues.append("UI opening wiring missing: " + required)

    if "class ARCHCITYINDARKNESS_API UACIDReviewDialogueWidget : public UUserWidget" not in wh:
        issues.append("UMG user widget class missing")
    if "void FocusCurrentChoice();" not in wh or "FirstChoiceButton" not in wh:
        issues.append("Accessible first response focus contract missing")
    if "Widget->FocusCurrentChoice()" not in opening:
        issues.append("Player input mode must focus first source response")
    if "UScrollBox" not in wcpp or "ChoiceScroll->AddChild(ChoiceList)" not in wcpp:
        issues.append("Long response lists must be scrollable")
    if "Frame->SetPadding(" not in wcpp:
        issues.append("Caption review frame must have interior padding")
    focus = section(wcpp, "void UACIDReviewDialogueWidget::FocusCurrentChoice()")
    if "FirstChoiceButton->SetKeyboardFocus()" not in focus:
        issues.append("FocusCurrentChoice must focus a visible actual choice button")
    if "class ARCHCITYINDARKNESS_API UACIDReviewDialogueChoiceButton : public UButton" not in wh:
        issues.append("Per-choice clickable button class missing")

    loader = section(wcpp, "bool UACIDReviewDialogueWidget::LoadLocalReviewGraph()")
    for required in (
        'TEXT("Prototypes")', 'TEXT("dialogue_v1.json")',
        'TEXT("status")', 'TEXT("PROTOTYPE_NOT_CANON")',
        'TEXT("quest_id")', 'TEXT("the_unclaimed_hour")',
        'TEXT("layout_id")', 'TEXT("glassbend_greybox_v1")',
        "FJsonSerializer::Deserialize",
        "return false",
    ):
        if required not in loader:
            issues.append("Review JSON loader fail-closed contract missing: " + required)
    open_widget = section(wcpp, "bool UACIDReviewDialogueWidget::OpenFor(")
    for required in (
        "Character->IsReviewDialogueActiveFor(Marker)",
        "Marker->CanReviewInteract(Character)",
        "LoadLocalReviewGraph()",
        'TEXT("entrypoints")',
        "ShowSourceNode(EntryNode)",
    ):
        if required not in open_widget:
            issues.append("Widget opening source guard missing: " + required)

    render = section(wcpp, "bool UACIDReviewDialogueWidget::ShowSourceNode(")
    for required in (
        "FindSourceNode(NodeId)", 'TEXT("anchor_id")',
        "Marker->AnchorId.ToString()",
        'TEXT("line")', 'TEXT("choices")',
        'TEXT("player_text")',
        "Button->BindReviewChoice(this, FName(*Id))",
    ):
        if required not in render:
            issues.append("Caption/choice render contract missing: " + required)
    selection = section(wcpp, "void UACIDReviewDialogueWidget::SelectSourceChoice(")
    for required in (
        "FindSourceNode(CurrentNodeId)",
        "Character->IsReviewDialogueActiveFor(Marker)",
        'TEXT("id")',
        'TEXT("action_id")',
        "ActionForDialogueChoice(",
        "Expected != FName(*ActionId)",
        "Marker->TryApplyReviewDialogueChoice(Character, ChoiceId)",
        'TEXT("on_success")', 'TEXT("on_failure")',
        "CloseReviewDialogue();",
    ):
        if required not in selection:
            issues.append("Active-node explicit choice selection gate missing: " + required)
    close = section(wcpp, "void UACIDReviewDialogueWidget::CloseReviewDialogue()")
    for required in (
        "FInputModeGameOnly", "Character->EndGraphDialogue(this)", "RemoveFromParent()",
    ):
        if required not in close:
            issues.append("Widget teardown/restore input missing: " + required)
    key = section(wcpp, "FReply UACIDReviewDialogueWidget::NativeOnKeyDown(")
    if "EKeys::Escape" not in key or "CloseReviewDialogue()" not in key:
        issues.append("Escape-to-close binding missing")
    return issues


def main() -> int:
    src = {p: (ROOT / p).read_text(encoding="utf-8")
           for p in REQUIRED if (ROOT / p).is_file()}
    errors = validate_m011(src)
    if errors:
        for item in errors:
            print("M011 SOURCE FAIL:", item)
        return 1
    print("M011 SOURCE PASS: graph 19-node caption UI source and seven gated action bindings")
    print("NO NATIVE EVIDENCE: C++ compile, UMG input/focus, PIE choice flow, GPU screenshots, art")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
