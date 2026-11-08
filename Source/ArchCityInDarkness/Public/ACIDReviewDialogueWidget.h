#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Components/Button.h"
#include "ACIDReviewDialogueWidget.generated.h"

class AACIDPreludeCharacter;
class AACIDPreludeInteractable;
class UTextBlock;
class UVerticalBox;
class UACIDReviewDialogueWidget;
class FJsonObject;

/** Single captioned option. Every button owns its exact source-dialogue choice ID. */
UCLASS()
class ARCHCITYINDARKNESS_API UACIDReviewDialogueChoiceButton : public UButton
{
    GENERATED_BODY()

public:
    void BindReviewChoice(UACIDReviewDialogueWidget* InPanel, FName InChoiceId);

private:
    TWeakObjectPtr<UACIDReviewDialogueWidget> ReviewPanel;
    FName ChoiceId = NAME_None;

    UFUNCTION()
    void OnReviewChoiceClicked();
};

/**
 * Disposable caption-first M005 dialogue display constructed from C++ widgets.
 * Reads source JSON from the local project checkout; not packaged/canon-ready.
 * Unreal compilation, UI interaction, focus and visual legibility are NOT VERIFIED.
 */
UCLASS()
class ARCHCITYINDARKNESS_API UACIDReviewDialogueWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    /** Call after AddToViewport; only operates on a verified active NPC/prop session. */
    bool OpenFor(AACIDPreludeCharacter* Character, AACIDPreludeInteractable* Marker);
    void SelectSourceChoice(FName ChoiceId);
    void CloseReviewDialogue();

protected:
    virtual void NativeConstruct() override;
    virtual FReply NativeOnKeyDown(const FGeometry& InGeometry, const FKeyEvent& InKeyEvent) override;

private:
    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> HeaderText;

    UPROPERTY(Transient)
    TObjectPtr<UTextBlock> LineText;

    UPROPERTY(Transient)
    TObjectPtr<UVerticalBox> ChoiceList;

    TWeakObjectPtr<AACIDPreludeCharacter> Player;
    TWeakObjectPtr<AACIDPreludeInteractable> Anchor;
    TSharedPtr<FJsonObject> DialogueGraph;
    FString CurrentNodeId;

    bool LoadLocalReviewGraph();
    TSharedPtr<FJsonObject> FindSourceNode(const FString& NodeId) const;
    bool ShowSourceNode(const FString& NodeId);
    static FString ReadString(const TSharedPtr<FJsonObject>& Object, const TCHAR* Key);
};
