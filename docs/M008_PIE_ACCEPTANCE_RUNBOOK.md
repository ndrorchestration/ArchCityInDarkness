# M008 — first controlled Glassbend interaction (PIE acceptance runbook)

**Status: DRAFT / PROTOTYPE_NOT_CANON / NATIVE PIE NOT VERIFIED.**
Tracking issue: https://github.com/ndrorchestration/ArchCityInDarkness/issues/23
Base integration: draft PR #22, reviewed at commit bfd10643b939c99bd8e594f4b46c6c4ee939abe1.
No canon, production actor or asset promotion is authorized.

## Purpose

Prove the smallest human-controlled loop in the original fictional
Columbus-inspired Glassbend district: move to the shift_receipt marker, press E,
obtain exactly one intended quest clue, and confirm hunger remains unchanged.
No ending, UMG, disk SaveGame, cinematics or art approval is required for M008.
The first-person pawn is review-only, not approval of a permanent camera design.

## Baseline evidence (not a new run)

PR #22 reports an Unreal 5.8.4 Editor compile, four separate native contract
tests, a NullRHI reopen with five markers, and a six-second headless game
startup on November 5, 2026. None verifies human input, actual PIE quest
interaction or GPU output. At this review Neontic was offline, and no native
execution could be attempted.

## Portable source-only preflight

Run on a clean checkout of the M008 branch:

    python tools/check_m008_source_readiness.py
    python -m unittest discover -s tools/tests -p 'test_*.py' -v
    python tools/check_project_structure.py

The checker looks for expected source-level wiring signatures and the review
map asset. It does not compile the C++ code or verify gameplay.
Its successful outcome must be recorded as SOURCE_PRECHECK_PASS, not PIE_PASS.

## Safe native execution prerequisites

1. Reconnect an authorized Neontic agent. If offline, record
   BLOCKED_DEVICE_OFFLINE and stop. Do not claim a native run.
2. Check RAM, free disk, exact engine version and UnrealEditor/LiveCodingConsole
   processes read-only. Do not terminate, clear caches or alter TSTSS.
3. Work in a clean isolated checkout of the exact reviewed branch commit.
   Record Git head, branch, and clean status. Do not modify main.
4. If the native build must be repeated, user must first safely save and close
   active Unreal Editor/Live Coding. Use the existing fail-closed
   tools/Verify-UnrealNative.ps1 to run Hunger, Quest, Interaction and Prelude
   contracts independently; preserve native logs and reports.
5. Open /Game/ArchCity/Review/Glassbend_Prelude_Greybox in Unreal Editor 5.8.4.
   Confirm actual PIE pawn possession and native GPU output, not just NullRHI.

## Manual acceptance sequence

| Action | Required observation |
| --- | --- |
| Start PIE | AACIDPreludeCharacter possessed; first-person camera renders |
| Move WASD and mouse | Both movement and camera rotation respond, collision sensible |
| Press Tab | Quest phase, clue list and hunger before action visible |
| Press E from beyond 2.75m | Receipt not added |
| Press E with solid obstacle between player and receipt | Receipt not added; obstacle truly intersects visibility ray |
| Walk into unobstructed range and press E | shift_receipt added exactly once, feedback readable |
| Press Tab, then E at same receipt again | Clue listed once; no duplicate or early resolution |
| Compare hunger | Hunger unchanged by receipt interaction |

Caution: the current pawn chooses the nearest marker before checking line of
sight at dispatch. When testing a blocked receipt, make sure another closer
marker is not selected; otherwise label the observation ambiguous, not PASS.

## Actual execution record — fill only after a real run

- UTC timestamp; operator; local machine; exact commit and branch:
- Unreal version; isolated checkout path; map; pawn/GameMode:
- Build and native contract test result links or local paths:
- Before and after clue snapshot, phase and hunger:
- Out-of-range rejection observed:
- Blocked line-of-sight rejection observed:
- In-range receipt acceptance, duplicate rejection observed:
- GPU screenshot/recording provenance and file hashes:
- Editor log locations, exit codes and meaningful defects:
- Verdict: M008_PIE_PASS only when all criteria have native evidence;
  otherwise FAIL_CLOSED or NOT_RUN.

Local evidence stays ignored/private unless explicitly authorized for release.
Do not upload private LARP messages, copyrighted Bloodlines franchise
expression, unrelated TSTSS data or unlicensed art. Keep all associated PRs
draft and unmerged until verified and reviewed.
