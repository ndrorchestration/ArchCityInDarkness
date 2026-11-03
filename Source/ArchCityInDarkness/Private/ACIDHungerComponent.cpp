#include "ACIDHungerComponent.h"

UACIDHungerComponent::UACIDHungerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UACIDHungerComponent::SetHunger(float NewValue)
{
    if (!FMath::IsFinite(NewValue))
    {
        return false;
    }

    const float Clamped = FMath::Clamp(NewValue, 0.0f, 100.0f);
    if (!FMath::IsNearlyEqual(Hunger, Clamped))
    {
        const float Previous = Hunger;
        Hunger = Clamped;
        OnHungerChanged.Broadcast(Previous, Hunger);
    }
    return true;
}

bool UACIDHungerComponent::AccrueHunger(float Amount)
{
    if (!FMath::IsFinite(Amount) || Amount <= 0.0f)
    {
        return false;
    }
    return SetHunger(Hunger + Amount);
}

bool UACIDHungerComponent::Feed(float Nourishment)
{
    if (!FMath::IsFinite(Nourishment) || Nourishment <= 0.0f)
    {
        return false;
    }
    return SetHunger(Hunger - Nourishment);
}
