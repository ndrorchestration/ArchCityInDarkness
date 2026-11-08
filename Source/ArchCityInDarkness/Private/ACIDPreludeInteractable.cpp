#include "ACIDPreludeInteractable.h"
#include "ACIDPreludeCharacter.h"
#include "ACIDQuestLedgerComponent.h"
#include "ACIDQuestInteractionBridge.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "UObject/ConstructorHelpers.h"

AACIDPreludeInteractable::AACIDPreludeInteractable()
{
    PrimaryActorTick.bCanEverTick = false;
    Marker = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Marker"));
    RootComponent = Marker;
    Marker->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
    Marker->SetCollisionResponseToAllChannels(ECR_Ignore);
    Marker->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
    Marker->SetRelativeScale3D(FVector(0.65, 0.65, 1.7));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
    if (Cube.Succeeded())
    {
        Marker->SetStaticMesh(Cube.Object);
    }
}

bool AACIDPreludeInteractable::IsKnownAnchor(FName Candidate)
{
    return Candidate == TEXT("shift_receipt") || Candidate == TEXT("mara_vale") ||
        Candidate == TEXT("nico_bell") || Candidate == TEXT("annex_badge") ||
        Candidate == TEXT("etta_quill");
}

FName AACIDPreludeInteractable::SelectAction(const AACIDPreludeCharacter* Character) const
{
    const UACIDQuestLedgerComponent* Ledger = IsValid(Character) ? Character->GetQuestLedger() : nullptr;
    if (!IsValid(Ledger) || Ledger->GetPhase() != EACIDQuestPhase::Investigating)
    {
        return NAME_None;
    }
    if (AnchorId == TEXT("shift_receipt"))
        return Ledger->HasClue(TEXT("shift_receipt")) ? NAME_None : FName(TEXT("inspect_receipt"));
    if (AnchorId == TEXT("annex_badge"))
        return Ledger->HasClue(TEXT("annex_badge")) ? NAME_None : FName(TEXT("inspect_annex_badge"));
    // In this review actor, E can discover a clue but MUST NEVER select an
    // irreversible route by itself. The separately proposed M005 dialogue
    // choices are not an Unreal UI; a later explicit, world-gated player
    // selection must dispatch commit_dialogue/stealth/confrontation.
    if (AnchorId == TEXT("mara_vale"))
        return Ledger->HasClue(TEXT("ledger_gap")) ? NAME_None : FName(TEXT("ask_mara_about_ledger"));
    if (AnchorId == TEXT("nico_bell"))
        return Ledger->HasClue(TEXT("route_note")) ? NAME_None : FName(TEXT("ask_nico_about_route"));
    if (AnchorId == TEXT("etta_quill"))
        return NAME_None;
    return NAME_None;
}

bool AACIDPreludeInteractable::TryInteract(AACIDPreludeCharacter* Character)
{
    if (!IsKnownAnchor(AnchorId) || !IsValid(Character) || !Character->IsPlayerControlled() ||
        GetWorld() == nullptr || Character->GetWorld() != GetWorld() ||
        GetWorld()->GetNetMode() != NM_Standalone)
    {
        return false;
    }

    // Recheck both gates at dispatch, not only while the pawn selects a target.
    constexpr float MaxDistanceCm = 275.0f;
    if (FVector::DistSquared2D(Character->GetActorLocation(), GetActorLocation()) >
        FMath::Square(MaxDistanceCm) ||
        FMath::Abs(Character->GetActorLocation().Z - GetActorLocation().Z) > 200.0f)
    {
        return false;
    }
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(GlassbendInteract), false);
    Params.AddIgnoredActor(Character);
    const FVector Eyes = Character->GetPawnViewLocation();
    const FVector Target = GetActorLocation() + FVector(0, 0, 85);
    const bool Blocked = GetWorld()->LineTraceSingleByChannel(Hit, Eyes, Target, ECC_Visibility, Params);
    if (Blocked && Hit.GetActor() != this)
    {
        return false;
    }
    const FName Action = SelectAction(Character);
    if (Action.IsNone())
    {
        return false;
    }
    return UACIDQuestInteractionBridge::TryApplyAction(Character->GetQuestLedger(), Action);
}

