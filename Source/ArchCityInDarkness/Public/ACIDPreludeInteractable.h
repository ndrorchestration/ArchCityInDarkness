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
private:
    FName SelectAction(const AACIDPreludeCharacter* Character) const;
};
