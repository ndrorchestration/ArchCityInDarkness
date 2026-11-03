#if WITH_DEV_AUTOMATION_TESTS

#include "ACIDHungerComponent.h"
#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FACIDHungerContractTest,
    "ArchCityInDarkness.Survival.Hunger.Contract",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FACIDHungerContractTest::RunTest(const FString& Parameters)
{
    UACIDHungerComponent* Component = NewObject<UACIDHungerComponent>();
    if (!TestNotNull(TEXT("Can construct hunger component"), Component))
    {
        return false;
    }

    TestEqual(TEXT("Starts at configured prototype hunger"), Component->GetHunger(), 25.0f);
    TestTrue(TEXT("Valid hunger increase"), Component->AccrueHunger(10.0f));
    TestEqual(TEXT("Hunger increased"), Component->GetHunger(), 35.0f);
    TestTrue(TEXT("Valid feed"), Component->Feed(5.0f));
    TestEqual(TEXT("Feeding decreased hunger"), Component->GetHunger(), 30.0f);

    TestTrue(TEXT("Upper clamp accepts an out-of-range finite value"), Component->SetHunger(150.0f));
    TestEqual(TEXT("Hunger clamped high"), Component->GetHunger(), 100.0f);
    TestTrue(TEXT("Lower clamp accepts an out-of-range finite value"), Component->SetHunger(-10.0f));
    TestEqual(TEXT("Hunger clamped low"), Component->GetHunger(), 0.0f);

    TestFalse(TEXT("Negative feeding rejected"), Component->Feed(-1.0f));
    TestFalse(TEXT("Zero hunger accrual rejected"), Component->AccrueHunger(0.0f));
    TestEqual(TEXT("Rejected actions leave state unchanged"), Component->GetHunger(), 0.0f);
    return true;
}

#endif // WITH_DEV_AUTOMATION_TESTS
