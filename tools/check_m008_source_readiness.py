#!/usr/bin/env python3
"""Fail-closed portable source signatures for M008; never Unreal/PIE proof."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MAP = "Content/ArchCity/Review/Glassbend_Prelude_Greybox.umap"
INPUT = "Config/DefaultInput.ini"
PAWN = "Source/ArchCityInDarkness/Private/ACIDPreludeCharacter.cpp"
MARKERS = "Source/ArchCityInDarkness/Private/ACIDPreludeInteractable.cpp"
MODE = "Source/ArchCityInDarkness/Private/ACIDPreludeGameMode.cpp"
BRIDGE = "Source/ArchCityInDarkness/Private/ACIDQuestInteractionBridge.cpp"
LEDGER = "Source/ArchCityInDarkness/Private/ACIDQuestLedgerComponent.cpp"
SOURCE_PATHS = (INPUT, PAWN, MARKERS, MODE, BRIDGE, LEDGER)

ANCHORS = ("shift_receipt", "mara_vale", "nico_bell", "annex_badge", "etta_quill")
INPUT_MAPPINGS = (
    '+ActionMappings=(ActionName="Interact",Key=E)',
    '+ActionMappings=(ActionName="QuestStatus",Key=Tab)',
    '+AxisMappings=(AxisName="MoveForward",Key=W,Scale=1.000000)',
    '+AxisMappings=(AxisName="MoveForward",Key=S,Scale=-1.000000)',
    '+AxisMappings=(AxisName="MoveRight",Key=A,Scale=-1.000000)',
    '+AxisMappings=(AxisName="MoveRight",Key=D,Scale=1.000000)',
    '+AxisMappings=(AxisName="Turn",Key=MouseX,Scale=1.000000)',
    '+AxisMappings=(AxisName="LookUp",Key=MouseY,Scale=-1.000000)',
)
PAWN_BINDINGS = (
    'BindAxis(TEXT("MoveForward")',
    'BindAxis(TEXT("MoveRight")',
    'BindAxis(TEXT("Turn")',
    'BindAxis(TEXT("LookUp")',
    'BindAction(TEXT("Interact")',
    'BindAction(TEXT("QuestStatus")',
)
GATES = (
    "Character->IsPlayerControlled()",
    "Character->GetWorld() != GetWorld()",
    "GetWorld()->GetNetMode() != NM_Standalone",
    "FVector::DistSquared2D(",
    "FMath::Square(MaxDistanceCm)",
    "LineTraceSingleByChannel(Hit, Eyes, Target, ECC_Visibility",
    'FName(TEXT("inspect_receipt"))',
)
RECEIPT_SELECTION = (
    r'if\s*\(AnchorId\s*==\s*TEXT\("shift_receipt"\)\)\s*'
    r'return\s+Ledger->HasClue\(TEXT\("shift_receipt"\)\)\s*'
    r'\?\s*NAME_None\s*:\s*FName\(TEXT\("inspect_receipt"\)\)\s*;'
)
RECEIPT_BRIDGE = (
    r'if\s*\(ActionId\s*==\s*FName\(TEXT\("inspect_receipt"\)\)\)\s*'
    r'\{\s*return\s+QuestLedger->DiscoverClue\('
    r'FName\(TEXT\("shift_receipt"\)\)\)\s*;\s*\}'
)


def check_sources(source: dict[str, str], map_present: bool) -> list[str]:
    """Detect specific source drift. Strings cannot prove runtime behavior."""
    missing = [path for path in SOURCE_PATHS if path not in source]
    if missing:
        return [f"Missing source: {path}" for path in missing]
    problems = []
    if not map_present:
        problems.append(f"Missing noncanonical review map: {MAP}")
    config, pawn, marker, mode, bridge, ledger = (source[p] for p in SOURCE_PATHS)
    for mapping in INPUT_MAPPINGS:
        if config.count(mapping) != 1:
            problems.append(f"Input mapping missing or duplicated: {mapping}")
    for binding in PAWN_BINDINGS:
        if pawn.count(binding) != 1:
            problems.append(f"Pawn binding missing or duplicated: {binding}")
    if "DefaultPawnClass = AACIDPreludeCharacter::StaticClass()" not in mode:
        problems.append("Game mode no longer declares review pawn")
    if 'QuestLedger->ExportSnapshot()' not in pawn or "Nearest->TryInteract(this)" not in pawn:
        problems.append("Pawn investigation/update path not evident in source")
    for anchor in ANCHORS:
        if marker.count(f'Candidate == TEXT("{anchor}")') != 1:
            problems.append(f"Anchor missing or duplicated: {anchor}")
    for gate in GATES:
        if gate not in marker:
            problems.append(f"Missing interaction gate or receipt action: {gate}")
    if "MaxDistanceCm = 275.0f" not in marker:
        problems.append("Exact 2.75m dispatch distance gate changed")
    if not re.search(RECEIPT_SELECTION, marker):
        problems.append("Receipt selection/duplicate guard source path drifted")
    if not re.search(RECEIPT_BRIDGE, bridge):
        problems.append("Receipt action-to-clue bridge source path drifted")
    if "DiscoveredClues.Contains(ClueId)" not in ledger or "DiscoveredClues.Add(ClueId)" not in ledger:
        problems.append("Quest clue duplicate prevention source path drifted")
    if "UACIDQuestInteractionBridge::TryApplyAction(Character->GetQuestLedger(), Action)" not in marker:
        problems.append("Marker no longer dispatches to quest bridge")
    if re.search(r'->\s*(?:Feed|SetHunger|ModifyHunger)\s*\(', pawn + marker + bridge):
        problems.append("Direct hunger mutation detected in M008 interaction sources")
    return problems


def main() -> int:
    contents = {
        name: (ROOT / name).read_text(encoding="utf-8")
        for name in SOURCE_PATHS if (ROOT / name).is_file()
    }
    problems = check_sources(contents, (ROOT / MAP).is_file())
    if problems:
        for item in problems:
            print("M008 SOURCE PRECHECK FAIL:", item)
        return 1
    print("M008 SOURCE PRECHECK PASS: signature checks only; PIE INPUT/RENDERING/QUEST UPDATE NOT VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
