# Technical architecture — initial intent

## Repository layers
- `ArchCityInDarkness.uproject`: standard Unreal project descriptor targeting the 5.8 engine family (user's target 5.8.4).
- `Source/ArchCityInDarkness`: runtime module. Presently one prototype `UActorComponent` for hunger rules. No actor/level/pawn implementation yet.
- `Source/.../Private/Tests`: Unreal automation tests compiled for dev-test contexts.
- `tools/check_project_structure.py`: portable structural sanity check, **not** C++ compile or native Unreal test.
- `docs`: intent and milestone/rights/verification contracts.

## Minimal gameplay contracts
`UACIDHungerComponent` owns one transient per-instance scalar: 0 = sated, 100 = maximal hunger. Prototype begins at 25. `SetHunger` rejects nonfinite values and clamps finite values. `Feed` and `AccrueHunger` accept only finite positive values and return booleans. `OnHungerChanged` broadcasts only on meaningful state changes. It does not automatically interact with people, NPC AI or combat, and it has no save-game semantics yet.

## Stacked source-only milestones (not yet merged or native verified)
- M002: `UACIDQuestLedgerComponent` provides guarded deterministic clue discovery, one-way route resolution, a versioned in-memory snapshot contract and native automation **test source**. No actual disk persistence.
- M003: `layout_v1.json` defines provisional 140 × 90 m fictional Glassbend environment markers and four review cameras. It is not a `.umap` or proof of physical traversal.
- M004: `UACIDQuestInteractionBridge::TryApplyAction` is a closed-list Blueprint-callable action-ID adapter. It delegates to the quest ledger only. It does **not** validate actor identity, distance, line of sight, input, or ownership. Those conditions are required before in-engine activation. The associated C++ automation test remains **NOT_RUN** until a native Unreal verification.
- M005: `dialogue_v1.json` is an original five-entrypoint dialogue graph with guarded success/failure branches referring to M004 action IDs. Portable graph validation checks reachability/caption shape but no widget, localization pipeline, voice acting or in-engine dialogue exists.
- No source-only milestone is an approved art, character, gameplay, build, collision, rendering or release artifact. All are stacked review branches and maintain the originality/IP boundary.

## Extension seam — proposals, not implemented
- `PlayerCharacter` and `Interaction` components for movement and selection.
- `DialogueGraph` data assets and gameplay tag conditions.
- `QuestState` / decision ledger with idempotent transition validation.
- `SocialStanding` data and NPC relationship state.
- `Exposure` rather than any borrowed franchise-specific masking rules.
- Save-game versioned schema, migration and tests.
- Enemy AI/stealth only once the noncombat routes and persistence work.

## Engineering policy
Keep code modular, no hard dependencies on art, avoid global singletons for plot state, validate player actions serverlessly in single-player, and make test fixtures data-driven. Implement integrations one slice at a time. No source file should be treated as native-verified until Unreal logs establish a successful build and automation run.
