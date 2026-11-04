# M004 — Glassbend interaction-to-quest bridge (source-only)

**Status:** `PROTOTYPE_NOT_CANON` / `NATIVE_UNVERIFIED`. This is a staged C++ Blueprint-callable *action routing adapter*, not player input, world-target interaction, an actor, a level, UI, a proximity check, executable gameplay or approved story.

## Design purpose
Prior source milestones have two independent contracts: original quest outcome rules (`UACIDQuestLedgerComponent`) and fictional Glassbend spatial/actor markers (`layout_v1.json`). M004 connects a small closed list of **7 named player-intent actions** to those quest-rule entry points, so an eventual world interaction component does not embed quest decision logic in a widget or prop Blueprint.

## Explicit bindings
| Action ID | Source anchor | Safe quest operation |
| --- | --- | --- |
| `inspect_receipt` | `shift_receipt` prop marker | `DiscoverClue(shift_receipt)` |
| `ask_mara_about_ledger` | `mara_vale` NPC marker | `DiscoverClue(ledger_gap)` |
| `ask_nico_about_route` | `nico_bell` NPC marker | `DiscoverClue(route_note)` |
| `inspect_annex_badge` | `annex_badge` prop marker | `DiscoverClue(annex_badge)` |
| `commit_dialogue` | `mara_vale` NPC marker | `TryResolve(Dialogue)` |
| `commit_stealth` | `nico_bell` NPC marker | `TryResolve(Stealth)` |
| `commit_confrontation` | `etta_quill` NPC marker | `TryResolve(Confrontation)` |

Identifiers and anchor provenance live in [interaction_bindings_v1.json](../Prototypes/Glassbend/interaction_bindings_v1.json). The C++ source `UACIDQuestInteractionBridge::TryApplyAction(UACIDQuestLedgerComponent*, FName)` is a narrow adapter: it rejects null/unknown IDs, calls only existing ledger transitions, and returns their success status. The ledger itself rejects duplicate clues, wrong route prerequisites, post-resolution mutation and contradictory saved states.

**Critical security/UX boundary:** The bridge accepts an action ID from its caller. It does not inspect a pawn, line of sight, actor identity, distance, press event, authority, cooldown or physical availability. **Do not wire it directly to arbitrary UI input** as if those checks are complete. Future UE actor/controller code must prove valid nearby interactable identity and player ownership before dispatch.

## What portable verification covers
- `tools/validate_interaction_bindings.py` checks the seven exact IDs against the reviewed quest JSON, layout anchors, C++ dispatch cases and noncanonical contract.
- `tools/tests/test_interaction_bindings.py` supplies negative fixtures for duplicate/unknown IDs, wrong quests/routes, missing anchors, C++ drift and inappropriate world-gate claims.
- `tools/check_project_structure.py` runs the integration checks in CI; portable PASS does not compile C++.
- `Source/ArchCityInDarkness/Private/Tests/ACIDQuestInteractionBridgeTests.cpp` contains Unreal-native **test source** for valid choices, duplicate rejection, insufficient prerequisites, invalid IDs, and no post-resolution overwrite. Until executed on Unreal 5.8.4, these assertions are `NOT_RUN`.

## Gates in order
1. M001 hunger native Editor compile and automation test PASS on exact [PR #1](https://github.com/ndrorchestration/ArchCityInDarkness/pull/1) head. Do not force-close an active Editor/Live Coding session.
2. M002 quest native compile and both existing native tests PASS on [PR #4](https://github.com/ndrorchestration/ArchCityInDarkness/pull/4) head.
3. M003 layout data review and scene direction approval on [PR #6](https://github.com/ndrorchestration/ArchCityInDarkness/pull/6) head. No claim that source layout shows actual collision or rendering.
4. Only then compile this M004 stacked head in UE 5.8.4; run all **three** individually named tests with independent Editor logs and reports. Example after the above prerequisites, from a clean isolated M004 checkout with Editor closed normally:

```powershell
pwsh -NoProfile -File .\tools\Verify-UnrealNative.ps1 -Tests `
    'ArchCityInDarkness.Survival.Hunger.Contract', `
    'ArchCityInDarkness.Quest.Glassbend.Contract', `
    'ArchCityInDarkness.Interaction.Glassbend.Contract'
```

5. If all native gates and creator story approval pass, implement the first **disposable review-only** actor/pawn interaction layer with world-space reach, line-of-sight, player input, and accessibility. Capture native evidence of valid/invalid interactions and route outcomes. Do not merge drafts, promote art, release or assert real persistence on source-only evidence.

No historical LARP messages, real-person participant data, franchise artwork, copied vampire-lore systems or game locations are used.
