# M006 — Standalone Glassbend text preview (NOT Unreal gameplay)

**Status:** `PROTOTYPE_NOT_CANON` / `SOURCE_ONLY`. This is a portable, single-process Python narrative rehearsal of the original *The Unclaimed Hour* quest. It is intentionally not an Unreal map, packaged game, player controller, actor interaction, 3D rendering, production gameplay, C++ compilation or approved fiction.

## Why this exists
M006 lets the game designer try the source-defined dialogue and quest choices while the in-engine slice is developed. It reuses the approved-for-review *contracts*, not the private historical Columbus in Darkness archive. Character/dialogue/story still require creator canon approval.

## Opening and prelude
The text rehearsal now opens in a fictional rain-soaked Glassbend after midnight. The scene establishes the protagonist's hunger, the shelter and archive, and the missing worker's unexplained hour, then leaves the first destination to the player. The proposed narration avoids specifying a protagonist name or backstory; it is provisional and awaiting creator review. It runs again when a new investigation is started. This is text-only narrative staging, not an Unreal cinematic, playable scene, or approved canon.

## Start the preview on Windows
From a clean checkout of this isolated draft branch, using Python 3:

```powershell
python tools/glassbend_text_preview.py
```

Follow numbered prompts to visit the shelter receipt, Mara, Nico, the annex badge or Etta. Choose numbered dialogue options. The state readout reports clues, route, route-specific evidence, Mara trust, public exposure and hunger. At the street menu, `s` saves, `l` loads, `n` starts a new investigation after confirmation, and `q` exits. Reopening a location lets you try alternate questions. Once a route is resolved, all other quest actions remain rejected until a new investigation is started. A new investigation leaves the existing save file untouched.

For three deterministic, noninteractive examples (no typing required):

```powershell
python tools/glassbend_text_preview.py --demo
```

Each demonstration starts with a fresh in-memory state, follows a source-defined route and prints the resulting evidence/exposure/trust. The preview calls the existing pure `resolve` reference implementation from `tools/validate_quest_prototype.py` and uses the exact dialogue and action IDs in the M002–M005 JSON contracts. It does **not** call Unreal C++ or simulate proximity. Optional local Python saves are described in [the save guide](GLASSBEND_PREVIEW_SAVEGAME.md).

## Verification evidence
- `tools/tests/test_glassbend_text_preview.py` tests all three routes, missing prerequisites, duplicate actions, forged choice rejection, irreversible resolution, zero forced hunger mutation and drift rejection.
- The source checker and portable Python suite must pass at this exact review head; the Windows terminal `--demo` output is **text evidence**, not UE PIE evidence.
- M001-B Hunger and M002 Quest passed named native tests on their respective exact review heads on November 5, 2026. M004 Interaction remains **NOT_RUN**; Python testing does not establish Unreal scene or interaction behavior.

## Later Unreal migration
Use these choice nodes to prototype a real accessible UMG dialogue panel in a disposable Unreal scene **only after** earlier native and creator approvals. The actual UE client must separately enforce world-space distance/line of sight, target identity, keyboard/controller focus, captions and persistence. Pure Python outcome parity may help catch drift, but cannot prove C++ gameplay equivalence.

No external character likenesses, archived roleplay messages, borrowed franchise descriptions, paid assets, Voice of World of Darkness material or live player records are included.
