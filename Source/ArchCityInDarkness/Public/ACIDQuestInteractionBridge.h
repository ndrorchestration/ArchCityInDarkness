#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ACIDQuestInteractionBridge.generated.h"

class UACIDQuestLedgerComponent;

/**
 * Noncanonical source-only adapter between explicit action IDs and the Glassbend quest ledger.
 * The caller MUST enforce real player proximity, line of sight, actor identity and input
 * ownership before invoking this library. None of those world checks exist in this prototype.
 */
UCLASS()
class ARCHCITYINDARKNESS_API UACIDQuestInteractionBridge : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /** Returns false for invalid actions, null ledger or failed quest prerequisites. */
    UFUNCTION(BlueprintCallable, Category="Glassbend|Prototype")
    static bool TryApplyAction(UACIDQuestLedgerComponent* QuestLedger, FName ActionId);
};
