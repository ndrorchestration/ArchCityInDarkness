# M005 — The Unclaimed Hour dialogue graph (source-only narrative proposal)

**Status:** `PROTOTYPE_NOT_CANON` / `NOT_IMPLEMENTED`. Original dialogue data only: no Unreal widget, actor, input, localization pipeline, voice acting, screenshots or tested playable sequence. Copyrighted franchise dialogue and historical roleplay correspondence are excluded.

## What this adds
[dialogue_v1.json](../Prototypes/Glassbend/dialogue_v1.json) contains **19 nodes, 30 player-visible choice entries and five independent entrypoints** tied to the source-only interaction anchors: sheltered pay receipt, discarded annex badge, night archivist Mara Vale, courier Nico Bell and annex manager Etta Quill.

The dialogue preserves the earlier provisional quest treatment: a missing hour in an otherwise plausible shift ledger. The prototype offers four discoverable clues and three nonviolent resolutions. It does not reveal the underlying larger mystery or lock the user into one route.

| Entry point | Role in the prototype | Action bindings |
| --- | --- | --- |
| Pay receipt | Examine an unexplained paid shift | `inspect_receipt` |
| Mara | Learn about a missing ledger hour; optional privacy-preserving persuasion | `ask_mara_about_ledger`, `commit_dialogue` |
| Nico | Learn the transfer route; observe without approaching anyone | `ask_nico_about_route`, `commit_stealth` |
| Annex badge | Discover a discarded visitor pass | `inspect_annex_badge` |
| Etta | Nonviolent confrontation about annex records | `commit_confrontation` |

## Choice routing
Each choice has an explicit unique ID, captioned player text, optional `action_id`, success/failure next-node references and a close flag. Failed actions lead to a source-defined retry or explanation node, not to a success reveal. A completed quest cannot be overwritten by another route (enforced by the M002 quest ledger when it eventually runs in Unreal).

All dialogue line text and UI-choice captions are provisional English source strings. They are not licensed recordings or published game content. No required violence or forced feeding action exists in the data. The C++ interaction bridge and quest ledger remain on prior stacked branches; this M005 milestone introduces **no additional native gameplay code**.

## Portable verification
`tools/validate_dialogue_contract.py` checks schema, noncanonical status, entrypoint/actor/anchor parity, unique dialogue and choice IDs, valid branching targets, complete seven-action coverage, no cross-NPC jumps, node reachability, dialogue exit options and caption-size limits.

`tools/tests/test_dialogue_contract.py` contains negative fixtures and pure **reference** walkthroughs of all three outcomes, failure/retry and no automatic hunger changes. These synthetic checks do not execute Unreal C++ or prove UI behavior.

From clean review checkout:

```powershell
python tools/check_project_structure.py
python tools/validate_dialogue_contract.py
python -m unittest discover -s tools/tests -p test_*.py -v
```

## Integration path and acceptance
1. Native build/test the M001 hunger, M002 quest, and M004 action bridge on their exact reviewed heads after the user safely closes Unreal Editor/Live Coding; preserve separate automated reports. Existing draft PRs remain unmerged.
2. Creator reviews fictional Glassbend story, character tone, all provisional lines and licensing boundary; this is a **proposal**, not accepted canon.
3. Only then build a disposable native Unreal dialogue widget (high contrast, readable at 1080p, caption-first) and bind exact action IDs from M004 behind real pawn/actor proximity and line-of-sight checks.
4. Verify in PIE: all five entrypoints, all three routes, insufficient-clue feedback, duplicate choices, no hard lock, irreversible outcomes, persistent save/load once a real versioned SaveGame exists, and accessible traversal/input.
5. Gather actual screen captures of NPC interaction plus night scene lighting. Until then `NATIVE_TEST=NOT_RUN`, `PLAYABLE=NOT_ESTABLISHED`, `ART=NOT_APPROVED`.

Originality: fictional new names and dialogue, no incorporation of Vampire: The Masquerade / World of Darkness dialogue, Columbus in Darkness LARP archives, personal correspondence, other franchise maps, or real-world identifying details.
