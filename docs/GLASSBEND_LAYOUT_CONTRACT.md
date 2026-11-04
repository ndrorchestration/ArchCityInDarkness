# M003 — Glassbend spatial/layout contract (source only)

**Status: PROTOTYPE_NOT_CANON.** This is a fictional, original location-data proposal, **not** an Unreal `.umap`, navigable environment, player controller, NPC, collision, render, or approved art. No map or gameplay is being promoted before the M001 native gate and creator review.

## Bounds and conventions
- Unreal review scale: **100 cm = 1 m**, fictional XY plane from the southwest corner.
- Proposed footprint **140 m × 90 m**; no claim of geographic fidelity to real Columbus.
- Start marker **(22, 20) m**; temporary height reference **175 cm** human proxy.
- Five rectangular reference zones are *planning envelopes*, not collision meshes or a guaranteed unobstructed scene.

| Zone | XY center (m) | Width × depth (m) | Design purpose |
| --- | --- | --- | --- |
| shelter | 22, 12 | 35 × 8 | Arrival / receipt |
| archive | 60, 37 | 25 × 18 | Mara / ledger gap |
| alley | 93, 49 | 12 × 36 | Nico / courier route |
| annex | 123, 47 | 28 × 20 | Etta / badge |
| overlook | 65, 82 | 50 × 12 | Riverfront view |

## Integration references
- [Spatial markers](../Prototypes/Glassbend/layout_v1.json) use the exact original NPC and clue IDs from [the provisional quest contract](../Prototypes/Glassbend/the_unclaimed_hour.json); this prevents the planned actors or clue spawns from drifting from the quest without an explicit contract change.
- Mara Vale is anchored to the archive, Nico Bell to the alley, and Etta Quill to the annex; their interaction radii are **2.5 m** as a planning target only.
- Four camera markers — **arrival**, **archive**, **alley**, **overlook** — specify review eye/target XY and FOV. Eye height, lens response, atmospheric fog, exposure and actual screen composition must be tuned in native Unreal later. There are **no captured screenshots**.
- Twelve XY waypoints suggest one loop. Validity checks test bounds, closure and nondegenerate edges, **not** collision, reachability, player movement, AI navigation or route lighting.

## Portable verification
Run in a clean isolated review checkout:

~~~powershell
python tools/check_project_structure.py
python tools/validate_glassbend_layout.py
python -m unittest discover -s tools/tests -p "test_*.py" -v
~~~

The validator checks scale, zone extents/overlap, quest-ID correspondence, actor/clue positions, provisional traversal loop and camera markers. These checks remain static Python checks, **never native Unreal verification**.

## Native gate before production implementation
1. [Issue #2](https://github.com/ndrorchestration/ArchCityInDarkness/issues/2): compile and test M001 hunger foundation in Unreal 5.8.4 after user safely closes any active Editor/Live Coding sessions.
2. [Issue #5](https://github.com/ndrorchestration/ArchCityInDarkness/issues/5): compile and test stacked M002 quest code independently with matching reports.
3. Obtain creator review of provisional Glassbend narrative and environment directions.
4. Only then create a disposable `.umap` with these approximate markers, test traversal/input/collision, save/load consequences, UI legibility and 1080p nighttime lighting; gather four native GPU captures. Do not infer visual acceptance from this JSON.

## Originality and privacy
This is a new fictional layout; no real Columbus building, other game's level geometry, proprietary World of Darkness lore, historical live-action roleplay location, participant information or personal archival correspondence is imported. Title and release rights remain unverified.
