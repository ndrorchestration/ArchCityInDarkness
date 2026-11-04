# M002 — Glassbend quest ledger native-source candidate

**Status:** source-only review prototype. Unreal compilation and native automation test execution are **not verified**; milestone M001-B remains blocked by active Editor Live Coding.

## Implemented source
- `UACIDQuestLedgerComponent` is an Unreal `UActorComponent` with no Tick, built for the first original Glassbend investigation.
- `DiscoverClue(FName)` accepts only four known clues and rejects duplicates, unrecognized clues, and discovery after resolution.
- `TryResolve(EACIDResolutionRoute)` implements **exactly three** independent choices: Dialogue, Stealth, Confrontation. Missing prerequisites reject without mutating state; completed decisions cannot be rewritten.
- `FACIDQuestSnapshot` exports the state in stable clue order. `TryRestoreSnapshot` validates schema, evidence, route, clue uniqueness, trust and exposure, and only accepts a snapshot on a pristine component. This is **a serialization data boundary, not a working SaveGame file system**.
- Unreal Editor automation test source `ArchCityInDarkness.Quest.Glassbend.Contract` covers route prerequisites, duplicate clues, evidence distinctions, choice idempotence, in-progress resume, and explicit rejection of tampered snapshots (schema, clue, route evidence and trust). These assertions are *written*, not yet executed in Unreal.
- Narrative character names and route choices remain noncanonical concept work; original historical roleplay correspondence is not in this repository.

## Route mapping (original prototype)
| Route | Required clue IDs | Evidence | Mara trust | Exposure |
| --- | --- | --- | ---: | ---: |
| Dialogue | shift_receipt, ledger_gap | redacted_shift_log | +1 | 0 |
| Stealth | route_note | timecard_photo | 0 | +12 |
| Confrontation | annex_badge | discarded_register | -1 | +25 |

Hunger remains untouched by this component. No mandatory feeding, attack or nonlethal action is implemented; the routes are state transitions only.

## Test gate
1. GitHub structure CI and Python prototype tests may pass; **do not equate them with native Unreal evidence**.
2. After closing Unreal Editor / Live Coding normally, open M001 source head in a separate review checkout, compile and run `ArchCityInDarkness.Survival.Hunger.Contract` first.
3. Only after passing M001 gate, compile this stacked M002 branch and run both `ArchCityInDarkness.Survival.Hunger.Contract` and `ArchCityInDarkness.Quest.Glassbend.Contract` using the explicit `-Tests` selection in [the native runbook](NATIVE_VERIFICATION_RUNBOOK.md). The runner generates a distinct report and Editor log for each exact test; an individual missing or failed result fails the overall gate. This runner extension is source-only until verified on Windows.
4. No changes are merged, and no Blueprint, level, NPC, UE SaveGame, or world-playability is claimed.
5. Any native error creates an issue with evidence instead of silently loosening the requirements.

## Source/reference boundaries
- Reference proposal: [Glassbend quest JSON](../Prototypes/Glassbend/the_unclaimed_hour.json)
- Existing C++ hunger component: [ACIDHungerComponent](../Source/ArchCityInDarkness/Public/ACIDHungerComponent.h)
- Vertical slice: [M001](VERTICAL_SLICE.md)
- Issue #2: native source verification
- Issue #3: future playable neighborhood
