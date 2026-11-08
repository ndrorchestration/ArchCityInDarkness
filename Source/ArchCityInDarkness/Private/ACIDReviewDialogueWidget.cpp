#include "ACIDReviewDialogueWidget.h"

#include "ACIDPreludeCharacter.h"
#include "ACIDPreludeInteractable.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Dom/JsonObject.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

void UACIDReviewDialogueChoiceButton::BindReviewChoice(
    UACIDReviewDialogueWidget* InPanel, FName InChoiceId)
{
    ReviewPanel = InPanel;
    ChoiceId = InChoiceId;
    OnClicked.AddDynamic(this, &UACIDReviewDialogueChoiceButton::OnReviewChoiceClicked);
}

void UACIDReviewDialogueChoiceButton::OnReviewChoiceClicked()
{
    if (UACIDReviewDialogueWidget* Panel = ReviewPanel.Get())
    {
        Panel->SelectSourceChoice(ChoiceId);
    }
}

void UACIDReviewDialogueWidget::NativeConstruct()
{
    Super::NativeConstruct();
    bIsFocusable = true;

    UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass());
    WidgetTree->RootWidget = Canvas;

    UBorder* Frame = WidgetTree->ConstructWidget<UBorder>(UBorder::StaticClass());
    Frame->SetBrushColor(FLinearColor(0.035f, 0.045f, 0.07f, 0.97f));
    UCanvasPanelSlot* FrameSlot = Canvas->AddChildToCanvas(Frame);
    FrameSlot->SetAnchors(FAnchors(0.10f, 0.49f, 0.90f, 0.94f));
    FrameSlot->SetOffsets(FMargin(0, 0, 0, 0));

    UVerticalBox* Column = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
    Frame->SetContent(Column);

    HeaderText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    HeaderText->SetColorAndOpacity(FSlateColor(FLinearColor(0.91f, 0.78f, 0.54f, 1)));
    FSlateFontInfo HeadingFont = HeaderText->GetFont();
    HeadingFont.Size = 25;
    HeaderText->SetFont(HeadingFont);
    Column->AddChildToVerticalBox(HeaderText);

    LineText = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
    LineText->SetColorAndOpacity(FSlateColor(FLinearColor::White));
    LineText->SetAutoWrapText(true);
    FSlateFontInfo LineFont = LineText->GetFont();
    LineFont.Size = 23;
    LineText->SetFont(LineFont);
    Column->AddChildToVerticalBox(LineText);

    ChoiceList = WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass());
    Column->AddChildToVerticalBox(ChoiceList);
}

FString UACIDReviewDialogueWidget::ReadString(
    const TSharedPtr<FJsonObject>& Object, const TCHAR* Key)
{
    FString Out;
    if (Object.IsValid())
    {
        Object->TryGetStringField(Key, Out);
    }
    return Out;
}

bool UACIDReviewDialogueWidget::LoadLocalReviewGraph()
{
    const FString Path = FPaths::Combine(
        FPaths::ProjectDir(), TEXT("Prototypes"), TEXT("Glassbend"),
        TEXT("dialogue_v1.json"));
    FString Json;
    if (!FFileHelper::LoadFileToString(Json, *Path))
    {
        UE_LOG(LogTemp, Warning, TEXT("[ArchCity M011 REVIEW] Missing local source JSON: %s"), *Path);
        return false;
    }
    TSharedPtr<FJsonObject> Loaded;
    if (!FJsonSerializer::Deserialize(TJsonReaderFactory<>::Create(Json), Loaded) ||
        !Loaded.IsValid() ||
        ReadString(Loaded, TEXT("status")) != TEXT("PROTOTYPE_NOT_CANON") ||
        ReadString(Loaded, TEXT("quest_id")) != TEXT("the_unclaimed_hour") ||
        ReadString(Loaded, TEXT("layout_id")) != TEXT("glassbend_greybox_v1") ||
        ReadString(Loaded, TEXT("interaction_model")) != TEXT("EXPLICIT_ACTION_IDS_ONLY"))
    {
        UE_LOG(LogTemp, Warning, TEXT("[ArchCity M011 REVIEW] Dialogue JSON integrity gate failed."));
        return false;
    }
    DialogueGraph = Loaded;
    return true;
}

