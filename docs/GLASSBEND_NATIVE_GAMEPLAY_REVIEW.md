# Glassbend native gameplay review — integration pilot

Status: **PROTOTYPE_NOT_CANON**, **DRAFT**. Native Editor compilation and four separately logged contract tests have PASSED; the upgraded map has passed independent NullRHI readback. **Playable PIE input, collision, visuals and 3D quest completion remain unverified**.

This isolated branch stacks the M004 quest interaction bridge (and its M002/M003 dependencies) with the separate PR #20 Glassbend native review map. It adds a review-only first-person character, camera, keyboard/mouse input, five original world markers, a map-specific game mode, proximity and visibility gates and onscreen diagnostic prelude/status text. It does not copy historical Columbus in Darkness communications, third-party franchise expression or assets.

Controls: WASD movement, mouse look, E interact with nearest marker, Tab inspect investigation state. The shelter receipt, archivist Mara, courier Nico, annex badge and manager Etta are represented by engine primitives. At Mara and Nico, use E once for a clue and again to attempt the eligible resolution; Etta requires the annex badge. Dialogue, stealth and confrontation outcomes reuse the UACIDQuestInteractionBridge and the quest ledger's original three nonlethal outcomes. Hunger must remain unchanged by interactions.

Safety: exact five-anchor allowlist, player-controlled input requirement, standalone matching world, rechecked 2.75-metre range and visibility, quest prerequisite checking, single irreversible ending and no arbitrary dispatched action ID. The onscreen text is diagnostic, not an accessible UMG dialogue UI or cinematics. No SaveGame disk serialization, production assets, voice, NPC animation, robust traversal, GPU screenshot, packaging or creator canon approval is claimed.

## Verified on Neontic, November 5, 2026

- Compiled UE 5.8.4 Editor target on the isolated integration branch: **18/18 build actions, Result: Succeeded, exit 0**. Compiled player pawn, map interaction actor, game mode and Prelude native test source, plus inherited M001-M004 contracts.
- The one-time Unreal Python upgrade saved the original review map with five marker actors and a map-specific game mode. Independent Unreal NullRHI reopen printed **ARCHCITY_GAMEPLAY_REVIEW_READBACK_PASS anchors=5** and exited 0.
- Four separately executed and independently checked native automation reports/logs: **Hunger, Quest, Interaction and Prelude all PASS**. Prelude checked five approved anchor IDs, unknown-ID rejection and null-player rejection; it does not simulate a real pawn physically moving.
- Source-only checks on the review branch: project structure PASS; **54/54 portable tests PASS**. All local Unreal evidence is under ignored Saved/ folders, not in the repository.
- Headless **native game runtime smoke PASS** on the committed review map: Unreal launched /Game/ArchCity/Review/Glassbend_Prelude_Greybox with -game -NullRHI -benchmark -seconds=6. Native log confirmed world brought up for play and printed the original Prelude BeginPlay narrative from the new player character; process exited 0. This confirms startup/pawn BeginPlay, **not** actual keyboard/mouse control, 3D rendering, pathfinding or PIE outcome verification.
- Evidence was gathered against compiled source commit 171916dfde74e2101a4c6dc0415d71443cd92e89 before the final upgraded map binary and verification documentation are committed. Do not describe these as a fresh native replay on a later documentation/map commit.

## Remaining acceptance gates

The project now has a compiled integration candidate and a saved/reopened map, but **no verified PIE playthrough**. Next, launch the exact Glassbend review map in the native Editor and independently verify pawn possession, WASD/mouse input, visibility and collision gating, all three mutually exclusive nonlethal endings, readable captions, no hunger mutation, and debug evidence. Then implement a proper accessible dialogue UI and save/load system and seek creator visual/canon approval. Preserve active unrelated Unreal processes and disk space; keep this PR draft and unmerged.
