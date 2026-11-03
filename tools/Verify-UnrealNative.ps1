#Requires -Version 7.0
<# Runs only on a Windows Unreal machine; never merges or releases. #>
[CmdletBinding()]
param(
    [string]$EngineRoot = 'C:\Program Files\Epic Games\UE_5.8',
    [string]$ProjectRoot = (Join-Path $PSScriptRoot '..'),
    [string]$PythonExecutable = 'python'
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
$RunId = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ') + '-' + [guid]::NewGuid().ToString('N').Substring(0, 8)
$Output = Join-Path $ProjectRoot "Saved\ArchCityVerification\$RunId"
$Report = Join-Path $Output 'AutomationReport'
New-Item -ItemType Directory -Path $Report -Force | Out-Null
$BuildLog = Join-Path $Output 'Build.log'
$EditorLog = Join-Path $Output 'Editor.log'
$EditorStdout = Join-Path $Output 'Editor-stdout.log'
$SummaryPath = Join-Path $Output 'summary.json'
$Summary = [ordered]@{
    timestamp_utc = (Get-Date).ToUniversalTime().ToString('o')
    git_head = $Head
    branch = $Branch
    ue_version = '5.8.4'
    build = 'NOT_RUN'
    test = 'NOT_RUN'
    outcome = 'FAIL_CLOSED'
    error = $null
}
try {
    $Summary.build = 'STARTED'
    & $Build 'ArchCityInDarknessEditor' 'Win64' 'Development' $Project '-WaitMutex' '-NoHotReload' 2>&1 | Tee-Object -FilePath $BuildLog
    $BuildExit = $LASTEXITCODE
    if ($BuildExit -ne 0) { throw "Build.bat returned $BuildExit" }
    $Summary.build = 'PASS'
    $Summary.test = 'STARTED'
    $Args = @(
        $Project, '-unattended', '-nop4', '-nosplash', '-NoSound', '-NullRHI',
        "-ReportExportPath=$Report", '-ExecCmds=Automation RunTest ArchCityInDarkness.Survival.Hunger.Contract;Quit',
        "-abslog=$EditorLog"
    )
    & $Editor @Args 2>&1 | Tee-Object -FilePath $EditorStdout
    $EditorExit = $LASTEXITCODE
    if ($EditorExit -ne 0) { throw "UnrealEditor-Cmd returned $EditorExit" }
    & $PythonExecutable $Verifier '--report' (Join-Path $Report 'index.json') '--log' $EditorLog
    if ($LASTEXITCODE -ne 0) { throw 'Native automation evidence failed validation' }
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
