#include "ACIDPreludeCharacter.h"
#include "ACIDPreludeInteractable.h"
#include "ACIDHungerComponent.h"
#include "ACIDQuestLedgerComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "GameFramework/CharacterMovementComponent.h"

AACIDPreludeCharacter::AACIDPreludeCharacter()
{
    PrimaryActorTick.bCanEverTick = false;
    GetCapsuleComponent()->InitCapsuleSize(42.0f, 88.0f);
    bUseControllerRotationYaw = true;
    GetCharacterMovement()->bOrientRotationToMovement = false;
    GetCharacterMovement()->MaxWalkSpeed = 420.0f;

    ViewCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("PreludeCamera"));
    ViewCamera->SetupAttachment(GetCapsuleComponent());
    ViewCamera->SetRelativeLocation(FVector(0, 0, 58));
    ViewCamera->bUsePawnControlRotation = true;

    Hunger = CreateDefaultSubobject<UACIDHungerComponent>(TEXT("Hunger"));
    QuestLedger = CreateDefaultSubobject<UACIDQuestLedgerComponent>(TEXT("GlassbendQuest"));
}

void AACIDPreludeCharacter::BeginPlay()
{
    Super::BeginPlay();
    PrintReviewText(TEXT("ARCH CITY IN DARKNESS | GLASSBEND, AFTER MIDNIGHT\n"
        "Rain over the shelter. A worker is missing and an hour is unaccounted for.\n"
        "WASD move | Mouse look | E clue | F talk | Enter confirm | Escape cancel | Tab status.\n"
        "Review-only greybox, original provisional story. No forced feeding."));
}

void AACIDPreludeCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    check(PlayerInputComponent);
    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &AACIDPreludeCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &AACIDPreludeCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &AACIDPreludeCharacter::LookYaw);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &AACIDPreludeCharacter::LookPitch);
    PlayerInputComponent->BindAction(TEXT("Interact"), IE_Pressed, this, &AACIDPreludeCharacter::Interact);
    PlayerInputComponent->BindAction(TEXT("QuestStatus"), IE_Pressed, this, &AACIDPreludeCharacter::ShowStatus);
    PlayerInputComponent->BindAction(TEXT("ReviewDialogueOpen"), IE_Pressed, this, &AACIDPreludeCharacter::OpenReviewDialogue);
    PlayerInputComponent->BindAction(TEXT("ReviewDialogueConfirm"), IE_Pressed, this, &AACIDPreludeCharacter::ConfirmReviewDialogue);
    PlayerInputComponent->BindAction(TEXT("ReviewDialogueCancel"), IE_Pressed, this, &AACIDPreludeCharacter::CancelReviewDialogue);
}

