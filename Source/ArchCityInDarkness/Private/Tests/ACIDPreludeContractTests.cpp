#if WITH_DEV_AUTOMATION_TESTS
#include "ACIDPreludeInteractable.h"
#include "ACIDPreludeCharacter.h"
#include "ACIDPreludeGameMode.h"
#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FACIDPreludeContract,
    "ArchCityInDarkness.Prelude.Glassbend.Contract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FACIDPreludeContract::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("Known receipt anchor"), AACIDPreludeInteractable::IsKnownAnchor(TEXT("shift_receipt")));
    TestTrue(TEXT("Known archivist anchor"), AACIDPreludeInteractable::IsKnownAnchor(TEXT("mara_vale")));
    TestTrue(TEXT("Known courier anchor"), AACIDPreludeInteractable::IsKnownAnchor(TEXT("nico_bell")));
    TestTrue(TEXT("Known annex clue"), AACIDPreludeInteractable::IsKnownAnchor(TEXT("annex_badge")));
    TestTrue(TEXT("Known manager anchor"), AACIDPreludeInteractable::IsKnownAnchor(TEXT("etta_quill")));
    TestFalse(TEXT("Unknown ID must fail closed"), AACIDPreludeInteractable::IsKnownAnchor(TEXT("other")));
    TestNotNull(TEXT("Marker class is registered"), AACIDPreludeInteractable::StaticClass());
    TestFalse(TEXT("Class default object rejects null player"),
        GetMutableDefault<AACIDPreludeInteractable>()->TryInteract(nullptr));
    TestNotNull(TEXT("Review pawn class"), AACIDPreludeCharacter::StaticClass());
    TestNotNull(TEXT("Review game mode class"), AACIDPreludeGameMode::StaticClass());
    // Source-level automation assertions; these must be executed in a NEW
    // native UE 5.8.4 test run before counting as verified.
    TestEqual(TEXT("Mara explicit choice is dialogue only"),
        AACIDPreludeInteractable::ReviewChoiceActionForAnchor(
            TEXT("mara_vale"), TEXT("mara_resolve")), FName(TEXT("commit_dialogue")));
    TestEqual(TEXT("Nico explicit choice is stealth only"),
        AACIDPreludeInteractable::ReviewChoiceActionForAnchor(
            TEXT("nico_bell"), TEXT("nico_resolve")), FName(TEXT("commit_stealth")));
    TestEqual(TEXT("Etta explicit choice is confrontation only"),
        AACIDPreludeInteractable::ReviewChoiceActionForAnchor(
            TEXT("etta_quill"), TEXT("etta_resolve")), FName(TEXT("commit_confrontation")));
    TestEqual(TEXT("Mismatched NPC choice rejects"),
        AACIDPreludeInteractable::ReviewChoiceActionForAnchor(
            TEXT("mara_vale"), TEXT("nico_resolve")), NAME_None);
    TestEqual(TEXT("Unknown NPC rejects"),
        AACIDPreludeInteractable::ReviewChoiceActionForAnchor(
            TEXT("other_npc"), TEXT("mara_resolve")), NAME_None);
    TestEqual(TEXT("Raw action ID cannot be a choice"),
        AACIDPreludeInteractable::ReviewChoiceActionForAnchor(
            TEXT("mara_vale"), TEXT("commit_dialogue")), NAME_None);
    TestFalse(TEXT("No pending player can resolve on default marker"),
        GetMutableDefault<AACIDPreludeInteractable>()->TryCommitReviewChoice(
            nullptr, TEXT("mara_resolve")));
    return true;
}
#endif
