#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ACIDPreludeInteractable.generated.h"

class AACIDPreludeCharacter;
class UStaticMeshComponent;

/** Original noncanonical Glassbend review marker. Only five known anchors are accepted. */
UCLASS()
class ARCHCITYINDARKNESS_API AACIDPreludeInteractable : public AActor
{
    GENERATED_BODY()
public:
    AACIDPreludeInteractable();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Glassbend")
    TObjectPtr<UStaticMeshComponent> Marker;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category="Glassbend")
    FName AnchorId = NAME_None;

    UFUNCTION(BlueprintCallable, Category="Glassbend")
    bool TryInteract(AACIDPreludeCharacter* Character);

    static bool IsKnownAnchor(FName Candidate);

    /** Review-only NPCs permitted to open an explicit confirmation session. */
    bool IsReviewDialogueNPC() const;

    /** Recheck player, world, range, height and visibility at opening AND commit. */
    bool CanReviewInteract(const AACIDPreludeCharacter* Character) const;

    /** Fixed per-NPC choice identity; not arbitrary external player action. */
    FName GetReviewChoiceId() const;
    static FName ReviewChoiceActionForAnchor(FName CandidateAnchor, FName CandidateChoice);

    /** Requires the active dialogue session and in-world interaction gates. */
    bool TryCommitReviewChoice(AACIDPreludeCharacter* Character, FName ChoiceId);

    /** Fixed original M005 choice mapping; never accepts arbitrary action IDs. */
    static FName ActionForDialogueChoice(FName CandidateAnchor, FName ChoiceId);

    /** Called only after the active M005 node/choice is checked by the review UI. */
    bool TryApplyReviewDialogueChoice(AACIDPreludeCharacter* Character, FName ChoiceId);
private:
    FName SelectAction(const AACIDPreludeCharacter* Character) const;
};
