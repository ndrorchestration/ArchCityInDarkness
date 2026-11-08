#!/usr/bin/env python3
"""M008 portable preflight, NOT an Unreal compilation, PIE test or visual proof."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = "Content/ArchCity/Review/Glassbend_Prelude_Greybox.umap"
INPUT = "Config/DefaultInput.ini"
PAWN = "Source/ArchCityInDarkness/Private/ACIDPreludeCharacter.cpp"
MARKERS = "Source/ArchCityInDarkness/Private/ACIDPreludeInteractable.cpp"
MODE = "Source/ArchCityInDarkness/Private/ACIDPreludeGameMode.cpp"

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


def check_sources(source: dict[str, str], map_present: bool) -> list[str]:
    """Check textual wiring only; matched strings are not execution evidence."""
    problems = []
    for path in (INPUT, PAWN, MARKERS, MODE):
        if path not in source:
            problems.append(f"Missing source: {path}")
    if problems:
        return problems
    if not map_present:
        problems.append(f"Missing noncanonical review map: {MAP}")
    config, pawn, marker, mode = (source[p] for p in (INPUT, PAWN, MARKERS, MODE))
    for mapping in INPUT_MAPPINGS:
        if mapping not in config:
            problems.append(f"Missing input mapping: {mapping}")
    for binding in PAWN_BINDINGS:
        if binding not in pawn:
            problems.append(f"Missing pawn binding: {binding}")
    if "DefaultPawnClass = AACIDPreludeCharacter::StaticClass()" not in mode:
        problems.append("Game mode no longer declares review pawn")
    if 'QuestLedger->ExportSnapshot()' not in pawn or "Nearest->TryInteract(this)" not in pawn:
        problems.append("Pawn investigation/update path not evident in source")
    for anchor in ANCHORS:
        if f'Candidate == TEXT("{anchor}")' not in marker:
            problems.append(f"Missing anchor allowlist ID: {anchor}")
    for gate in GATES:
        if gate not in marker:
            problems.append(f"Missing interaction gate or receipt action: {gate}")
    if "MaxDistanceCm = 275.0f" not in marker:
        problems.append("Exact 2.75m dispatch distance gate changed")
    return problems


def main() -> int:
    contents = {name: (ROOT / name).read_text(encoding="utf-8")
                for name in (INPUT, PAWN, MARKERS, MODE) if (ROOT / name).is_file()}
    problems = check_sources(contents, (ROOT / MAP).is_file())
    if problems:
        for item in problems:
            print("M008 SOURCE PRECHECK FAIL:", item)
        return 1
    print("M008 SOURCE PRECHECK PASS: wiring signatures only; PIE INPUT/RENDERING/QUEST UPDATE NOT VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
