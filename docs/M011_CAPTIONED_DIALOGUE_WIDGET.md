# M011 — Captioned M005 dialogue graph in a disposable Unreal UMG review widget

**STATUS: DRAFT / PROTOTYPE_NOT_CANON / UNREAL NATIVE BUILD NOT VERIFIED /
GPU PIE NOT VERIFIED / NO ART OR WRITING APPROVAL.**

This is a stacked experimental addition to M010, not a production dialogue
system. It preserves the original provisional, fictional Columbus-inspired
Glassbend story and the existing M005 dialogue graph. All parent PRs remain
unmerged. Do not substitute source/CI success for Unreal execution.

## Purpose and design

M010 offers a diagnostic **F → Enter** route confirmation without presenting
the real choices. M011 supplies a distinct **G** source-dialogue review path
that *attempts* to display the complete original M005 source graph as native
UMG elements, with readable captions and individually clickable choices.

The existing data contract has **19 nodes, 30 choices, five entrypoints and
seven bound gameplay actions**. This PR does not edit that JSON. It reads
Prototypes/Glassbend/dialogue_v1.json from the local Unreal *project checkout*
when a review dialogue is opened; this intentionally does **not** claim that
the file is packaged for distribution or imported as a production UE asset.

### Controls — source intent only

| Input | Intended outcome |
| --- | --- |
| WASD/mouse | Move/look in noncanonical first-person review map |
| E | Existing guarded world clue action; never implicitly resolve a quest |
| F / Enter / Escape | Existing M010 fixed-route diagnostic experiment |
| G | Open full proposed captioned dialogue graph at a visible nearby marker |
| Mouse click / focusable button | Select a line's specific captioned response |
| Escape inside widget | Close, clear pending session, restore game input mode |
| Tab outside UI | Current clues/hunger/status |

The review widget is created from C++ source via UMG (CanvasPanel, Border,
VerticalBox, TextBlock, Button). Its source sets heading, line and choice
caption sizes and a contrasting background; **actual readable size, layout,
focus, mouse clicks, keyboard/controller accessibility and rendering are
unverified until native GPU PIE capture**.

### Data/permission boundary

The widget:
- requires a current local player, an exact weak-referenced actor session,
  active investigation, same standalone world, 2.75m range, height and line
  of sight **before opening**;
- locates the requested node by ID in the original graph and verifies its
  anchor matches the currently bound world marker;
- creates buttons from that node's own choice IDs, not from arbitrary action IDs;
- rechecks active node and marker before applying a choice;
- checks the selected graph's action ID against the actor's **exact seven
  anchored choice → action allowlist**;
- revalidates the player/session, same world, range, height, LOS and quest
  phase **again at side-effect dispatch**;
- asks the existing quest ledger to enforce clue prerequisites, duplicate
  rejection, mutually exclusive endings, trust/exposure and no feeding;
- follows original on_success/on_failure branches; invalid JSON, unknown
  IDs or mismatched nodes fail closed without a quest side effect.

The previous M010 F/Enter route experiment is retained separately for
diagnostics. G is the graph-driven UX candidate; neither is canon-approved.

## Acceptance criteria (not yet satisfied by source changes)

**Portable development gate:**
- [ ] Exact-head GitHub source CI passes: M008, M009, M010, M011 contracts;
  original dialogue validator and Python synthetic regression suite.
- [ ] Static checks verify exact M005 graph integrity, seven original mapped
  actions, G input and UMG dependencies, active-node selection and double
  world authorization. This is only source/evidence readiness.

**Native implementation gate on Neontic:**
- [ ] With an isolated clean review checkout, log exact Git SHA and Unreal
  5.8.4 version; preserve active Unreal/Live Coding sessions and TSTSS work.
- [ ] UE 5.8.4 Editor build succeeds after adding UMG/Slate/Json module
  dependencies; **do not assume this C++ widget compiles from source CI**.
- [ ] Native Hunger, Quest, Interaction, Prelude contract tests pass at the
  SAME HEAD with validated report JSON and Unreal logs.
