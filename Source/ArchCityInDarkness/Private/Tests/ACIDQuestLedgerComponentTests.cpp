#if WITH_DEV_AUTOMATION_TESTS

#include "ACIDQuestLedgerComponent.h"
#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FACIDQuestLedgerContractTest,
    "ArchCityInDarkness.Quest.Glassbend.Contract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FACIDQuestLedgerContractTest::RunTest(const FString& Parameters)
{
    UACIDQuestLedgerComponent* Dialogue = NewObject<UACIDQuestLedgerComponent>();
    if (!TestNotNull(TEXT("Quest component constructs"), Dialogue)) return false;

    TestFalse(TEXT("No resolution without prerequisite clues"),
        Dialogue->TryResolve(EACIDResolutionRoute::Dialogue));
    TestFalse(TEXT("Unknown clue is rejected"), Dialogue->DiscoverClue(FName(TEXT("unknown"))));
    TestTrue(TEXT("Shift receipt is discoverable"), Dialogue->DiscoverClue(FName(TEXT("shift_receipt"))));
    TestFalse(TEXT("Duplicate clue is rejected"), Dialogue->DiscoverClue(FName(TEXT("shift_receipt"))));
    TestTrue(TEXT("Ledger gap is discoverable"), Dialogue->DiscoverClue(FName(TEXT("ledger_gap"))));
    TestTrue(TEXT("Dialogue route resolves"), Dialogue->TryResolve(EACIDResolutionRoute::Dialogue));
    TestTrue(TEXT("Phase is resolved"), Dialogue->GetPhase() == EACIDQuestPhase::Resolved);
    TestEqual(TEXT("Dialogue reputation change"), Dialogue->GetMaraTrust(), 1);
    TestEqual(TEXT("Dialogue causes zero exposure"), Dialogue->GetPublicExposure(), 0);
    TestFalse(TEXT("Cannot rewrite resolved route"),
        Dialogue->TryResolve(EACIDResolutionRoute::Confrontation));
    TestFalse(TEXT("Cannot discover after final resolution"),
        Dialogue->DiscoverClue(FName(TEXT("annex_badge"))));

    const FACIDQuestSnapshot Snapshot = Dialogue->ExportSnapshot();
    UACIDQuestLedgerComponent* Restored = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Valid snapshot restores into fresh component"), Restored->TryRestoreSnapshot(Snapshot));
    TestTrue(TEXT("Restored route is dialogue"), Restored->GetRoute() == EACIDResolutionRoute::Dialogue);
    TestFalse(TEXT("Cannot restore again into resolved component"),
        Restored->TryRestoreSnapshot(Snapshot));

    FACIDQuestSnapshot Invalid = Snapshot;
    Invalid.PublicExposure = 99;
    UACIDQuestLedgerComponent* Rejector = NewObject<UACIDQuestLedgerComponent>();
    TestFalse(TEXT("Impossible snapshot is rejected"), Rejector->TryRestoreSnapshot(Invalid));
    TestTrue(TEXT("Rejected snapshot leaves phase unchanged"),
        Rejector->GetPhase() == EACIDQuestPhase::Investigating);

    UACIDQuestLedgerComponent* Stealth = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Route note discovered"), Stealth->DiscoverClue(FName(TEXT("route_note"))));
    TestTrue(TEXT("Stealth route resolves"), Stealth->TryResolve(EACIDResolutionRoute::Stealth));
    TestEqual(TEXT("Stealth exposure"), Stealth->GetPublicExposure(), 12);

    UACIDQuestLedgerComponent* Confrontation = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Annex badge discovered"), Confrontation->DiscoverClue(FName(TEXT("annex_badge"))));
    TestTrue(TEXT("Confrontation resolves"), Confrontation->TryResolve(EACIDResolutionRoute::Confrontation));
    TestEqual(TEXT("Confrontation exposure"), Confrontation->GetPublicExposure(), 25);
    TestEqual(TEXT("Confrontation trust"), Confrontation->GetMaraTrust(), -1);
    return true;
}
#endif // WITH_DEV_AUTOMATION_TESTS
