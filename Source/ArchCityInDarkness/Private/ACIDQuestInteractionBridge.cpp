#include "ACIDQuestInteractionBridge.h"
#include "ACIDQuestLedgerComponent.h"

bool UACIDQuestInteractionBridge::TryApplyAction(
    UACIDQuestLedgerComponent* QuestLedger, FName ActionId)
{
    if (!IsValid(QuestLedger) || ActionId.IsNone())
    {
        return false;
    }

    // These identifiers must match Prototypes/Glassbend/interaction_bindings_v1.json.
    // This code does NOT validate who pressed a button or where the player is standing.
    if (ActionId == FName(TEXT("inspect_receipt")))
    {
        return QuestLedger->DiscoverClue(FName(TEXT("shift_receipt")));
    }
    if (ActionId == FName(TEXT("ask_mara_about_ledger")))
    {
        return QuestLedger->DiscoverClue(FName(TEXT("ledger_gap")));
    }
    if (ActionId == FName(TEXT("ask_nico_about_route")))
    {
        return QuestLedger->DiscoverClue(FName(TEXT("route_note")));
    }
    if (ActionId == FName(TEXT("inspect_annex_badge")))
    {
        return QuestLedger->DiscoverClue(FName(TEXT("annex_badge")));
    }

    if (ActionId == FName(TEXT("commit_dialogue")))
    {
        return QuestLedger->TryResolve(EACIDResolutionRoute::Dialogue);
    }
    if (ActionId == FName(TEXT("commit_stealth")))
    {
        return QuestLedger->TryResolve(EACIDResolutionRoute::Stealth);
    }
    if (ActionId == FName(TEXT("commit_confrontation")))
    {
        return QuestLedger->TryResolve(EACIDResolutionRoute::Confrontation);
    }
    return false;
}
