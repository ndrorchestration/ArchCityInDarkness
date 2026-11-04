# M007 — Opt-in local save/load for the Glassbend text preview

**Status:** `PROTOTYPE_NOT_CANON` / `PYTHON_ONLY` / `UNREAL_SAVEGAME_NOT_IMPLEMENTED`. This is an actual disk-backed feature for the portable **terminal story rehearsal**, not an Unreal Engine `USaveGame` implementation or a playable 3D build.

## How to use
From a clean, isolated M007 checkout, run:

```powershell
python tools/glassbend_text_preview.py
```

At the **street menu**, type `s` to save and `l` to load. Type `q` to quit. The same choices remain available after reaching a resolved ending, so the final outcome can be saved. There is **no autosave and no autoload**. Starting a new session without `l` begins a fresh investigation.

By default, the file is stored outside the public repository in the OS user's local-data directory:
- Windows: `%LOCALAPPDATA%\\ArchCityInDarkness\\GlassbendPreview\\save_v1.json`
- Unix-like: `$XDG_DATA_HOME/ArchCityInDarkness/GlassbendPreview/save_v1.json` (or `~/.local/share/...`)

For an explicit alternate private file (for disposable tests or a separate playthrough):

```powershell
python tools/glassbend_text_preview.py --save-file "$env:TEMP\\GlassbendReviewSave.json"
```

Use `--demo` for three fresh in-memory reference routes; it never reads or writes the local save path.

## Exact data boundary
- Schema **v1** stores the original quest ID and only seven scalar/array state fields: phase, known clue IDs in deterministic quest order, route, evidence, Mara trust, public exposure and hunger.
- Clue IDs must exist in the original quest. Duplicates, unknown IDs, reversed serialization order and malformed scalar types are refused.
- Investigating state cannot have route/evidence/consequences; a resolved save must contain exactly one known route, its prerequisites and matching evidence/trust/exposure. Impossible saves fail closed.
- File limit 16 KiB; UTF-8 JSON with no duplicate object keys or `NaN`/`Infinity` values.
- An accompanying SHA-256 checksum is used for **accidental corruption detection only**. It provides **no authentication or anti-cheat protection**; anyone who controls the file could forge both data and checksum.
- Saves are written to a temporary file in the same folder, flushed, then atomically replaced; failed replacement leaves the previous completed file intact. The loader validates all data **before** replacing the live in-memory session. A rejected load preserves current progress.
- Dialogue visual/node position is intentionally **not persisted**; save/load operates only at the street menu. This avoids resuming half-completed action side effects.

## Verification
Portable tests in `tools/tests/test_glassbend_savegame.py` cover explicit opt-in, checkpoint and three resolved-state roundtrips, invalid/mismatched versions, checksums, contradictory outcomes, route prerequisites, duplicate IDs, malformed data, size limits, transactional replacement failure and restart flows. Existing quests/dialogue remain covered by the inherited suite.

```powershell
python tools/check_project_structure.py
python -m unittest discover -s tools/tests -p "test_*.py" -v
```

No portable test can prove native Unreal C++, an Editor build, in-engine save/load, player movement, NPC UI, renderer quality or release approval. The **M001, M002 and M004 native test gates remain pending** while active Unreal Editor/Live Coding prevents safe external builds.

## Native follow-up
After those exact-head native gates and creator story review, implement a separately reviewed Unreal `USaveGame` model with guarded serialization, disk roundtrips, version/migration decisions and automation. Do **not** reuse the Python JSON file as a promised UE save format without specifying a tested migration. Do not merge the draft branches or import private LARP data, external franchise content or another game's assets.
