"""Independent NullRHI reopen of original noncanonical Glassbend gameplay review map."""
import unreal

MAP = "/Game/ArchCity/Review/Glassbend_Prelude_Greybox"
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not levels.load_level(MAP):
    raise RuntimeError("Review map reopen failed")
found = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
anchors = ("shift_receipt", "mara_vale", "nico_bell", "annex_badge", "etta_quill")
for anchor in anchors:
    label = "Interact " + anchor
    if label not in found or not isinstance(found[label], unreal.ACIDPreludeInteractable):
        raise RuntimeError("Missing or invalid marker " + label)
    if str(found[label].get_editor_property("anchor_id")) != anchor:
        raise RuntimeError("Wrong action identity at " + label)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world:
    raise RuntimeError("No editor world")
mode = world.get_world_settings().get_editor_property("default_game_mode")
if mode != unreal.ACIDPreludeGameMode.static_class():
    raise RuntimeError("Wrong world-specific game mode: " + str(mode))
unreal.log("ARCHCITY_GAMEPLAY_REVIEW_READBACK_PASS anchors=" + str(len(anchors)))
