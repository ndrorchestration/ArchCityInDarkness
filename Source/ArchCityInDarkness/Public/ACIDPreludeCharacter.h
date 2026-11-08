#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ACIDPreludeCharacter.generated.h"

class UCameraComponent;
class UACIDHungerComponent;
class UACIDQuestLedgerComponent;
class AACIDPreludeInteractable;
class UACIDReviewDialogueWidget;

/** Disposable first-person review pawn. E collects clues; dialogue routes need F+Enter. */
UCLASS()
class ARCHCITYINDARKNESS_API AACIDPreludeCharacter : public ACharacter
{
    GENERATED_BODY()
public:
    AACIDPreludeCharacter();
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintPure, Category="Glassbend")
    UACIDQuestLedgerComponent* GetQuestLedger() const { return QuestLedger; }

    /** Internal session check; no arbitrary action IDs are accepted from player input. */
    bool IsReviewDialogueActiveFor(const AACIDPreludeInteractable* Marker) const;

    /** Called when the disposable captioned source-graph widget closes. */
    void EndGraphDialogue(UACIDReviewDialogueWidget* Source);

private:
    UPROPERTY(VisibleAnywhere, Category="Glassbend")
    TObjectPtr<UCameraComponent> ViewCamera;

    UPROPERTY(VisibleAnywhere, Category="Glassbend")
    TObjectPtr<UACIDHungerComponent> Hunger;

    UPROPERTY(VisibleAnywhere, Category="Glassbend")
    TObjectPtr<UACIDQuestLedgerComponent> QuestLedger;

    /** Weak reference: an actor disappearing invalidates a pending review choice. */
    TWeakObjectPtr<AACIDPreludeInteractable> ActiveReviewDialogueMarker;

    UPROPERTY(Transient)
    TObjectPtr<UACIDReviewDialogueWidget> ActiveGraphWidget;

    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    void Interact();
    void OpenReviewDialogue();
    void OpenGraphDialogue();
    void ConfirmReviewDialogue();
    void CancelReviewDialogue();
    void ShowStatus();
    void PrintReviewText(const FString& Message) const;
};
