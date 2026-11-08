using UnrealBuildTool;

public class ArchCityInDarkness : ModuleRules
{
    public ArchCityInDarkness(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "InputCore", "UMG", "Slate", "SlateCore", "Json" });
    }
}
