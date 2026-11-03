#include "ACIDQuestLedgerComponent.h"

namespace ACIDQuest
{
    const FName ShiftReceipt(TEXT("shift_receipt"));
    const FName LedgerGap(TEXT("ledger_gap"));
    const FName RouteNote(TEXT("route_note"));
    const FName AnnexBadge(TEXT("annex_badge"));
    const FName RedactedShiftLog(TEXT("redacted_shift_log"));
    const FName TimecardPhoto(TEXT("timecard_photo"));
    const FName DiscardedRegister(TEXT("discarded_register"));
}

UACIDQuestLedgerComponent::UACIDQuestLedgerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UACIDQuestLedgerComponent::IsKnownClue(FName ClueId)
{
    return ClueId == ACIDQuest::ShiftReceipt || ClueId == ACIDQuest::LedgerGap ||
           ClueId == ACIDQuest::RouteNote || ClueId == ACIDQuest::AnnexBadge;
}

bool UACIDQuestLedgerComponent::DiscoverClue(FName ClueId)
{
    if (Phase != EACIDQuestPhase::Investigating ||
        !IsKnownClue(ClueId) || DiscoveredClues.Contains(ClueId))
    {
        return false;
    }
    DiscoveredClues.Add(ClueId);
    return true;
}

bool UACIDQuestLedgerComponent::HasClue(FName ClueId) const
{
    return DiscoveredClues.Contains(ClueId);
}

bool UACIDQuestLedgerComponent::RequirementsSatisfied(
    EACIDResolutionRoute SelectedRoute, const TSet<FName>& OwnedClues)
{
    switch (SelectedRoute)
    {
        case EACIDResolutionRoute::Dialogue:
            return OwnedClues.Contains(ACIDQuest::ShiftReceipt) &&
                   OwnedClues.Contains(ACIDQuest::LedgerGap);
        case EACIDResolutionRoute::Stealth:
            return OwnedClues.Contains(ACIDQuest::RouteNote);
        case EACIDResolutionRoute::Confrontation:
            return OwnedClues.Contains(ACIDQuest::AnnexBadge);
        default:
            return false;
    }
}

FName UACIDQuestLedgerComponent::EvidenceFor(EACIDResolutionRoute SelectedRoute)
{
    switch (SelectedRoute)
    {
        case EACIDResolutionRoute::Dialogue: return ACIDQuest::RedactedShiftLog;
        case EACIDResolutionRoute::Stealth: return ACIDQuest::TimecardPhoto;
        case EACIDResolutionRoute::Confrontation: return ACIDQuest::DiscardedRegister;
        default: return NAME_None;
    }
}

bool UACIDQuestLedgerComponent::TryResolve(EACIDResolutionRoute SelectedRoute)
{
    if (Phase != EACIDQuestPhase::Investigating ||
        !RequirementsSatisfied(SelectedRoute, DiscoveredClues))
    {
        return false;
    }

    const FName NextEvidence = EvidenceFor(SelectedRoute);
    if (NextEvidence.IsNone())
    {
        return false;
    }

    Route = SelectedRoute;
    EvidenceId = NextEvidence;
    MaraTrust = SelectedRoute == EACIDResolutionRoute::Dialogue ? 1 :
                SelectedRoute == EACIDResolutionRoute::Confrontation ? -1 : 0;
    PublicExposure = SelectedRoute == EACIDResolutionRoute::Stealth ? 12 :
                     SelectedRoute == EACIDResolutionRoute::Confrontation ? 25 : 0;
    Phase = EACIDQuestPhase::Resolved;
    OnQuestResolved.Broadcast(Route);
    return true;
}

FACIDQuestSnapshot UACIDQuestLedgerComponent::ExportSnapshot() const
{
    FACIDQuestSnapshot Out;
    Out.Phase = Phase;
    Out.Route = Route;
    Out.EvidenceId = EvidenceId;
    Out.MaraTrust = MaraTrust;
    Out.PublicExposure = PublicExposure;
    // Stable ordering means identical state produces identical serialized clue arrays.
    for (FName Candidate : {ACIDQuest::ShiftReceipt, ACIDQuest::LedgerGap,
                            ACIDQuest::RouteNote, ACIDQuest::AnnexBadge})
    {
        if (DiscoveredClues.Contains(Candidate))
        {
            Out.Clues.Add(Candidate);
        }
    }
    return Out;
}

bool UACIDQuestLedgerComponent::ValidateSnapshot(const FACIDQuestSnapshot& Candidate)
{
    if (Candidate.SchemaVersion != 1 || Candidate.PublicExposure < 0 ||
        Candidate.PublicExposure > 100)
    {
        return false;
    }

    TSet<FName> UniqueClues;
    for (FName Clue : Candidate.Clues)
    {
        if (!IsKnownClue(Clue) || UniqueClues.Contains(Clue))
        {
            return false;
        }
        UniqueClues.Add(Clue);
    }
    if (Candidate.Phase == EACIDQuestPhase::Investigating)
    {
        return Candidate.Route == EACIDResolutionRoute::None &&
               Candidate.EvidenceId.IsNone() &&
               Candidate.MaraTrust == 0 && Candidate.PublicExposure == 0;
    }
    if (Candidate.Phase != EACIDQuestPhase::Resolved ||
        !RequirementsSatisfied(Candidate.Route, UniqueClues) ||
        Candidate.EvidenceId != EvidenceFor(Candidate.Route))
    {
        return false;
    }
    const int32 Trust = Candidate.Route == EACIDResolutionRoute::Dialogue ? 1 :
                        Candidate.Route == EACIDResolutionRoute::Confrontation ? -1 : 0;
    const int32 Exposure = Candidate.Route == EACIDResolutionRoute::Stealth ? 12 :
                           Candidate.Route == EACIDResolutionRoute::Confrontation ? 25 : 0;
    return Candidate.MaraTrust == Trust && Candidate.PublicExposure == Exposure;
}

bool UACIDQuestLedgerComponent::TryRestoreSnapshot(const FACIDQuestSnapshot& Candidate)
{
    // Never replace a live choice or collected clue. Call only on a fresh component.
    if (Phase != EACIDQuestPhase::Investigating ||
        Route != EACIDResolutionRoute::None ||
        !DiscoveredClues.IsEmpty() || !ValidateSnapshot(Candidate))
    {
        return false;
    }

    for (FName Clue : Candidate.Clues)
    {
        DiscoveredClues.Add(Clue);
    }
    Phase = Candidate.Phase;
    Route = Candidate.Route;
    EvidenceId = Candidate.EvidenceId;
    MaraTrust = Candidate.MaraTrust;
    PublicExposure = Candidate.PublicExposure;
    return true;
}