void AACIDPreludeCharacter::MoveForward(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
        AddMovementInput(FRotationMatrix(FRotator(0, Controller->GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::X), Value);
}

void AACIDPreludeCharacter::MoveRight(float Value)
{
    if (Controller && !FMath::IsNearlyZero(Value))
        AddMovementInput(FRotationMatrix(FRotator(0, Controller->GetControlRotation().Yaw, 0)).GetUnitAxis(EAxis::Y), Value);
}

void AACIDPreludeCharacter::LookYaw(float Value)
{
    AddControllerYawInput(Value);
}

void AACIDPreludeCharacter::LookPitch(float Value)
{
    AddControllerPitchInput(Value);
}

void AACIDPreludeCharacter::Interact()
{
    if (!IsLocallyControlled() || !GetWorld()) return;
    // Any other world interaction cancels a pending NPC confirmation.
    ActiveReviewDialogueMarker.Reset();
    AACIDPreludeInteractable* Nearest = nullptr;
    float BestDistance = FMath::Square(275.0f);
    for (TActorIterator<AACIDPreludeInteractable> It(GetWorld()); It; ++It)
    {
        const float Distance = FVector::DistSquared(GetActorLocation(), It->GetActorLocation());
        if (Distance < BestDistance)
        {
            BestDistance = Distance;
            Nearest = *It;
        }
    }
    if (!IsValid(Nearest))
    {
        PrintReviewText(TEXT("No review interaction in range. Move near a marker."));
        return;
    }
    const FString AnchorLabel = Nearest->AnchorId.ToString();
    if (!Nearest->TryInteract(this))
    {
        PrintReviewText(FString::Printf(TEXT("%s: blocked, already collected, or requires more evidence."), *AnchorLabel));
        return;
    }
    PrintReviewText(FString::Printf(TEXT("Interacted at %s. Quest state updated."), *AnchorLabel));
    ShowStatus();
}


bool AACIDPreludeCharacter::IsReviewDialogueActiveFor(
    const AACIDPreludeInteractable* Marker) const
{
    return IsValid(Marker) && ActiveReviewDialogueMarker.Get() == Marker;
}

void AACIDPreludeCharacter::OpenReviewDialogue()
{
    ActiveReviewDialogueMarker.Reset();
    if (!IsLocallyControlled() || !GetWorld() || !IsValid(QuestLedger) ||
        QuestLedger->GetPhase() != EACIDQuestPhase::Investigating)
    {
        PrintReviewText(TEXT("Review dialogue cannot open in this state."));
        return;
    }

    AACIDPreludeInteractable* Nearest = nullptr;
    float BestDistance = FMath::Square(275.0f);
    for (TActorIterator<AACIDPreludeInteractable> It(GetWorld()); It; ++It)
    {
        if (!It->IsReviewDialogueNPC()) continue;
        const float Distance = FVector::DistSquared(GetActorLocation(), It->GetActorLocation());
        if (Distance < BestDistance)
        {
            BestDistance = Distance;
            Nearest = *It;
        }
    }
    if (!IsValid(Nearest) || !Nearest->CanReviewInteract(this))
    {
        PrintReviewText(TEXT("No visible NPC within 2.75m for review dialogue."));
        return;
    }
    ActiveReviewDialogueMarker = Nearest;
    const FName Anchor = Nearest->AnchorId;
    const TCHAR* Option = Anchor == TEXT("mara_vale")
        ? TEXT("Request a privacy-safe redacted record from Mara")
        : Anchor == TEXT("nico_bell")
            ? TEXT("Observe Nico's transfer without confrontation")
            : TEXT("Present the annex evidence to Etta without violence");
    PrintReviewText(FString::Printf(
        TEXT("ORIGINAL GLASSBEND REVIEW | %s\n%s\nEnter: explicitly attempt this choice | Escape: cancel\n")
        TEXT("This is a diagnostic prompt, NOT the approved M005 dialogue UI."),
        *Anchor.ToString(), Option));
}

void AACIDPreludeCharacter::ConfirmReviewDialogue()
{
    AACIDPreludeInteractable* Marker = ActiveReviewDialogueMarker.Get();
    if (!IsLocallyControlled() || !IsValid(Marker))
    {
        ActiveReviewDialogueMarker.Reset();
        PrintReviewText(TEXT("No active review dialogue choice to confirm."));
        return;
    }
    // No action ID is accepted from raw input: only a fixed choice on the
    // session-bound NPC, with all world gates rechecked at actual dispatch.
    const bool bCommitted = Marker->TryCommitReviewChoice(this, Marker->GetReviewChoiceId());
    ActiveReviewDialogueMarker.Reset();  // single use, including failed attempts
    if (!bCommitted)
    {
        PrintReviewText(TEXT("Choice rejected: evidence, range, sight or quest state invalid."));
        return;
    }
    PrintReviewText(TEXT("Explicit review choice resolved. No forced feeding."));
    ShowStatus();
}

void AACIDPreludeCharacter::CancelReviewDialogue()
{
    ActiveReviewDialogueMarker.Reset();
    PrintReviewText(TEXT("Review dialogue canceled. No quest outcome selected."));
}

void AACIDPreludeCharacter::ShowStatus()
{
    if (!IsValid(QuestLedger) || !IsValid(Hunger)) return;
    const FACIDQuestSnapshot Snapshot = QuestLedger->ExportSnapshot();
    FString Clues;
    for (const FName& Clue : Snapshot.Clues)
    {
        if (!Clues.IsEmpty()) Clues += TEXT(", ");
        Clues += Clue.ToString();
    }
    if (Clues.IsEmpty()) Clues = TEXT("none");
    const FString Status = FString::Printf(
        TEXT("THE UNCLAIMED HOUR | %s\nClues: %s | Hunger: %.0f | Trust: %d | Exposure: %d\nEvidence: %s"),
        Snapshot.Phase == EACIDQuestPhase::Resolved ? TEXT("RESOLVED") : TEXT("INVESTIGATING"),
        *Clues, Hunger->GetHunger(), Snapshot.MaraTrust, Snapshot.PublicExposure, *Snapshot.EvidenceId.ToString());
    PrintReviewText(Status);
}

void AACIDPreludeCharacter::PrintReviewText(const FString& Message) const
{
    UE_LOG(LogTemp, Display, TEXT("[ArchCity Prelude REVIEW] %s"), *Message);
    if (GEngine)
    {
        GEngine->AddOnScreenDebugMessage(-1, 12.0f, FColor::White, Message);
    }
}
