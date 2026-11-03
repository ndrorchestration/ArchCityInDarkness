# Glassbend — Level 001 greybox implementation plan

**Status:** planning only; this is not an Unreal map, tested gameplay, approved art, or physical recreation of Columbus. No private roleplay archive content may be imported.

## Single-location production target
One **original fictional** nighttime block in Columbus, Ohio. Plan an initial playable area of approximately **140 m × 90 m**, with a short walkable loop and clear sight lines; this is a prototype bounding box, not a claim about a real city's dimensions. Unreal default 100 cm = 1 m.

### Greybox landmarks
| Zone | Approximate size | Purpose | Provisional Unreal names |
| --- | --- | --- | --- |
| Sidewalk and shelter | 35 × 8 m | Start, inspect shift receipt | `BP_ACID_StartShelter`, `BP_ACID_Clue_Receipt` |
| Archive frontage | 25 × 18 m | Mara dialogue and ledger gap clue | `BP_ACID_ArchiveDoor`, `BP_ACID_NPC_Mara` |
| Courier cut-through | 12 × 36 m | Nico, route-note clue, stealth vantage | `BP_ACID_Alley`, `BP_ACID_NPC_Nico` |
| Transit annex | 28 × 20 m | Etta and badge clue, confrontation alternative | `BP_ACID_TransitAnnex`, `BP_ACID_NPC_Etta` |
| Fictional river overlook | 50 × 12 m | Night mood and route readability | `BP_ACID_RiverOverlook` |

All locations and venue names are fictional. The skyline may draw on general architectural features of central Ohio but must not reproduce copyrighted game maps or existing LARP depictions.

## Build stages
1. **Blockout:** primitive collision meshes, walkable route, start/exit triggers and one calibrated 175 cm mannequin proxy. No purchased/borrowed game art.
2. **Interaction:** traceable targets for NPCs and clues. One interaction per input press, no soft lock or repeating unlock animations.
3. **Quest choice:** eventually load/translate `Prototypes/Glassbend/the_unclaimed_hour.json` into native Unreal data assets. Until then its Python reference model is **not** gameplay.
4. **Three-route end condition:** dialogue, stealth, and confrontation should each produce evidence and route-specific consequences. No mandatory violence, killing, or feeding.
5. **Save/load:** once a versioned `USaveGame` contract exists, persist flags, trust, exposure and final method; same saved result must not be overwritten by revisiting an interaction.
6. **Visual review:** capture four Unreal camera viewpoints (arrival, archive, alley, overlook), controller prompt visibility, rain readability and 1080p legibility. Placeholder art remains noncanonical.

## Minimum operational requirements
- Keyboard/mouse movement and interaction are checked in PIE before shipping any build.
- Provide an accessible high-contrast prompt and captions for all dialogue (no reliance on audio cues alone).
- Readable nighttime lighting without forcing players to use postprocess exposure tricks; accessibility pass on UI contrast.
- For early performance, profile a basic 1080p development build and record actual frame time. **No FPS target is claimed met.**
- Track all scene files and content provenance; unlicensed external artwork is prohibited.
- Verify collision around stairs, doorways and prop placement using UE Editor captures and a traversal checklist.

## Acceptance and evidence gate
Native Unreal C++ compile and hunger automation in issue #2 must be verified before implementation of the first interactive scene. The portable quest proposal and its tests prove only data consistency. If native build remains blocked by the running Editor/Live Coding, leave the implementation gated.

## Dependencies and traceability
- Draft PR #1: <https://github.com/ndrorchestration/ArchCityInDarkness/pull/1>
- Native verification: <https://github.com/ndrorchestration/ArchCityInDarkness/issues/2>
- First level: <https://github.com/ndrorchestration/ArchCityInDarkness/issues/3>
- Original story treatment: [FIRST_SCENE.md](FIRST_SCENE.md)
