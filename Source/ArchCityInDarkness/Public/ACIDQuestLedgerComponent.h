#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ACIDQuestLedgerComponent.generated.h"

/** Only the original Glassbend source prototype is supported in milestone M002. */
UENUM(BlueprintType)
enum class EACIDQuestPhase : uint8
{
    Investigating,
    Resolved
};

UENUM(BlueprintType)
enum class EACIDResolutionRoute : uint8
{
    None,
    Dialogue,
    Stealth,
    Confrontation
};

/** Small explicit data contract; no UACIDSaveGame implementation is claimed. */
USTRUCT(BlueprintType)
struct ARCHCITYINDARKNESS_API FACIDQuestSnapshot
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 SchemaVersion = 1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    EACIDQuestPhase Phase = EACIDQuestPhase::Investigating;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    EACIDResolutionRoute Route = EACIDResolutionRoute::None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    TArray<FName> Clues;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    FName EvidenceId = NAME_None;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 MaraTrust = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Quest")
    int32 PublicExposure = 0;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FACIDOnQuestResolved, EACIDResolutionRoute, Route);

/**
 * One-quest prototype: three independent clue routes, exactly one resolution.
 * All functions are deterministic, non-ticking and reject unsupported inputs.
 * Actor placement, dialogue UI, gameplay events and disk persistence are not implemented.
 */
UCLASS(ClassGroup=(Gameplay), meta=(BlueprintSpawnableComponent))
class ARCHCITYINDARKNESS_API UACIDQuestLedgerComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UACIDQuestLedgerComponent();

    UPROPERTY(BlueprintAssignable, Category="Quest")
    FACIDOnQuestResolved OnQuestResolved;

    UFUNCTION(BlueprintCallable, Category="Quest")
    bool DiscoverClue(FName ClueId);

    UFUNCTION(BlueprintPure, Category="Quest")
    bool HasClue(FName ClueId) const;

    UFUNCTION(BlueprintCallable, Category="Quest")
    bool TryResolve(EACIDResolutionRoute SelectedRoute);

    UFUNCTION(BlueprintPure, Category="Quest")
    FACIDQuestSnapshot ExportSnapshot() const;

    /** Restores only into a new pristine component after strict validation. */
    UFUNCTION(BlueprintCallable, Category="Quest")
    bool TryRestoreSnapshot(const FACIDQuestSnapshot& Candidate);

    UFUNCTION(BlueprintPure, Category="Quest")
    EACIDQuestPhase GetPhase() const { return Phase; }

    UFUNCTION(BlueprintPure, Category="Quest")
    EACIDResolutionRoute GetRoute() const { return Route; }

    UFUNCTION(BlueprintPure, Category="Quest")
    int32 GetMaraTrust() const { return MaraTrust; }

    UFUNCTION(BlueprintPure, Category="Quest")
    int32 GetPublicExposure() const { return PublicExposure; }

private:
    static bool IsKnownClue(FName ClueId);
    static bool RequirementsSatisfied(EACIDResolutionRoute SelectedRoute, const TSet<FName>& OwnedClues);
    static bool ValidateSnapshot(const FACIDQuestSnapshot& Candidate);
    static FName EvidenceFor(EACIDResolutionRoute SelectedRoute);

    UPROPERTY(VisibleAnywhere, Category="Quest")
    EACIDQuestPhase Phase = EACIDQuestPhase::Investigating;

    UPROPERTY(VisibleAnywhere, Category="Quest")
    EACIDResolutionRoute Route = EACIDResolutionRoute::None;

    UPROPERTY()
    TSet<FName> DiscoveredClues;

    UPROPERTY(VisibleAnywhere, Category="Quest")
    FName EvidenceId = NAME_None;

    UPROPERTY(VisibleAnywhere, Category="Quest")
    int32 MaraTrust = 0;

    UPROPERTY(VisibleAnywhere, Category="Quest")
    int32 PublicExposure = 0;
};
