#!/usr/bin/env python3
"""M010 source-only checks for guarded explicit diagnostic NPC input.

Never establishes C++ compilation, native UE automation, player-controlled PIE,
dialogue-widget accessibility, GPU visuals or verified gameplay outcomes.
"""
from pathlib import Path
import json
import re
from check_m009_dialogue_world_contract import (
    validate_world_dialogue, REQUIRED as M009_REQUIRED
)

ROOT = Path(__file__).resolve().parents[1]
HEADER = "Source/ArchCityInDarkness/Public/ACIDPreludeCharacter.h"
ACTOR_HEADER = "Source/ArchCityInDarkness/Public/ACIDPreludeInteractable.h"
PLAYER = "Source/ArchCityInDarkness/Private/ACIDPreludeCharacter.cpp"
ACTOR = "Source/ArchCityInDarkness/Private/ACIDPreludeInteractable.cpp"
CONFIG = "Config/DefaultInput.ini"
GRAPH = "Prototypes/Glassbend/dialogue_v1.json"
NATIVE_TEST = "Source/ArchCityInDarkness/Private/Tests/ACIDPreludeContractTests.cpp"
REQUIRED = tuple(dict.fromkeys((*M009_REQUIRED, HEADER, ACTOR_HEADER, NATIVE_TEST)))
CONFIRM_ACTIONS = {
    "mara_vale": ("mara_resolve", "commit_dialogue"),
    "nico_bell": ("nico_resolve", "commit_stealth"),
    "etta_quill": ("etta_resolve", "commit_confrontation"),
}
KEYS = {
    "ReviewDialogueOpen": "F",
    "ReviewDialogueConfirm": "Enter",
    "ReviewDialogueCancel": "Escape",
}


