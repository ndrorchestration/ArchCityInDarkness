# Technical architecture — initial intent

## Repository layers
- `ArchCityInDarkness.uproject`: standard Unreal project descriptor targeting the 5.8 engine family (user's target 5.8.4).
- `Source/ArchCityInDarkness`: runtime module. Presently one prototype `UActorComponent` for hunger rules. No actor/level/pawn implementation yet.
- `Source/.../Private/Tests`: Unreal automation tests compiled for dev-test contexts.
- `tools/check_project_structure.py`: portable structural sanity check, **not** C++ compile or native Unreal test.
- `docs`: intent and milestone/rights/verification contracts.

## Minimal gameplay contracts
`UACIDHungerComponent` owns one transient per-instance scalar: 0 = sated, 100 = maximal hunger. Prototype begins at 25. `SetHunger` rejects nonfinite values and clamps finite values. `Feed` and `AccrueHunger` accept only finite positive values and return booleans. `OnHungerChanged` broadcasts only on meaningful state changes. It does not automatically interact with people, NPC AI or combat, and it has no save-game semantics yet.

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
