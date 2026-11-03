using UnrealBuildTool;
using System.Collections.Generic;

public class ArchCityInDarknessEditorTarget : TargetRules
{
    public ArchCityInDarknessEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.V5;
        ExtraModuleNames.Add("ArchCityInDarkness");
    }
}
