# Glassbend native gameplay review — integration pilot

Status: **PROTOTYPE_NOT_CANON**, **DRAFT**. Native compilation, map readback and PIE gates require separate evidence at the exact current head.

This isolated branch stacks the M004 quest interaction bridge (and its M002/M003 dependencies) with the separate PR #20 Glassbend native review map. It adds a review-only first-person character, camera, keyboard/mouse input, five original world markers, a map-specific game mode, proximity and visibility gates and onscreen diagnostic prelude/status text. It does not copy historical Columbus in Darkness communications, third-party franchise expression or assets.

Controls: WASD movement, mouse look, E interact with nearest marker, Tab inspect investigation state. The shelter receipt, archivist Mara, courier Nico, annex badge and manager Etta are represented by engine primitives. At Mara and Nico, use E once for a clue and again to attempt the eligible resolution; Etta requires the annex badge. Dialogue, stealth and confrontation outcomes reuse the UACIDQuestInteractionBridge and the quest ledger's original three nonlethal outcomes. Hunger must remain unchanged by interactions.

Safety: exact five-anchor allowlist, player-controlled input requirement, standalone matching world, rechecked 2.75-metre range and visibility, quest prerequisite checking, single irreversible ending and no arbitrary dispatched action ID. The onscreen text is diagnostic, not an accessible UMG dialogue UI or cinematics. No SaveGame disk serialization, production assets, voice, NPC animation, robust traversal, GPU screenshot, packaging or creator canon approval is claimed.

After compiling the Unreal 5.8 Editor target in a clean isolated workspace, run the upgrade_prelude_gameplay.py editor commandlet once on the disposable map, and independently run verify_prelude_gameplay.py. Run the native ArchCityInDarkness.Prelude.Glassbend.Contract automation test separately, then manually test PIE for actual movement, collision, all three endings, readable prompts and creator visual review. Preserve all other project processes and caches. Keep draft/unmerged until independent evidence supports promotion.
