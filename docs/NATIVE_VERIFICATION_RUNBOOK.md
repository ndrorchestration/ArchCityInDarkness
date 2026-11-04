# Native Unreal 5.8.4 verification gate

**State: native build, Editor launch, runtime gameplay, and native test remain UNVERIFIED.**

## Already supported
- Initial source-only GitHub structure CI pass was recorded at commit 2818276deb72b7b0323425da4319df6dc53fc2df, run 41557541809.
- This feature-branch update adds an automated fail-closed Windows proof capture path. Check the current head's CI status independently.
- Portable report-parser fixtures do **not** constitute an executed Unreal test.

## Windows review (isolated non-main clean feature-branch checkout)
Required: PowerShell 7+, Git, Python 3, Unreal 5.8.4, compatible Visual Studio C++ build tools.

From repository root:

~~~powershell
python tools/check_project_structure.py
python -m unittest discover -s tools/tests -p 'test_*.py' -v
pwsh -NoProfile -File tools/Verify-UnrealNative.ps1 -EngineRoot "C:\Program Files\Epic Games\UE_5.8"
~~~

The script first checks for active Unreal Editor or Live Coding processes. If either is present, it fails closed with a saved summary and **does not terminate any process, run a build, or disturb unsaved work**. Save and close the Editor normally before rerunning. This conservative guard may also detect an Editor opened for another project.

The script checks Engine/Build/Build.version and compiles ArchCityInDarknessEditor for Win64 Development. By default it executes only `ArchCityInDarkness.Survival.Hunger.Contract` via UnrealEditor-Cmd. It creates an ignored `Saved/ArchCityVerification/` run directory with the build log, individual test reports and editor logs, and a summary. A report is valid only for its exact named test; results cannot be shared across contracts.

**M002 only, after M001-B is independently verified at the reviewed M001 commit:** in a fresh, clean M002 feature-branch checkout with Unreal Editor / Live Coding closed normally, run the same script with both tests explicitly selected:

~~~powershell
& .\tools\Verify-UnrealNative.ps1 -EngineRoot 'C:\Program Files\Epic Games\UE_5.8' -Tests `
    'ArchCityInDarkness.Survival.Hunger.Contract', `
    'ArchCityInDarkness.Quest.Glassbend.Contract'
~~~

The script compiles once, then launches a distinct UnrealEditor-Cmd process for each requested contract. The reports are separated under `AutomationReport/Hunger` and `AutomationReport/Quest`; each has a matching `Editor-Hunger.log` or `Editor-Quest.log`. `summary.json` records the exact Git head, requested tests, per-test results, and overall fail-closed outcome. It is not acceptable to use a portable test, an old report, a different branch, or a test of one contract to substantiate the other. Any failed test blocks an overall PASS.

**PASS** requires successful native compile and Editor process exit, exactly one named test in index.json with state Success, zero failed/notRun counts, and the matching successful completion event plus TEST COMPLETE exit-code-0 marker in native logs. Missing or contradictory evidence is **FAIL_CLOSED**, even if process exit is zero.

The runner does not install software, alter other repositories, merge PRs, create maps, package games, or promote assets. Review evidence and remove personal local paths before sharing in the public GitHub PR. If native verification fails, keep the relevant draft PR open and document the failed gate in issue #2 (hunger) or issue #5 (quest). Never force-close user Editor processes.

## What a PASS does not establish
No playable map, quest, player controls, save/load, art fidelity, or originality/trademark clearance is established by this unit test.

## References
Epic's Unreal 5.8 docs:
- https://dev.epicgames.com/documentation/unreal-engine/run-automation-tests-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/review-test-results-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/building-unreal-engine-from-source

## Evidence and reversibility
GitHub source changes can be reverted independently. Until the Windows runner actually executes, native compile/test status is NOT_VERIFIED. No generated logs are committed.
