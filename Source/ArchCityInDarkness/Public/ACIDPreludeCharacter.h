#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "ACIDPreludeCharacter.generated.h"

class UCameraComponent;
class UACIDHungerComponent;
class UACIDQuestLedgerComponent;

/** Disposable first-person review pawn. E collects clues / selects eligible endings. */
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

private:
    UPROPERTY(VisibleAnywhere, Category="Glassbend")
    TObjectPtr<UCameraComponent> ViewCamera;

    UPROPERTY(VisibleAnywhere, Category="Glassbend")
    TObjectPtr<UACIDHungerComponent> Hunger;

    UPROPERTY(VisibleAnywhere, Category="Glassbend")
    TObjectPtr<UACIDQuestLedgerComponent> QuestLedger;

    void MoveForward(float Value);
    void MoveRight(float Value);
    void LookYaw(float Value);
    void LookPitch(float Value);
    void Interact();
    void ShowStatus();
    void PrintReviewText(const FString& Message) const;
};
