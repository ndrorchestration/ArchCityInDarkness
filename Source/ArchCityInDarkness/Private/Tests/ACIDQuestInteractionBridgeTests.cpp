#if WITH_DEV_AUTOMATION_TESTS

#include "ACIDQuestInteractionBridge.h"
#include "ACIDQuestLedgerComponent.h"
#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FACIDQuestInteractionBridgeContract,
    "ArchCityInDarkness.Interaction.Glassbend.Contract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FACIDQuestInteractionBridgeContract::RunTest(const FString& Parameters)
{
    const auto Apply = [](UACIDQuestLedgerComponent* Ledger, const TCHAR* Id) {
        return UACIDQuestInteractionBridge::TryApplyAction(Ledger, FName(Id));
    };

    UACIDQuestLedgerComponent* Dialogue = NewObject<UACIDQuestLedgerComponent>();
    if (!TestNotNull(TEXT("Dialogue ledger constructs"), Dialogue)) return false;

    TestFalse(TEXT("Null ledger rejects known actions"),
        UACIDQuestInteractionBridge::TryApplyAction(nullptr, FName(TEXT("inspect_receipt"))));
    TestFalse(TEXT("Empty action rejected"), 
        UACIDQuestInteractionBridge::TryApplyAction(Dialogue, NAME_None));
    TestFalse(TEXT("Unrecognized action rejected without state mutation"),
        Apply(Dialogue, TEXT("unsupported_action")));
    TestTrue(TEXT("Invalid dispatch keeps ledger investigating"),
        Dialogue->GetPhase() == EACIDQuestPhase::Investigating &&
        Dialogue->GetEvidenceId().IsNone());

    TestFalse(TEXT("No route resolution before prerequisites"),
        Apply(Dialogue, TEXT("commit_dialogue")));
    TestTrue(TEXT("Receipt action discovers receipt"),
        Apply(Dialogue, TEXT("inspect_receipt")));
    TestFalse(TEXT("Duplicate receipt action rejects"),
        Apply(Dialogue, TEXT("inspect_receipt")));
    TestFalse(TEXT("One clue cannot resolve dialogue"),
        Apply(Dialogue, TEXT("commit_dialogue")));
    TestTrue(TEXT("Mara action discovers ledger gap"),
        Apply(Dialogue, TEXT("ask_mara_about_ledger")));
    TestTrue(TEXT("Dialogue route action resolves"),
        Apply(Dialogue, TEXT("commit_dialogue")));
    TestEqual(TEXT("Dialogue trust"), Dialogue->GetMaraTrust(), 1);
    TestEqual(TEXT("Dialogue public exposure"), Dialogue->GetPublicExposure(), 0);
    TestTrue(TEXT("Dialogue evidence"),
        Dialogue->GetEvidenceId() == FName(TEXT("redacted_shift_log")));
    TestFalse(TEXT("Cannot overwrite resolved route"),
        Apply(Dialogue, TEXT("commit_confrontation")));
    TestFalse(TEXT("Cannot collect clue after resolution"),
        Apply(Dialogue, TEXT("inspect_annex_badge")));

    UACIDQuestLedgerComponent* Stealth = NewObject<UACIDQuestLedgerComponent>();
    if (!TestNotNull(TEXT("Stealth ledger constructs"), Stealth)) return false;
    TestTrue(TEXT("Nico action discovers route note"),
        Apply(Stealth, TEXT("ask_nico_about_route")));
    TestTrue(TEXT("Stealth route action resolves"),
        Apply(Stealth, TEXT("commit_stealth")));
    TestEqual(TEXT("Stealth public exposure"), Stealth->GetPublicExposure(), 12);
    TestTrue(TEXT("Stealth evidence"),
        Stealth->GetEvidenceId() == FName(TEXT("timecard_photo")));

    UACIDQuestLedgerComponent* Confrontation = NewObject<UACIDQuestLedgerComponent>();
    if (!TestNotNull(TEXT("Confrontation ledger constructs"), Confrontation)) return false;
    TestTrue(TEXT("Annex badge action discovers badge"),
        Apply(Confrontation, TEXT("inspect_annex_badge")));
    TestTrue(TEXT("Confrontation route action resolves"),
        Apply(Confrontation, TEXT("commit_confrontation")));
    TestEqual(TEXT("Confrontation trust"), Confrontation->GetMaraTrust(), -1);
    TestEqual(TEXT("Confrontation public exposure"), Confrontation->GetPublicExposure(), 25);
    TestTrue(TEXT("Confrontation evidence"),
        Confrontation->GetEvidenceId() == FName(TEXT("discarded_register")));

    return true;
}
#endif // WITH_DEV_AUTOMATION_TESTS