- [ ] Real GPU PIE opens the map and accepts G near each of five known
  anchors, with corresponding header/line and exact choices shown.
- [ ] Escape closes the panel without changing quest state and input focus
  returns to the player; no stuck cursor or hidden input.
- [ ] All original M005 back, leave, action-failure and choice-success
  transitions are reachable; invalid graph/node/action is rejected.
- [ ] A world visibility/range change before click prevents any quest
  mutation; actions cannot be dispatched for a different NPC/prop.
- [ ] Fresh independent runs demonstrate dialogue, stealth, confrontation
  outcomes and unchanged hunger; no hidden repeat/overwrite.
- [ ] Actual 1080p native screenshots show captions and choice focus/contrast,
  not placeholder/offline/generated screenshots. Review text wrapping,
  keyboard/mouse access, and accessibility defects.
- [ ] Creator separately reviews provisional writing, camera choice, story
  tone and original NPC design; no canon or production-art promotion without
  explicit approval.

## Source-only commands

    python tools/check_project_structure.py
    python tools/validate_dialogue_contract.py
    python tools/check_m008_source_readiness.py
    python tools/check_m009_dialogue_world_contract.py
    python tools/check_m010_explicit_review_input.py
    python tools/check_m011_captioned_widget.py
    python -m unittest discover -s tools/tests -p 'test_*.py' -v

New native automation **source assertions** cover all seven fixed M005
dialogue action pairs and negative/unknown IDs; these test lines have NOT been
executed in Unreal until a later real machine run.

## Technical follow-ons and current limitations

- Native runtime uses loose project-root JSON, intentionally unavailable in
  packaged builds. When native semantics are confirmed, migrate to a
  content-managed Unreal data asset with deterministic cook/integrity checks
  before claiming distribution readiness.
- Dynamic UMG widgets provide a candidate display but not an approved UX
  system. The graph is source-first and error handling is intentionally strict.
- Proper focus/accessible narration, selection by keyboard/controller,
  scroll behavior for 30 choices across nodes, responsive localization,
  layout safe areas, high-contrast review and UI sound require native review.
- E/F/G currently coexist as separate prototype input paths; simplifying
  them to one accessible canonical interaction flow is a later, explicitly
  reviewed integration decision.
- Native SaveGame/restore, production NPC actors, animation, voice, lighting
  and high-quality gameplay screenshots are all independent unfinished gates.
- Respect original rights and privacy: do not import copyrighted Bloodlines
  assets or dialogue, personal LARP archives or unrelated TSTSS materials.

**Do not merge, publish, or call this playable until exact-head native
compilation, observed PIE interaction and creator review are complete.**


## Offline M011 follow-up: keyboard focus and blocked target selection

Later source-only review identified two user-facing risks in the first UI candidate:

1. A panel could receive focus without any response button being focused,
   making keyboard-based review awkward or impossible.
2. When multiple markers are near each other, an occluded nearest marker
   could prevent the G dialogue from opening on another reachable marker.

The draft now creates a scrollable choice list with padding, stores its first
visible response button, calls FocusCurrentChoice after entering UI input mode,
and focuses the next node's first response after graph navigation. Its G target
scan checks CanReviewInteract on each candidate before choosing the nearest.

These are **uncompiled source changes**, not verified visual/accessibility fixes.
Native review must additionally check at 1280x720 and 1920x1080:
- At G opening, the first response truly has keyboard focus and Enter/Space
  activates the intended choice without unexpected movement.
- Escape closes the panel both with and without a button focused, restoring
  character control and mouse visibility.
- Multi-choice nodes remain fully visible or scroll correctly with mouse,
  keyboard and any supported controller navigation; padding and contrast are
  checked against real rendered pixels, not assumed from C++ values.
- Two markers in range with the nearest obscured still allow dialogue with a
  visible reachable candidate; all side-effect clicks still independently
  recheck world authorization and LOS.
- M005 route and failure branches continue to work with the selected focus
  moving to a valid new response. No auto-triggering of outcomes.

This additional work deliberately does not edit the provisional dialogue
writing or approve the camera, art or user-interface design.
