# Native build attempt log — public-safe summary

**State: neither native attempt passed.** This file records reproducible blockers, not a compilation success.

| Attempt | UTC time | Exact commit | Phase reached | Result |
| --- | --- | --- | --- | --- |
| A | 2026-11-03 01:38 | `80af41b88af9545bd2dd6229c82ab84264f664c7` | UnrealBuildTool evaluated targets | FAILED (exit 6): V5 warning defaults incompatible with shared Unreal Editor |
| B | 2026-11-03 01:40 | `fb2dd642ae9e26988229eb0a689aaba940c1988f` | UnrealHeaderTool produced four generated files | FAILED (exit 6): Editor Live Coding active, external build blocked |

The source fix for attempt A replaced V5 with V7 and explicitly set Unreal 5.8 include order in the Game and Editor targets. Both attempts were run on the authorized Windows workstation in a **separate, clean, non-main checkout**. Full build output and run summary files remain locally in ignored `Saved/ArchCityVerification` subdirectories. The native hunger test did not execute in either attempt.

The editor was left open intentionally to avoid discarding unsaved work. The native runner now checks for active Editor/Live Coding processes before building and fails closed without stopping any process.

## Next native gate
After the user saves and closes Unreal Editor normally, rerun `tools/Verify-UnrealNative.ps1` from the isolated checkout. Capture the exact source commit, complete build result and test report; preserve FAIL_CLOSED if any evidence is missing.

See [issue #2](https://github.com/ndrorchestration/ArchCityInDarkness/issues/2) for the current blocker. No game assets, TSTSS source, or player/chronicle correspondence are included here.
