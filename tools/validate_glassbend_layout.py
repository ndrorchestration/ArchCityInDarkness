#!/usr/bin/env python3
"""Static spatial consistency checks for a noncanonical Glassbend layout proposal.

No Unreal map, collision check, playable path, native build or GPU render is run.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT_PATH = ROOT / "Prototypes/Glassbend/layout_v1.json"
QUEST_PATH = ROOT / "Prototypes/Glassbend/the_unclaimed_hour.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def point(value, bounds, label, errors):
    if not isinstance(value, list) or len(value) != 2 or any(
        type(n) not in (int, float) or not math.isfinite(n) for n in value
    ):
        errors.append(f"{label}: expected two finite numeric coordinates")
        return None
    x, y = value
    if not (0 <= x <= bounds[0] and 0 <= y <= bounds[1]):
        errors.append(f"{label}: outside fictional layout bounds")
    return x, y


def entries(items, label, errors):
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        errors.append(f"{label}: expected object list")
        return {}
    result = {}
    for item in items:
        identity = item.get("id")
        if not isinstance(identity, str) or not identity or identity in result:
            errors.append(f"{label}: duplicate or invalid id {identity!r}")
        else:
            result[identity] = item
    return result


def within_zone(p, zone):
    x, y = p
    cx, cy = zone["center_m"]
    w, h = zone["size_m"]
    return abs(x - cx) <= w / 2 and abs(y - cy) <= h / 2


def validate_layout(layout: dict, quest: dict) -> list[str]:
    errors = []
    if not isinstance(layout, dict) or not isinstance(quest, dict):
        return ["Both layout and quest must be JSON objects"]
    if layout.get("schema_version") != 1 or layout.get("status") != "PROTOTYPE_NOT_CANON":
        errors.append("Layout must remain schema v1, noncanonical")
    if layout.get("quest_id") != quest.get("quest_id"):
        errors.append("Layout quest_id must match the source quest")
    if layout.get("units") != "meters" or layout.get("cm_per_meter") != 100:
        errors.append("Unreal scale convention must be 100 centimeters per meter")
    bounds = layout.get("bounds_m")
    if bounds != [140, 90]:
        errors.append("First-slice layout must retain reviewed 140m x 90m footprint")
        return errors
    point(layout.get("player_start_m"), bounds, "player_start", errors)
    if layout.get("player_proxy_height_cm") != 175:
        errors.append("Scale-review player proxy must be 175 cm")

    zones = entries(layout.get("zones"), "zones", errors)
    if set(zones) != {"shelter", "archive", "alley", "annex", "overlook"}:
        errors.append("Unexpected first-slice zone IDs")
    valid_zones = {}
    for name, zone in zones.items():
        center = point(zone.get("center_m"), bounds, f"zone {name} center", errors)
        size = zone.get("size_m")
        if center is None or not isinstance(size, list) or len(size) != 2 or any(
            type(n) not in (int, float) or not math.isfinite(n) or n <= 0 for n in size
        ):
            errors.append(f"zone {name}: invalid extent")
            continue
        if center[0] - size[0] / 2 < 0 or center[0] + size[0] / 2 > bounds[0] or (
            center[1] - size[1] / 2 < 0 or center[1] + size[1] / 2 > bounds[1]
        ):
            errors.append(f"zone {name}: footprint crosses layout boundary")
        valid_zones[name] = zone

    zone_list = list(valid_zones.items())
    for i, (name, zone) in enumerate(zone_list):
        for other_name, other in zone_list[i + 1:]:
            dx = abs(zone["center_m"][0] - other["center_m"][0])
            dy = abs(zone["center_m"][1] - other["center_m"][1])
            if dx < (zone["size_m"][0] + other["size_m"][0]) / 2 and (
                dy < (zone["size_m"][1] + other["size_m"][1]) / 2
            ):
                errors.append(f"Zone footprints overlap: {name} / {other_name}")

    for label, key, reference in (
        ("actors", "actors", quest.get("actors")),
        ("clues", "clue_spawns", quest.get("clues")),
    ):
        things = entries(layout.get(key), key, errors)
        expected = {item["id"] for item in reference if isinstance(item, dict) and "id" in item} if isinstance(reference, list) else set()
        if set(things) != expected:
            errors.append(f"{label}: ID mismatch against source quest")
        for name, item in things.items():
            zone_name = item.get("zone")
            if zone_name not in valid_zones:
                errors.append(f"{label} {name}: unrecognized zone")
                continue
            loc = point(item.get("position_m"), bounds, f"{label} {name}", errors)
            if loc is not None and not within_zone(loc, valid_zones[zone_name]):
                errors.append(f"{label} {name}: outside assigned zone")
            if label == "actors":
                radius = item.get("interaction_radius_m")
                if type(radius) not in (int, float) or not (1 <= radius <= 3):
                    errors.append(f"actor {name}: interaction radius must be 1–3 m")

    waypoints = layout.get("traversal_waypoints_m")
    if not isinstance(waypoints, list) or len(waypoints) < 6:
        errors.append("Traversal review loop needs at least six coordinate points")
    else:
        coordinates = [point(p, bounds, "traversal waypoint", errors) for p in waypoints]
        if all(p is not None for p in coordinates):
            if coordinates[0] != coordinates[-1]:
                errors.append("Traversal review waypoints do not close the proposed loop")
            for a, b in zip(coordinates, coordinates[1:]):
                length = math.dist(a, b)
                if not 0.5 <= length <= 55:
                    errors.append("Traversal waypoint edge is degenerate or longer than 55 m")

    cameras = entries(layout.get("camera_markers"), "camera_markers", errors)
    if set(cameras) != {"arrival", "archive", "alley", "overlook"}:
        errors.append("Four required native review camera IDs are missing or extra")
    for name, camera in cameras.items():
        eye = point(camera.get("position_m"), bounds, f"camera {name}", errors)
        target = point(camera.get("look_at_m"), bounds, f"camera {name} target", errors)
        fov = camera.get("fov_degrees")
        if type(fov) not in (int, float) or not (35 <= fov <= 80):
            errors.append(f"camera {name}: FOV must be 35–80 degrees")
        if eye is not None and target is not None and eye == target:
            errors.append(f"camera {name}: zero-length look direction")

    visual = layout.get("visual_review")
    if not isinstance(visual, dict) or visual.get("target_resolution") != [1920, 1080] or (
        visual.get("render_status") != "NOT_RENDERED"
    ):
        errors.append("Render evidence must remain NOT_RENDERED with 1080p review target")
    return errors


def main() -> int:
    problems = validate_layout(load_json(LAYOUT_PATH), load_json(QUEST_PATH))
    for problem in problems:
        print("FAIL:", problem)
    if problems:
        return 1
    print("PASS: fictional layout IDs, scale, spatial bounds and camera contract (source only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
