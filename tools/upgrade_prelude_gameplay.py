"""Add original gameplay review markers to Glassbend greybox. UE Editor -ExecutePythonScript."""
import unreal

MAP = "/Game/ArchCity/Review/Glassbend_Prelude_Greybox"
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not levels.load_level(MAP):
    raise RuntimeError("Cannot load original review map")
found = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
placements = {
    "shift_receipt": (2200, 1200, 100),
    "mara_vale": (6000, 3300, 100),
    "nico_bell": (9300, 4900, 100),
    "annex_badge": (11900, 4400, 100),
    "etta_quill": (12300, 4500, 100),
}
for anchor, xyz in placements.items():
    label = "Interact " + anchor
    if label in found:
        raise RuntimeError("Review marker already present: " + label)
    actor = actors.spawn_actor_from_class(unreal.ACIDPreludeInteractable, unreal.Vector(*xyz))
    if not actor:
        raise RuntimeError("Unable to place " + anchor)
    actor.set_actor_label(label)
    actor.set_editor_property("anchor_id", anchor)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world:
    raise RuntimeError("Editor world unavailable")
settings = world.get_world_settings()
settings.set_editor_property("default_game_mode", unreal.ACIDPreludeGameMode.static_class())
if not levels.save_current_level():
    raise RuntimeError("Could not save modified review map")
unreal.log("ARCHCITY_GAMEPLAY_REVIEW_MAP_SAVED marker_count=" + str(len(placements)))
