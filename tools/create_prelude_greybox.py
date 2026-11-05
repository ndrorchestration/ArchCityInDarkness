import unreal

# Disposable, original geometry only. No production assets or story approval.
MAP = "/Game/ArchCity/Review/Glassbend_Prelude_Greybox"
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if unreal.EditorAssetLibrary.does_asset_exist(MAP):
    raise RuntimeError("Refusing to overwrite an existing review map")
if not levels.new_level(MAP):
    raise RuntimeError("Could not create review level")
cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
if not cube:
    raise RuntimeError("Engine cube missing")

def box(label, location, scale):
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*location))
    a.set_actor_label(label)
    a.static_mesh_component.set_static_mesh(cube)
    a.set_actor_scale3d(unreal.Vector(*scale))
    return a

# Engine cube is 100 cm on each side. Locations are in centimetres.
box("Walkable ground", (7000, 4500, -50), (140, 90, 1))
box("Archive facade", (6000, 3800, 250), (25, 1, 5))
box("Annex facade", (12300, 5000, 250), (28, 1, 5))
box("Shelter back", (2200, 800, 150), (10, .2, 3))
box("Shelter roof", (2200, 1200, 310), (10, 8, .2))
box("Overlook barrier", (6500, 8400, 55), (50, .3, 1.1))
start = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(2200, 2000, 120))
start.set_actor_label("Prelude arrival start")
for label, location in [("Shelter light", (2200,1200,300)),
                        ("Archive light", (6000,3300,300)),
                        ("Annex light", (12300,4500,300))]:
    light = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(*location))
    light.set_actor_label(label)
    light.point_light_component.set_editor_property("intensity", 8000.0)
if not levels.save_current_level():
    raise RuntimeError("Failed to save review level")
unreal.log("ARCHCITY_PRELUDE_GREYBOX_SAVED " + MAP)