TSharedPtr<FJsonObject> UACIDReviewDialogueWidget::FindSourceNode(const FString& NodeId) const
{
    if (!DialogueGraph.IsValid())
    {
        return nullptr;
    }
    const TArray<TSharedPtr<FJsonValue>>* Nodes = nullptr;
    if (!DialogueGraph->TryGetArrayField(TEXT("nodes"), Nodes) || Nodes == nullptr)
    {
        return nullptr;
    }
    for (const TSharedPtr<FJsonValue>& Item : *Nodes)
    {
        if (Item.IsValid() && Item->Type == EJson::Object)
        {
            const TSharedPtr<FJsonObject> Node = Item->AsObject();
            if (ReadString(Node, TEXT("id")) == NodeId)
            {
                return Node;
            }
        }
    }
    return nullptr;
}

bool UACIDReviewDialogueWidget::ShowSourceNode(const FString& NodeId)
{
    AACIDPreludeInteractable* Marker = Anchor.Get();
    const TSharedPtr<FJsonObject> Node = FindSourceNode(NodeId);
    if (!IsValid(Marker) || !Node.IsValid() || !IsValid(ChoiceList) ||
        ReadString(Node, TEXT("anchor_id")) != Marker->AnchorId.ToString())
    {
        return false;
    }
    const FString Line = ReadString(Node, TEXT("line"));
    const FString Speaker = ReadString(Node, TEXT("speaker_id"));
    const TArray<TSharedPtr<FJsonValue>>* Options = nullptr;
    if (Line.IsEmpty() || Speaker.IsEmpty() ||
        !Node->TryGetArrayField(TEXT("choices"), Options) || Options == nullptr ||
        Options->IsEmpty())
    {
        return false;
    }

    ChoiceList->ClearChildren();
    HeaderText->SetText(FText::FromString(
        FString::Printf(TEXT("GLASSBEND  |  %s  |  UNAPPROVED REVIEW TEXT"), *Speaker)));
    LineText->SetText(FText::FromString(Line));

    for (const TSharedPtr<FJsonValue>& Option : *Options)
    {
        if (!Option.IsValid() || Option->Type != EJson::Object)
        {
            return false;
        }
        const TSharedPtr<FJsonObject> Choice = Option->AsObject();
        const FString Id = ReadString(Choice, TEXT("id"));
        const FString Caption = ReadString(Choice, TEXT("player_text"));
        if (Id.IsEmpty() || Caption.IsEmpty())
        {
            return false;
        }
        UACIDReviewDialogueChoiceButton* Button =
            WidgetTree->ConstructWidget<UACIDReviewDialogueChoiceButton>(
                UACIDReviewDialogueChoiceButton::StaticClass());
        UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass());
        Label->SetColorAndOpacity(FSlateColor(FLinearColor::White));
        Label->SetAutoWrapText(true);
        FSlateFontInfo ChoiceFont = Label->GetFont();
        ChoiceFont.Size = 21;
        Label->SetFont(ChoiceFont);
        Label->SetText(FText::FromString(TEXT("> ") + Caption));
        Button->AddChild(Label);
        Button->BindReviewChoice(this, FName(*Id));
        ChoiceList->AddChildToVerticalBox(Button);
    }
    CurrentNodeId = NodeId;
    return true;
}

bool UACIDReviewDialogueWidget::OpenFor(
    AACIDPreludeCharacter* Character, AACIDPreludeInteractable* Marker)
{
    if (!IsValid(Character) || !IsValid(Marker) ||
        !Character->IsReviewDialogueActiveFor(Marker) ||
        !Marker->CanReviewInteract(Character) ||
        !LoadLocalReviewGraph())
    {
        return false;
    }

    const TArray<TSharedPtr<FJsonValue>>* Entrypoints = nullptr;
    if (!DialogueGraph->TryGetArrayField(TEXT("entrypoints"), Entrypoints) ||
        Entrypoints == nullptr)
    {
        return false;
    }
    FString EntryNode;
    for (const TSharedPtr<FJsonValue>& Item : *Entrypoints)
    {
        if (!Item.IsValid() || Item->Type != EJson::Object)
        {
            return false;
        }
        const TSharedPtr<FJsonObject> Entry = Item->AsObject();
        if (ReadString(Entry, TEXT("anchor_id")) == Marker->AnchorId.ToString())
        {
            EntryNode = ReadString(Entry, TEXT("node_id"));
            break;
        }
    }
    if (EntryNode.IsEmpty())
    {
        return false;
    }
    Player = Character;
    Anchor = Marker;
    return ShowSourceNode(EntryNode);
}

