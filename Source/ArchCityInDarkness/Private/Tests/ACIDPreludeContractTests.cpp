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
    return true;
}
#endif
