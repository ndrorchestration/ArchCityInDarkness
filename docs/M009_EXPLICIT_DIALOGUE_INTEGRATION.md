# M009 — Explicit player choices for Glassbend (source integration review)

**Status:** DRAFT / PROTOTYPE_NOT_CANON / NO NATIVE M009 VERIFICATION.
The existing M005 dialogue files were copied byte-for-byte from draft PR #9,
head d57110d5cdaf13fb90daf416117b875a691d8435. This is an integration
candidate, not a claim that PR #9 was merged or its writing approved.

The world integration base is the draft PR #22 first-person review map, stacked
through M008 PR #24. All parent PRs remain draft and unmerged. No private
Columbus in Darkness material, licensed Bloodlines expression, or TSTSS assets
have been imported.

## Problem and decision

Prior prototype native code selected commit_dialogue or commit_stealth when the
player pressed E on Mara or Nico *again* after obtaining their clue. E at Etta
could select commit_confrontation. This permits an irreversible story outcome
without an explicit, readable player choice.

**M009 review decision:** disable these implicit route commits in the temporary
world actor. E is permitted to discover the original source clues only. The
route-specific actions remain present in UACIDQuestInteractionBridge and the
canonical review quest ledger, but cannot be triggered from the M009 one-key
world interaction. All final route selections are deferred to a properly
validated, explicit dialogue UI; it is *not implemented* by this PR.

## Proposed graph data imported from M005

- 19 provisional original captioned dialogue nodes.
- 30 captioned player choices; 5 actor/prop entrypoints.
- 7 explicit source action IDs (4 clue actions, 3 resolution actions).
- Mara, Nico, Etta are original fictional NPCs. Text and identities are
  exploratory and not creator-approved canon.
- Existing quest effects must remain unchanged:

| Route | Required clues | Explicit choice action | Evidence | Exposure | Hunger change |
| --- | --- | --- | --- | --- | --- |
| Dialogue | shift_receipt + ledger_gap | commit_dialogue | redacted_shift_log | 0 | 0 |
| Stealth | route_note | commit_stealth | timecard_photo | 12 | 0 |
| Confrontation | annex_badge | commit_confrontation | discarded_register | 25 | 0 |

All routes are nonlethal and allow opting out. No automatic feeding.

## World E behavior at this review head

| World anchor | First E while eligible | Later E after clue / prereq | Is route commit possible via E? |
| --- | --- | --- | --- |
| shelter shift_receipt | inspect_receipt | no-op | No |
| annex_badge | inspect_annex_badge | no-op | No |
| Mara Vale | ask_mara_about_ledger | no-op | No |
| Nico Bell | ask_nico_about_route | no-op | No |
| Etta Quill | no-op | no-op | No |

Current on-screen feedback for a blocked/no-op interaction remains generic;
it is NOT a dialogue widget, and all three ending routes are deliberately
unreachable via the world E input until explicit dialogue selection exists.
The unaltered M005 graph models proposed decisions in source data only.

## Portable verification

    python tools/validate_dialogue_contract.py
    python tools/check_m009_dialogue_world_contract.py
    python -m unittest discover -s tools/tests -p 'test_*.py' -v
    python tools/check_project_structure.py
    python tools/check_m008_source_readiness.py

The M009 static guard cross-checks world allowlisted anchor IDs, source dialogue
entrypoints, dispatch IDs, 4 clue-only E actions, absence of auto-commit action
selection, and nonlethal/no-hunger routes. The test suite deliberately mutates
contracts and source signatures to confirm rejection. Portable validation is
not Unreal compilation, native runtime behavior, or artistic approval.

## Native Unreal 5.8.4 gate — not yet executed for M009

After Neontic reconnects, preserve active Unreal work; record resource preflight,
exact Git SHA and UE version in a clean isolated review checkout. Build and
native-test the changed C++ source, then in real GPU PIE verify:

1. A single E on Mara or Nico discovers the corresponding clue.
2. A second E on that NPC does **not** resolve a route, regardless of whether
   prerequisites for a route are already held.
3. E on Etta does not resolve confrontation, with or without annex_badge.
4. Repeated E on both prop clues remains idempotent.
5. No input path mutates hunger, changes trust/exposure or resolves the quest
   without an explicit resolution choice.
6. UI shows a clear "dialogue unavailable in review" indication rather than
   confusing a blocked interaction with a missing prerequisite; if not,
   report an accessibility/UX blocker for later work.

Log native state before/after and capture actual Unreal GPU screens. Do not
promote the temporary first-person camera choice to approved canonical design.

## Follow-on required before playable dialogue can be claimed

- Implement an accessible UMG dialogue panel whose rendered text, choices and
  focus behavior are reviewed at 1080p. Show a back/leave choice and readable
  captions; keyboard and controller selection remain future implementation.
- Opening the dialogue may start only after validating the selected world
  marker/player is current, in the same standalone world, within 2.75m and
  unobstructed. Re-check all gates again at explicit selection time.
- Validate that the choice ID belongs to the currently active dialogue node,
  and its action ID is allowed **for that anchor**. Do not expose a generic
  arbitrary-action dispatch from client input. The bridge alone is not a
  security gate.
- The quest ledger remains the authoritative branch/outcome check, including
  clue prerequisites, no duplicate clues and exactly one irreversible ending.
- Test all three route completions and negative cases in native PIE only after
  that explicit UI exists. Native SaveGame restart/round-trip is a separate gate.
- Seek creator approval of provisional story, original characters and camera
  direction before any art/canon or release promotion.

This PR is source-integration preparation, not a playable dialogue milestone.
