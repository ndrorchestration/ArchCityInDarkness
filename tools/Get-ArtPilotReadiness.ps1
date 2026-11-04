# ART-PILOT-001 read-only local environment inventory.
# This script does NOT start/stop applications, install plugins, copy assets,
# update Unreal projects, download data, or write to disk.
[CmdletBinding()]
param(
    [ValidateRange(1, 1000)]
    [double] $MinimumFreeGiB = 15
)

$ErrorActionPreference = 'Stop'

function Find-ExistingFiles {
    param([string[]] $Candidates)
    @($Candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf })
}

$pf = $env:ProgramFiles
if (-not $pf) { $pf = 'C:\Program Files' }
$driveName = $env:SystemDrive
if (-not $driveName) { $driveName = 'C:' }

$dazCandidates = @(
    (Join-Path $pf 'DAZ 3D\DAZStudio6\DAZStudio.exe'),
    (Join-Path $pf 'DAZ 3D\DAZStudio4\DAZStudio.exe'),
    (Join-Path $pf 'Daz 3D\DAZStudio6\DAZStudio.exe')
)
$unrealCandidates = @(
    (Join-Path $pf 'Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe')
)
$dazBridgeCandidates = @(
    (Join-Path $pf 'DAZ 3D\DAZStudio6\plugins\dzunrealbridge.dll'),
    (Join-Path $pf 'DAZ 3D\DAZStudio4\plugins\dzunrealbridge.dll'),
    (Join-Path $pf 'Daz 3D\DAZStudio6\plugins\dzunrealbridge.dll')
)
$unrealBridgeCandidates = @(
    (Join-Path $pf 'Epic Games\UE_5.8\Engine\Plugins\Marketplace\DazToUnreal\DazToUnreal.uplugin'),
    (Join-Path $pf 'Epic Games\UE_5.8\Engine\Plugins\DazToUnreal\DazToUnreal.uplugin')
)

$dazFound = @(Find-ExistingFiles $dazCandidates)
$unrealFound = @(Find-ExistingFiles $unrealCandidates)
$dazBridges = @(Find-ExistingFiles $dazBridgeCandidates)
$unrealBridges = @(Find-ExistingFiles $unrealBridgeCandidates)

$processNames = @(
    Get-Process -ErrorAction SilentlyContinue |
        Where-Object {
            $_.ProcessName -in @('DAZ3DIM', 'DAZ3DIMHelper', 'DAZStudio', 'UnrealEditor', 'LiveCodingConsole')
        } |
        ForEach-Object { $_.ProcessName }
)
$installerActive = ('DAZ3DIM' -in $processNames) -or ('DAZ3DIMHelper' -in $processNames)

$drive = Get-CimInstance Win32_LogicalDisk -Filter ("DeviceID='" + $driveName + "'")
if (-not $drive) { throw "Could not read system drive free space" }
$freeGiB = [math]::Round($drive.FreeSpace / 1GB, 2)

$blockers = @()
if ($freeGiB -lt $MinimumFreeGiB) { $blockers += 'DISK_HEADROOM_BELOW_REVIEW_POLICY' }
if ($installerActive) { $blockers += 'INSTALL_MANAGER_RUNNING_COMPLETION_UNVERIFIED' }
if ($dazFound.Count -eq 0) { $blockers += 'DAZ_STUDIO_EXECUTABLE_NOT_FOUND_IN_STANDARD_PATHS' }
if ($unrealFound.Count -eq 0) { $blockers += 'UE_5_8_EXECUTABLE_NOT_FOUND_IN_STANDARD_PATHS' }
if ($dazBridges.Count -eq 0 -or $unrealBridges.Count -eq 0) {
    $blockers += 'BRIDGE_NOT_VERIFIED_IN_STANDARD_PATHS'
}
$blockers += 'ASSET_RIGHTS_AND_ENGINE_IMPORT_STILL_REQUIRE_REVIEW'
$blockers += 'CREATOR_ART_APPROVAL_AND_GPU_CAPTURES_MISSING'

$result = [ordered]@{
    schema_version = 1
    pilot_id = 'ART-PILOT-001'
    read_only = $true
    does_not_start_or_stop_programs = $true
    environment_verified_at_utc = (Get-Date).ToUniversalTime().ToString('o')
    system_drive = $driveName
    free_gib = $freeGiB
    minimum_free_gib_policy = $MinimumFreeGiB
    installer_process_visible = $installerActive
    checked_process_names = $processNames
    daz_studio_executables_in_standard_paths = $dazFound
    unreal_5_8_executables_in_standard_paths = $unrealFound
    daz_bridge_files_in_standard_paths = $dazBridges
    unreal_bridge_plugins_in_standard_paths = $unrealBridges
    compatibility_verified = $false
    license_verified = $false
    native_import_verified = $false
    production_import_authorized = $false
    blockers = $blockers
    notes = @(
        'Found files are not proof an application launches, a plug-in is compatible, or assets have game-distribution rights.',
        'Standard path checks are not an exhaustive filesystem inventory.',
        'Running Install Manager does not prove a download is currently active or complete.',
        'This script is strictly observational. Review blockers before any installation, conversion, or rendering.'
    )
}
$result | ConvertTo-Json -Depth 6
