#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ACIDHungerComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FACIDOnHungerChanged, float, PreviousHunger, float, CurrentHunger);

/**
 * Small, reusable and intentionally non-ticking prototype rule.
 * 0 = satiated; 100 = maximum hunger. No animation, AI, feeding victims,
 * irreversible outcomes, or exposure rules are implied by this component.
 */
UCLASS(ClassGroup=(Gameplay), meta=(BlueprintSpawnableComponent))
class ARCHCITYINDARKNESS_API UACIDHungerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UACIDHungerComponent();

    UPROPERTY(BlueprintAssignable, Category="Survival|Hunger")
    FACIDOnHungerChanged OnHungerChanged;

    UFUNCTION(BlueprintPure, Category="Survival|Hunger")
    float GetHunger() const { return Hunger; }

    /** Rejects non-finite values; otherwise clamps to [0,100]. */
    UFUNCTION(BlueprintCallable, Category="Survival|Hunger")
    bool SetHunger(float NewValue);

    /** Increases hunger if Amount is finite and strictly positive. */
    UFUNCTION(BlueprintCallable, Category="Survival|Hunger")
    bool AccrueHunger(float Amount);

    /** Reduces hunger if Nourishment is finite and strictly positive. */
    UFUNCTION(BlueprintCallable, Category="Survival|Hunger")
    bool Feed(float Nourishment);

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Survival|Hunger", meta=(AllowPrivateAccess="true"))
    float Hunger = 25.0f;
};
