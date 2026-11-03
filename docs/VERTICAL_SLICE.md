# Milestone 001 — Smallest reversible vertical-slice foundation
**Status:** source scaffold proposed in draft PR; not playable and not native-verified.

## Experience target
One original, compact fictional riverfront block in nighttime Columbus. The player can navigate it, speak with three distinct NPCs, face a survival choice, and resolve one original missing-person investigation by persuasion, stealth, or combat. The same event should alter later dialogue and remain saved.

## Phases
**M001-A — source only (this PR):**
- Unreal project descriptor + game/editor C++ targets.
- Reusable prototype hunger component with simple, testable constraints.
- Native automation test written but not yet executed.
- Project brief, originality rules, verification checklist.
No maps, character meshes, animations, NPCs, narrative assets or production art.

**M001-B — native gate:**
- Use Windows Unreal Engine 5.8.4; generate project files and build Editor target.
- Run `ArchCityInDarkness.Survival.Hunger.Contract`.
- Store exact command, engine path/version, head commit, build logs, test output, any errors.
- No pass claim until real logs prove it.

**M001-C — visual interaction prototype (future PRs only):**
- One original test map with placeholder geometry and blockout scale.
- Third-person pawn, camera, interaction trace, NPC conversation stub.
- Dialogue condition flags and a quest choice ledger; safe save/reload.
- One feeding interaction respecting player choice; avoid automatic forced feeding.
- Three resolution routes with a reproducible state-reconciliation test.
- Four-camera screenshots; motion, control readability and collision inspection.

## Visual acceptance (M001-C)
1. Columbus-inspired but original neighborhood; no imported Bloodlines or LARP visual assets.
2. Nighttime mood legible on a typical 1080p display, with doors/interactive NPCs discernible.
3. Character scale, sidewalks, doorways, lighting and traversal reviewed in multiple views.
4. Prototype meshes explicitly marked noncanonical.
5. No mistaken assumption that generated or offline renders are Unreal engine screenshots.

## Functional acceptance (M001-C)
- Keyboard/mouse navigation and deterministic interact prompt.
- Three NPCs with distinct states; one quest with 3 legitimately different routes.
- Survival meter 0–100, bounded, observable, no invalid action mutation.
- Consequence flags persist through restart; no accidental soft lock.
- A failing test or missing native capture blocks promotion.

## Non-goals
Full city map, social simulation at scale, combat polish, facial motion capture, public launch, deployment or merging this draft without review.
