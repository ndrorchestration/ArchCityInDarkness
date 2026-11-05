import unreal

MAP = "/Game/ArchCity/Review/Glassbend_Prelude_Greybox"
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not levels.load_level(MAP):
    raise RuntimeError("Could not reopen greybox map")
found = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
required = {
    "Walkable ground": unreal.StaticMeshActor,
    "Archive facade": unreal.StaticMeshActor,
    "Annex facade": unreal.StaticMeshActor,
    "Shelter back": unreal.StaticMeshActor,
    "Shelter roof": unreal.StaticMeshActor,
    "Overlook barrier": unreal.StaticMeshActor,
    "Prelude arrival start": unreal.PlayerStart,
    "Shelter light": unreal.PointLight,
    "Archive light": unreal.PointLight,
    "Annex light": unreal.PointLight,
}
for name, cls in required.items():
    if name not in found or not isinstance(found[name], cls):
        raise RuntimeError("Missing or wrong actor: " + name)
start = found["Prelude arrival start"].get_actor_location()
if abs(start.x-2200) > 0.1 or abs(start.y-2000) > 0.1:
    raise RuntimeError("Unexpected player start")
unreal.log("ARCHCITY_PRELUDE_READBACK_PASS actors=" + str(len(required)))
