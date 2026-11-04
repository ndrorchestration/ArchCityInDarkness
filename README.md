# Arch City in Darkness

**Status:** pre-production / original RPG prototype. **Engine target:** Unreal Engine 5.8.4 (Windows). **Playable build:** none verified.

An original, single-player, vampire-centered urban supernatural role-playing game set in a fictionalized contemporary **Columbus, Ohio**. Its aim is to evoke the *design strengths* of classic reactive urban RPGs—dialogue, stealth, faction politics, and different ways to finish quests—without reproducing any existing franchise's expressive content.

## Initial gameplay hypothesis

Explore a compact nighttime neighborhood, interact with original NPCs, manage hunger and exposure, and resolve a short investigation through **persuasion, stealth, or combat**. Consequences should persist across conversations and save/load.

- [Project brief](docs/PROJECT_BRIEF.md)
- [Originality and IP boundaries](docs/ORIGINALITY_AND_RIGHTS.md)
- [Vertical slice / definition of done](docs/VERTICAL_SLICE.md)
- [Technical architecture](docs/TECHNICAL_ARCHITECTURE.md)
- [Verification plan](docs/VERIFICATION.md)
- [Native Windows verification runbook](docs/NATIVE_VERIFICATION_RUNBOOK.md)
- [Original first-scene proposal (not canon)](docs/FIRST_SCENE.md)
- [Glassbend level blockout plan](docs/GLASSBEND_GREYBOX_PLAN.md)
- [Source-only quest data contract](Prototypes/Glassbend/the_unclaimed_hour.json)
- [M002 quest ledger C++ source candidate](docs/QUEST_LEDGER_SOURCE_PROTOTYPE.md) — stacked review branch; native unverified
- [M003 Glassbend spatial/camera marker prototype](docs/GLASSBEND_LAYOUT_CONTRACT.md) — further stacked source-only proposal; no Unreal map or rendering
- [M004 Glassbend interaction bridge](docs/GLASSBEND_INTERACTION_BRIDGE.md) — explicit action-to-quest C++ adapter and portable contract tests; no player proximity/input or native compile verified

## Current source foundation

The repository includes a minimal Unreal C++ project descriptor, build targets, a deterministic hunger component, and an Unreal automation-test *source file*. This is **not** evidence of a successfully generated project, compiled module, executed Unreal test, rendered environment, or playable experience.

The GitHub Actions check validates repository structure and portable quest/report-validator tests only; it **does not launch Unreal**. Native 5.8.4 Windows verification is a separate gate.

## Production rules

1. Small, reversible review branches; no unreviewed merges or asset promotions.
2. Original characters, dialogue, faction concepts, supernatural rules, quests, music, environments, and art only.
3. No Vampire: The Masquerade / World of Darkness assets, plot, clan names, or mechanics text. No copies of the *Columbus in Darkness* LARP chronicle, its emails, player data, or characters.
4. This repository is **public**. Historical roleplay messages and personal archives belong in a separate private research area.
5. No commercial/title clearance asserted. `Arch City in Darkness` is a working title pending naming and trademark review.
6. Keep `To Sail the Starry Sky` entirely separate.

## Next gate

Open the project in the specified Windows Unreal installation, generate project files, compile the Editor target, run the hunger automation test, record exact build logs/screenshots, and only then claim native verification. The first playable district and NPC assets have **not** been created.

No license grant is implied by the existence of this repository; clarify software and asset licensing before accepting outside contributions.
