#Requires -Version 7.0
<# Runs only on a Windows Unreal machine; never merges or releases. #>
[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [string]$ProjectRoot = (Join-Path $PSScriptRoot '..'),
    [string]$PythonExecutable = 'python',
    [ValidateSet('ArchCityInDarkness.Survival.Hunger.Contract', 'ArchCityInDarkness.Quest.Glassbend.Contract', 'ArchCityInDarkness.Interaction.Glassbend.Contract', 'ArchCityInDarkness.Prelude.Glassbend.Contract')]
    [string[]]$Tests = @('ArchCityInDarkness.Survival.Hunger.Contract')
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).Path
$Project = Join-Path $ProjectRoot 'ArchCityInDarkness.uproject'
$Build = Join-Path $EngineRoot 'Engine\Build\BatchFiles\Build.bat'
$Editor = Join-Path $EngineRoot 'Engine\Binaries\Win64\UnrealEditor-Cmd.exe'
$VersionPath = Join-Path $EngineRoot 'Engine\Build\Build.version'
$Verifier = Join-Path $ProjectRoot 'tools\verify_automation_report.py'
foreach ($Path in @($Project, $Build, $Editor, $VersionPath, $Verifier)) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing: $Path" }
}
$Version = Get-Content -LiteralPath $VersionPath -Raw | ConvertFrom-Json
if ($Version.MajorVersion -ne 5 -or $Version.MinorVersion -ne 8 -or $Version.PatchVersion -ne 4) {
    throw "Engine version mismatch: expected 5.8.4; found $($Version.MajorVersion).$($Version.MinorVersion).$($Version.PatchVersion)"
}
$Head = (& git -C $ProjectRoot rev-parse HEAD).Trim()
if ($LASTEXITCODE -ne 0) { throw 'Cannot read Git head' }
$Branch = (& git -C $ProjectRoot branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $Branch -eq 'main' -or -not $Branch) { throw 'Run from a named non-main review branch' }
$Dirty = @(& git -C $ProjectRoot status --porcelain)
if ($LASTEXITCODE -ne 0) { throw 'Cannot check Git status' }
if ($Dirty.Count -gt 0) { throw 'Tracked/untracked changes present; make an isolated clean checkout first' }
$RequestedTests = @($Tests | Select-Object -Unique)
if ($RequestedTests.Count -eq 0) { throw 'Specify at least one named contract test' }
$RunId = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$Output = Join-Path $ProjectRoot "Saved\ArchCityVerification\$RunId"
$ReportsRoot = Join-Path $Output 'AutomationReport'
New-Item -ItemType Directory -Path $ReportsRoot -Force | Out-Null
$BuildLog = Join-Path $Output 'Build.log'
$SummaryPath = Join-Path $Output 'summary.json'
$Summary = [ordered]@{
    timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
    git_head = $Head
    branch = $Branch
    ue_version = '5.8.4'
    build = 'NOT_RUN'
    test = 'NOT_RUN'
    requested_tests = @($RequestedTests)
    test_results = [ordered]@{}
    outcome = 'FAIL_CLOSED'
    blocker = $null
    error = $null
}
try {
    # External UnrealBuildTool compilation cannot proceed while Live Coding is attached.
    # Never terminate editors or Live Coding automatically: they can contain unsaved work.
    $BlockingProcesses = @(Get-Process -Name UnrealEditor,LiveCodingConsole -ErrorAction SilentlyContinue)
    if ($BlockingProcesses.Count -gt 0) {
        $Summary.blocker = 'ACTIVE_EDITOR_OR_LIVE_CODING'
        $Names = ($BlockingProcesses | ForEach-Object { "$($_.ProcessName) (PID $($_.Id))" }) -join ', '
        throw "Unsafe to start external Unreal build while $Names is running. Save work and close Unreal Editor normally; no processes were terminated."
    }
    $Summary.build = 'STARTED'
    & $Build 'ArchCityInDarknessEditor' 'Win64' 'Development' $Project '-WaitMutex' '-NoHotReload' 2>&1 | Tee-Object -FilePath $BuildLog
    $BuildExit = $LASTEXITCODE
    if ($BuildExit -ne 0) { throw "Build.bat returned $BuildExit" }
    $Summary.build = 'PASS'
    $Summary.test = 'STARTED'
    # Run each named test in a distinct Editor process and report directory.
    # Do not accept a pass from one test as evidence for another.
    foreach ($TestName in $RequestedTests) {
        $ShortName = switch ($TestName) {
            'ArchCityInDarkness.Survival.Hunger.Contract' { 'Hunger' }
            'ArchCityInDarkness.Quest.Glassbend.Contract' { 'Quest' }
            'ArchCityInDarkness.Interaction.Glassbend.Contract' { 'Interaction' }
            'ArchCityInDarkness.Prelude.Glassbend.Contract' { 'Prelude' }
        }
        $TestReport = Join-Path $ReportsRoot $ShortName
        $TestLog = Join-Path $Output "Editor-$ShortName.log"
        $TestStdout = Join-Path $Output "Editor-$ShortName-stdout.log"
        New-Item -ItemType Directory -Path $TestReport -Force | Out-Null
        $Summary.test_results[$TestName] = 'STARTED'
        $EditorArgs = @(
            $Project, '-unattended', '-nop4', '-nosplash', '-NoSound', '-NullRHI',
            "-ReportExportPath=$TestReport",
            ("-ExecCmds=Automation RunTest {0};Quit" -f $TestName),
            "-abslog=$TestLog"
        )
        & $Editor @EditorArgs 2>&1 | Tee-Object -FilePath $TestStdout
        $EditorExit = $LASTEXITCODE
        if ($EditorExit -ne 0) { throw "$TestName UnrealEditor-Cmd returned $EditorExit" }
        & $PythonExecutable $Verifier '--report' (Join-Path $TestReport 'index.json') '--log' $TestLog '--test' $TestName
        if ($LASTEXITCODE -ne 0) { throw "$TestName native automation evidence failed validation" }
        $Summary.test_results[$TestName] = 'PASS'
    }
    $Summary.test = 'PASS'
    $Summary.outcome = 'PASS'
}
catch {
    $Summary.error = $_.Exception.Message
    throw
}
finally {
    $Summary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $SummaryPath -Encoding utf8
    Write-Host "Verification evidence: $SummaryPath"
}