bool AACIDPreludeInteractable::IsReviewDialogueNPC() const
{
    return AnchorId == TEXT("mara_vale") || AnchorId == TEXT("nico_bell") ||
        AnchorId == TEXT("etta_quill");
}

FName AACIDPreludeInteractable::GetReviewChoiceId() const
{
    if (AnchorId == TEXT("mara_vale")) return FName(TEXT("mara_resolve"));
    if (AnchorId == TEXT("nico_bell")) return FName(TEXT("nico_resolve"));
    if (AnchorId == TEXT("etta_quill")) return FName(TEXT("etta_resolve"));
    return NAME_None;
}

FName AACIDPreludeInteractable::ReviewChoiceActionForAnchor(FName CandidateAnchor, FName CandidateChoice)
{
    // Exact original M005 IDs. Do not expose generic action-ID dispatch from input.
    if (CandidateAnchor == TEXT("mara_vale") && CandidateChoice == TEXT("mara_resolve"))
        return FName(TEXT("commit_dialogue"));
    if (CandidateAnchor == TEXT("nico_bell") && CandidateChoice == TEXT("nico_resolve"))
        return FName(TEXT("commit_stealth"));
    if (CandidateAnchor == TEXT("etta_quill") && CandidateChoice == TEXT("etta_resolve"))
        return FName(TEXT("commit_confrontation"));
    return NAME_None;
}

bool AACIDPreludeInteractable::CanReviewInteract(const AACIDPreludeCharacter* Character) const
{
    if (!IsKnownAnchor(AnchorId) || !IsValid(Character) || !Character->IsPlayerControlled() ||
        GetWorld() == nullptr || Character->GetWorld() != GetWorld() ||
        GetWorld()->GetNetMode() != NM_Standalone)
    {
        return false;
    }

    // The same range, height and line-of-sight conditions are checked again
    // at confirmation. Opening a session never grants persistent authorization.
    constexpr float MaxDistanceCm = 275.0f;
    if (FVector::DistSquared2D(Character->GetActorLocation(), GetActorLocation()) >
        FMath::Square(MaxDistanceCm) ||
        FMath::Abs(Character->GetActorLocation().Z - GetActorLocation().Z) > 200.0f)
    {
        return false;
    }
    FHitResult Hit;
    FCollisionQueryParams Params(SCENE_QUERY_STAT(GlassbendReviewConfirm), false);
    Params.AddIgnoredActor(Character);
    const FVector Eyes = Character->GetPawnViewLocation();
    const FVector Target = GetActorLocation() + FVector(0, 0, 85);
    const bool Blocked = GetWorld()->LineTraceSingleByChannel(
        Hit, Eyes, Target, ECC_Visibility, Params);
    return !Blocked || Hit.GetActor() == this;
}

bool AACIDPreludeInteractable::TryCommitReviewChoice(
    AACIDPreludeCharacter* Character, FName ChoiceId)
{
    if (!IsReviewDialogueNPC() || !CanReviewInteract(Character) ||
        !Character->IsReviewDialogueActiveFor(this))
    {
        return false;
    }
    UACIDQuestLedgerComponent* Ledger = Character->GetQuestLedger();
    if (!IsValid(Ledger) || Ledger->GetPhase() != EACIDQuestPhase::Investigating)
    {
        return false;
    }
    const FName Action = ReviewChoiceActionForAnchor(AnchorId, ChoiceId);
    if (Action.IsNone())
    {
        return false;
    }
    // The quest ledger itself enforces prerequisite clues and only one ending.
    return UACIDQuestInteractionBridge::TryApplyAction(Ledger, Action);
}
