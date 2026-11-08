# M010 — Diagnostic explicit-choice input in native Glassbend review pawn

**Status:** DRAFT, PROTOTYPE_NOT_CANON, SOURCE CANDIDATE ONLY.
**Unreal native compile/test and GPU PIE gameplay: NOT_RUN on this branch.**

## Purpose and boundaries

M009 prevented accidentally ending The Unclaimed Hour with repeated E presses.
M010 supplies an **intentionally temporary, non-UMG** way for a human to attempt
a distinct, deliberate route decision in an isolated Unreal review map, without
silently promoting the provisional M005 writing or claiming completed dialogue.

This review harness is not a finished dialogue panel and has none of the
branch-by-branch M005 text/caption presentation, menu focus, gamepad navigation,
localization, persistence, cinematic polish or accessibility approval. Never
promote it to approved dialogue, production art, or a released vertical slice.

## Proposed controls (source changes; native behavior still unverified)

| Input | Review action | Guard |
| --- | --- | --- |
| WASD / Mouse | First-person greybox locomotion/look | Existing player pawn |
| E | Discover a clue from an eligible marker | M009 same-world, 2.75m, line of sight |
| Tab | Display current investigation snapshot and hunger | Existing status |
| F | Open a pending, **single-use** diagnostic choice on nearby Mara, Nico or Etta | Player-controlled pawn, investigating phase, same world, range, height, line of sight |
| Enter | Confirm the *specific* pending NPC's original route choice | Same actor still present, player/session binding, same world/range/height/LOS revalidated; ledger enforces prerequisites and terminal phase |
| Escape | Abandon pending review choice with no quest change | Clears session |
| E on unrelated prop | Cancels any pending dialogue and executes E normally | Cannot reuse stale session |

A pending session is only a weak reference to a world NPC. There is no arbitrary
choice/action-ID input from keyboard, no auto-resolution from E, and no ability
to commit a different NPC's route using the current pending session.

### Exact original M005 IDs retained

| NPC anchor | Fixed review choice | Bridge action | Prerequisites | Outcome |
| --- | --- | --- | --- | --- |
| mara_vale | mara_resolve | commit_dialogue | shift_receipt + ledger_gap | redacted_shift_log; trust +1, exposure 0 |
| nico_bell | nico_resolve | commit_stealth | route_note | timecard_photo; trust 0, exposure 12 |
| etta_quill | etta_resolve | commit_confrontation | annex_badge | discarded_register; trust -1, exposure 25 |

These outcomes are mutually exclusive, nonlethal and have no automatic hunger
change. The scene's existing original NPCs and proposed geography remain
untouched. Choosing a route by pressing F then Enter is a diagnostic harness,
**not a substitute for selecting a captioned option in a proper M005 graph UI**.

## Portable source checks (not native verification)

    python tools/check_project_structure.py
    python tools/check_m008_source_readiness.py
    python tools/validate_dialogue_contract.py
    python tools/check_m009_dialogue_world_contract.py
    python tools/check_m010_explicit_review_input.py
    python -m unittest discover -s tools/tests -p 'test_*.py' -v

Portable M010 checks cover source signatures for session lifecycle, exact
anchor/choice/action mapping, fail-closed extra input, revalidation, and fixed
original dialogue graph parity. New M010 assertions in the Prelude native
automation test source must be compiled and **actually executed** in UE 5.8.4
before being considered verification evidence.

## Next native verification on Neontic (safe isolated review checkout)

1. Reconnect authorized remote agent. Read-only inspect disk/RAM, current
   Unreal Editor/Live Coding sessions, engine version and checkout SHA.
2. Do not disturb TSTSS or force-close active editor sessions. If an external
   build is needed, operator must save and close active Editor normally.
3. Build the exact M010 review branch with Unreal 5.8.4. Run the four native
   contracts (Hunger, Quest, Interaction, Prelude), independently preserving
   engine logs and validated automation reports.
4. Launch the actual Glassbend greybox in GPU PIE and test:
   - F out of range or behind a wall does not open a dialogue.
   - Enter without F does not resolve a route.
   - F on Mara then Escape cancels, and Enter afterward does nothing.
   - F on Mara then move out of range/behind obstruction before Enter rejects.
   - F on Nico cannot dispatch mara_resolve, and vice versa (native automated
     mapping tests for the static allowlist; active session guard in PIE).
   - Missing required clues cause Enter to reject without changing evidence,
     hunger, trust or exposure.
   - After collecting the required clues with E, F+Enter on each of the three
     NPCs in separate fresh runs yields only the matching original outcome;
     the other routes cannot overwrite the resolution.
   - E on an unrelated marker while a dialogue is pending cancels the session.
   - No automatic feeding or violence; readable diagnostic text appears.
5. Capture real native GPU screenshots and before/after logs at exact SHA.
   If any gate lacks evidence or fails, mark FAIL_CLOSED; do not merge.

## Known limitations and next engineering steps

- A proper accessible UMG dialogue overlay must display **actual original M005
  lines and per-choice captions**, including all back, failure and leave nodes.
  Native player selection must validate the **currently active node and choice**
  and recheck marker/world gates at dispatch. That is a distinct future
  milestone; this harness only exposes one fixed resolution option per NPC.
- The temporary review code uses Unreal legacy action mappings and on-screen
  debug messages, not a modern localized UI system or controller UX.
- The M010 native test contains source assertions for the exact allowlist and
  invalid action rejection; real PIE and build proof are outstanding.
- The underlying parent PRs #22, #24 and #26 are unmerged. Reconcile stacking
  and any overlapping M005 review work before considering integration to main.
- All writing and character art remain provisional. Do not import private
  Columbus in Darkness LARP archives, copyrighted Bloodlines assets, or TSTSS.

**Admission:** source-only CI PASS is not native compile/PIE PASS. Explicit
operator observation and creator review are still required.
