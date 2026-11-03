using UnrealBuildTool;
using System.Collections.Generic;

public class ArchCityInDarknessTarget : TargetRules
{
    public ArchCityInDarknessTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        ExtraModuleNames.Add("ArchCityInDarkness");
    }
}
