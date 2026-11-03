using UnrealBuildTool;

public class ArchCityInDarknessTarget : TargetRules
{
    public ArchCityInDarknessTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V7;
        IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
        ExtraModuleNames.Add("ArchCityInDarkness");
    }
}