def body(text: str, signature: str) -> str:
    """Locate source function through next top-level definition, not C++ parse."""
    start = text.find(signature)
    if start == -1:
        return ""
    opening = text.find("{", start)
    if opening < 0:
        return ""
    depth = 0
    for i in range(opening, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[opening:i + 1]
    return ""


def validate_m010(source: dict[str, str]) -> list[str]:
    missing = [p for p in REQUIRED if p not in source]
    if missing:
        return [f"Required source missing: {p}" for p in missing]
    problems = validate_world_dialogue(source)
    actor, player = source[ACTOR], source[PLAYER]
    config, h, ah, native = source[CONFIG], source[HEADER], source[ACTOR_HEADER], source[NATIVE_TEST]
    graph = json.loads(source[GRAPH])

    for action, key in KEYS.items():
        line = f'+ActionMappings=(ActionName="{action}",Key={key})'
        if config.count(line) != 1:
            problems.append(f"Missing/duplicate review key: {line}")
    for method, action in (
        ("OpenReviewDialogue", "ReviewDialogueOpen"),
        ("ConfirmReviewDialogue", "ReviewDialogueConfirm"),
        ("CancelReviewDialogue", "ReviewDialogueCancel"),
    ):
        expected = f'BindAction(TEXT("{action}"), IE_Pressed, this, &AACIDPreludeCharacter::{method})'
        if player.count(expected) != 1 or f"void {method}();" not in h:
            problems.append(f"Missing/duplicate player binding: {action}")

    open_fn = body(player, "void AACIDPreludeCharacter::OpenReviewDialogue()")
    confirm_fn = body(player, "void AACIDPreludeCharacter::ConfirmReviewDialogue()")
    cancel_fn = body(player, "void AACIDPreludeCharacter::CancelReviewDialogue()")
    session_fn = body(player, "bool AACIDPreludeCharacter::IsReviewDialogueActiveFor(")
    world_e_fn = body(player, "void AACIDPreludeCharacter::Interact()")
    # Source checks only: insist on meaningful operations on open/confirm/cancel.
    for snippet in (
        "ActiveReviewDialogueMarker.Reset()",
        "IsLocallyControlled()",
        "QuestLedger->GetPhase() != EACIDQuestPhase::Investigating",
        "Nearest->IsReviewDialogueNPC()",
        "Nearest->CanReviewInteract(this)",
        "ActiveReviewDialogueMarker = Nearest",
    ):
        if snippet not in open_fn and snippet != "Nearest->IsReviewDialogueNPC()":
            problems.append("Dialogue opening gate missing: " + snippet)
    if "It->IsReviewDialogueNPC()" not in open_fn:
        problems.append("Only known NPCs can open a dialogue")
    if not session_fn or "ActiveReviewDialogueMarker.Get() == Marker" not in session_fn:
        problems.append("Session binding to exact actor missing")
    for snippet in (
        "ActiveReviewDialogueMarker.Get()",
        "IsLocallyControlled()",
        "Marker->TryCommitReviewChoice(this, Marker->GetReviewChoiceId())",
        "ActiveReviewDialogueMarker.Reset()",
    ):
        if snippet not in confirm_fn:
            problems.append("Confirmation gate missing: " + snippet)
    if "ActiveReviewDialogueMarker.Reset()" not in cancel_fn:
        problems.append("Cancellation must clear pending dialogue")
    if "ActiveReviewDialogueMarker.Reset()" not in world_e_fn:
        problems.append("Other world E interactions must clear pending dialogue")
    if "TWeakObjectPtr<AACIDPreludeInteractable>" not in h:
        problems.append("Dialogue session must be weak/revocable")
    if "TryCommitReviewChoice(" not in ah or "CanReviewInteract(" not in ah:
        problems.append("World interaction gate/choice interface missing")

    candidate = body(actor, "bool AACIDPreludeInteractable::TryCommitReviewChoice(")
    gate = body(actor, "bool AACIDPreludeInteractable::CanReviewInteract(")
    action_fn = body(actor, "FName AACIDPreludeInteractable::ReviewChoiceActionForAnchor(")
    choice_fn = body(actor, "FName AACIDPreludeInteractable::GetReviewChoiceId()")
    for snippet in (
        "IsReviewDialogueNPC()",
        "CanReviewInteract(Character)",
        "Character->IsReviewDialogueActiveFor(this)",
        "Ledger->GetPhase() != EACIDQuestPhase::Investigating",
        "ReviewChoiceActionForAnchor(AnchorId, ChoiceId)",
        "UACIDQuestInteractionBridge::TryApplyAction(Ledger, Action)",
    ):
        if snippet not in candidate:
            problems.append("Commit-time gate missing: " + snippet)
    for snippet in (
        "Character->IsPlayerControlled()",
        "Character->GetWorld() != GetWorld()",
        "GetWorld()->GetNetMode() != NM_Standalone",
        "MaxDistanceCm = 275.0f",
        "FVector::DistSquared2D(",
        "FMath::Abs(",
        "LineTraceSingleByChannel(",
        "ECC_Visibility",
        "Params.AddIgnoredActor(Character)",
    ):
        if snippet not in gate:
            problems.append("Missing dispatch-time world revalidation: " + snippet)

    # Enforce each original M005 choice -> intended NPC/route.
    graph_actions = {}
    for node in graph["nodes"]:
        for choice in node["choices"]:
            if choice.get("action_id") in {a for _, a in CONFIRM_ACTIONS.values()}:
                graph_actions[(node["anchor_id"], choice["id"])] = choice["action_id"]
    if graph_actions != {(anchor, choice): action for anchor, (choice, action) in CONFIRM_ACTIONS.items()}:
        problems.append("Review route choice IDs no longer match original M005 graph")
    if action_fn.count("return FName(TEXT(") != 3 or "return NAME_None;" not in action_fn:
        problems.append("Review choice dispatch must be 3 exact cases plus default deny")
    for anchor, (choice, action) in CONFIRM_ACTIONS.items():
        expr = f'CandidateAnchor == TEXT("{anchor}") && CandidateChoice == TEXT("{choice}")'
        if expr not in action_fn or f'FName(TEXT("{action}"))' not in action_fn:
            problems.append("Missing fixed NPC/choice/action: " + anchor)
        if f'AnchorId == TEXT("{anchor}")' not in choice_fn or f'FName(TEXT("{choice}"))' not in choice_fn:
            problems.append("Review prompt choice drift: " + anchor)
        if f'TEXT("{anchor}"), TEXT("{choice}")' not in native:
            problems.append("Native candidate test missing: " + anchor)
    if "return NAME_None;" not in choice_fn or "return NAME_None;" not in action_fn:
        problems.append("Unknown review choices must fail closed")
    return problems


def main() -> int:
    source = {
        p: (ROOT / p).read_text(encoding="utf-8")
        for p in REQUIRED if (ROOT / p).is_file()
    }
    problems = validate_m010(source)
    for p in problems:
        print("M010 SOURCE FAIL:", p)
    if problems:
        return 1
    print("M010 SOURCE PASS: F/Enter/Escape session, three exact route choices and rechecked world gate")
    print("UNVERIFIED: native UE C++ build, native tests, actual input/PIE, HUD, route outcomes or art")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
