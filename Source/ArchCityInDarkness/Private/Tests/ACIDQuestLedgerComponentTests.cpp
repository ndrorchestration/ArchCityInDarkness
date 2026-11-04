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

    const FACIDQuestSnapshot InitialState = Dialogue->ExportSnapshot();
    TestFalse(TEXT("No resolution without prerequisite clues"),
        Dialogue->TryResolve(EACIDResolutionRoute::Dialogue));
    TestTrue(TEXT("Failed resolution preserves investigating phase"),
        Dialogue->GetPhase() == InitialState.Phase);
    TestTrue(TEXT("Failed resolution preserves empty evidence"),
        Dialogue->GetEvidenceId().IsNone());
    TestFalse(TEXT("Unknown clue is rejected"), Dialogue->DiscoverClue(FName(TEXT("unknown"))));
    TestTrue(TEXT("Shift receipt is discoverable"), Dialogue->DiscoverClue(FName(TEXT("shift_receipt"))));
    TestFalse(TEXT("Duplicate clue is rejected"), Dialogue->DiscoverClue(FName(TEXT("shift_receipt"))));
    TestFalse(TEXT("One of two dialogue clues is insufficient"),
        Dialogue->TryResolve(EACIDResolutionRoute::Dialogue));
    TestTrue(TEXT("Missing clue resolution has no effects"),
        Dialogue->GetEvidenceId().IsNone() && Dialogue->GetMaraTrust() == 0 &&
        Dialogue->GetPublicExposure() == 0);
    TestTrue(TEXT("Ledger gap is discoverable"), Dialogue->DiscoverClue(FName(TEXT("ledger_gap"))));
    TestTrue(TEXT("Dialogue route resolves"), Dialogue->TryResolve(EACIDResolutionRoute::Dialogue));
    TestTrue(TEXT("Phase is resolved"), Dialogue->GetPhase() == EACIDQuestPhase::Resolved);
    TestEqual(TEXT("Dialogue reputation change"), Dialogue->GetMaraTrust(), 1);
    TestEqual(TEXT("Dialogue causes zero exposure"), Dialogue->GetPublicExposure(), 0);
    TestTrue(TEXT("Dialogue grants its precise evidence"),
        Dialogue->GetEvidenceId() == FName(TEXT("redacted_shift_log")));
    TestFalse(TEXT("Cannot rewrite resolved route"),
        Dialogue->TryResolve(EACIDResolutionRoute::Confrontation));
    TestFalse(TEXT("Cannot discover after final resolution"),
        Dialogue->DiscoverClue(FName(TEXT("annex_badge"))));

    const FACIDQuestSnapshot Snapshot = Dialogue->ExportSnapshot();
    UACIDQuestLedgerComponent* Restored = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Valid snapshot restores into fresh component"), Restored->TryRestoreSnapshot(Snapshot));
    TestTrue(TEXT("Restored route is dialogue"), Restored->GetRoute() == EACIDResolutionRoute::Dialogue);
    TestTrue(TEXT("Restored snapshot retains evidence and clues"),
        Restored->GetEvidenceId() == Snapshot.EvidenceId &&
        Restored->HasClue(FName(TEXT("shift_receipt"))) &&
        Restored->HasClue(FName(TEXT("ledger_gap"))));
    TestFalse(TEXT("Cannot restore again into resolved component"),
        Restored->TryRestoreSnapshot(Snapshot));

    FACIDQuestSnapshot Invalid = Snapshot;
    Invalid.PublicExposure = 99;
    UACIDQuestLedgerComponent* Rejector = NewObject<UACIDQuestLedgerComponent>();
    TestFalse(TEXT("Impossible snapshot is rejected"), Rejector->TryRestoreSnapshot(Invalid));
    TestTrue(TEXT("Rejected snapshot leaves phase and evidence unchanged"),
        Rejector->GetPhase() == EACIDQuestPhase::Investigating &&
        Rejector->GetEvidenceId().IsNone());

    FACIDQuestSnapshot WrongVersion = Snapshot;
    WrongVersion.SchemaVersion = 2;
    TestFalse(TEXT("Unsupported snapshot schema rejected"),
        Rejector->TryRestoreSnapshot(WrongVersion));

    FACIDQuestSnapshot WrongEvidence = Snapshot;
    WrongEvidence.EvidenceId = FName(TEXT("timecard_photo"));
    TestFalse(TEXT("Contradictory route evidence rejected"),
        Rejector->TryRestoreSnapshot(WrongEvidence));

    FACIDQuestSnapshot DuplicateClue = Snapshot;
    DuplicateClue.Clues.Add(FName(TEXT("shift_receipt")));
    TestFalse(TEXT("Duplicate snapshot clues rejected"),
        Rejector->TryRestoreSnapshot(DuplicateClue));

    FACIDQuestSnapshot MissingPrerequisite = Snapshot;
    MissingPrerequisite.Clues.Remove(FName(TEXT("ledger_gap")));
    TestFalse(TEXT("Resolved snapshot missing route prerequisites rejected"),
        Rejector->TryRestoreSnapshot(MissingPrerequisite));

    FACIDQuestSnapshot InvalidTrust = Snapshot;
    InvalidTrust.MaraTrust = 12;
    TestFalse(TEXT("Impossible route trust rejected"),
        Rejector->TryRestoreSnapshot(InvalidTrust));

    FACIDQuestSnapshot InvalidUnresolved = InitialState;
    InvalidUnresolved.EvidenceId = FName(TEXT("redacted_shift_log"));
    TestFalse(TEXT("Unresolved snapshot containing resolved evidence rejected"),
        Rejector->TryRestoreSnapshot(InvalidUnresolved));

    TestTrue(TEXT("All invalid restores leave the fresh component pristine"),
        Rejector->GetPhase() == EACIDQuestPhase::Investigating &&
        Rejector->GetRoute() == EACIDResolutionRoute::None &&
        Rejector->GetEvidenceId().IsNone() &&
        !Rejector->HasClue(FName(TEXT("shift_receipt"))));

    UACIDQuestLedgerComponent* Preparing = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Preparing incomplete investigation clue"),
        Preparing->DiscoverClue(FName(TEXT("shift_receipt"))));
    const FACIDQuestSnapshot Partial = Preparing->ExportSnapshot();
    UACIDQuestLedgerComponent* InProgress = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Incomplete in-progress snapshot restores"),
        InProgress->TryRestoreSnapshot(Partial));
    TestTrue(TEXT("Restored progress retains discovered clue"),
        InProgress->HasClue(FName(TEXT("shift_receipt"))));
    TestFalse(TEXT("Restored progress is not prematurely resolved"),
        InProgress->TryResolve(EACIDResolutionRoute::Dialogue));
    TestTrue(TEXT("Restored progress can still acquire remaining clue"),
        InProgress->DiscoverClue(FName(TEXT("ledger_gap"))));
    TestTrue(TEXT("Restored progress can complete quest"),
        InProgress->TryResolve(EACIDResolutionRoute::Dialogue));


    UACIDQuestLedgerComponent* Stealth = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Route note discovered"), Stealth->DiscoverClue(FName(TEXT("route_note"))));
    TestTrue(TEXT("Stealth route resolves"), Stealth->TryResolve(EACIDResolutionRoute::Stealth));
    TestEqual(TEXT("Stealth exposure"), Stealth->GetPublicExposure(), 12);
    TestTrue(TEXT("Stealth route evidence is distinct"),
        Stealth->GetEvidenceId() == FName(TEXT("timecard_photo")));

    UACIDQuestLedgerComponent* Confrontation = NewObject<UACIDQuestLedgerComponent>();
    TestTrue(TEXT("Annex badge discovered"), Confrontation->DiscoverClue(FName(TEXT("annex_badge"))));
    TestTrue(TEXT("Confrontation resolves"), Confrontation->TryResolve(EACIDResolutionRoute::Confrontation));
    TestEqual(TEXT("Confrontation exposure"), Confrontation->GetPublicExposure(), 25);
    TestEqual(TEXT("Confrontation trust"), Confrontation->GetMaraTrust(), -1);
    TestTrue(TEXT("Confrontation evidence is distinct"),
        Confrontation->GetEvidenceId() == FName(TEXT("discarded_register")));
    return true;
}
#endif // WITH_DEV_AUTOMATION_TESTS