void UACIDReviewDialogueWidget::SelectSourceChoice(FName ChoiceId)
{
    AACIDPreludeCharacter* Character = Player.Get();
    AACIDPreludeInteractable* Marker = Anchor.Get();
    const TSharedPtr<FJsonObject> Node = FindSourceNode(CurrentNodeId);
    if (!IsValid(Character) || !IsValid(Marker) ||
        !Character->IsReviewDialogueActiveFor(Marker) ||
        !Node.IsValid() || ReadString(Node, TEXT("anchor_id")) != Marker->AnchorId.ToString())
    {
        CloseReviewDialogue();
        return;
    }
    const TArray<TSharedPtr<FJsonValue>>* Choices = nullptr;
    if (!Node->TryGetArrayField(TEXT("choices"), Choices) || Choices == nullptr)
    {
        CloseReviewDialogue();
        return;
    }
    for (const TSharedPtr<FJsonValue>& Value : *Choices)
    {
        if (!Value.IsValid() || Value->Type != EJson::Object)
        {
            CloseReviewDialogue();
            return;
        }
        const TSharedPtr<FJsonObject> Choice = Value->AsObject();
        if (FName(*ReadString(Choice, TEXT("id"))) != ChoiceId)
        {
            continue;
        }
        bool bClose = false;
        if (!Choice->TryGetBoolField(TEXT("close"), bClose))
        {
            CloseReviewDialogue();
            return;
        }
        FString ActionId;
        const bool bHasAction = Choice->TryGetStringField(TEXT("action_id"), ActionId);
        if (bHasAction)
        {
            // Graph node + choice ownership checked above. Actor verifies the
            // exact choice/action pair, active session, range/LOS and quest.
            const FName Expected = AACIDPreludeInteractable::ActionForDialogueChoice(
                Marker->AnchorId, ChoiceId);
            if (Expected.IsNone() || Expected != FName(*ActionId))
            {
                CloseReviewDialogue();
                return;
            }
        }
        if (bClose)
        {
            if (bHasAction)  // Never combine a side effect and closing action.
            {
                CloseReviewDialogue();
                return;
            }
            CloseReviewDialogue();
            return;
        }
        const bool bApplied = !bHasAction ||
            Marker->TryApplyReviewDialogueChoice(Character, ChoiceId);
        const FString Next = ReadString(Choice,
            bApplied ? TEXT("on_success") : TEXT("on_failure"));
        if (Next.IsEmpty() || !ShowSourceNode(Next))
        {
            CloseReviewDialogue();
        }
        return;
    }
    // No injected/unrecognized choice ID is permitted.
    CloseReviewDialogue();
}

FReply UACIDReviewDialogueWidget::NativeOnKeyDown(
    const FGeometry& InGeometry, const FKeyEvent& InKeyEvent)
{
    if (InKeyEvent.GetKey() == EKeys::Escape)
    {
        CloseReviewDialogue();
        return FReply::Handled();
    }
    return Super::NativeOnKeyDown(InGeometry, InKeyEvent);
}

void UACIDReviewDialogueWidget::CloseReviewDialogue()
{
    AACIDPreludeCharacter* Character = Player.Get();
    if (APlayerController* PC = GetOwningPlayer())
    {
        PC->SetInputMode(FInputModeGameOnly());
        PC->bShowMouseCursor = false;
    }
    if (IsValid(Character))
    {
        Character->EndGraphDialogue(this);
    }
    Player.Reset();
    Anchor.Reset();
    RemoveFromParent();
}
