"""Synthetic source-layout fixtures; these do not run an Unreal level."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from validate_glassbend_layout import LAYOUT_PATH, QUEST_PATH, load_json, validate_layout


class GlassbendLayoutContract(unittest.TestCase):
    def setUp(self):
        self.layout = copy.deepcopy(load_json(LAYOUT_PATH))
        self.quest = copy.deepcopy(load_json(QUEST_PATH))

    def problems(self):
        return validate_layout(self.layout, self.quest)

    def test_review_layout_matches_quest(self):
        self.assertEqual(self.problems(), [])

    def test_actor_outside_assigned_zone_rejected(self):
        self.layout["actors"][0]["position_m"] = [2, 3]
        self.assertTrue(self.problems())

    def test_missing_quest_actor_rejected(self):
        self.layout["actors"].pop()
        self.assertTrue(self.problems())

    def test_duplicate_clue_spawn_rejected(self):
        self.layout["clue_spawns"].append(copy.deepcopy(self.layout["clue_spawns"][0]))
        self.assertTrue(self.problems())

    def test_overlapping_zones_rejected(self):
        self.layout["zones"][1]["center_m"] = list(self.layout["zones"][0]["center_m"])
        self.assertTrue(self.problems())

    def test_zone_extending_outside_bounds_rejected(self):
        self.layout["zones"][3]["center_m"] = [139, 80]
        self.assertTrue(self.problems())

    def test_broken_traversal_loop_rejected(self):
        self.layout["traversal_waypoints_m"][-1] = [80, 80]
        self.assertTrue(self.problems())

    def test_missing_camera_rejected(self):
        self.layout["camera_markers"].pop()
        self.assertTrue(self.problems())

    def test_invalid_camera_fov_rejected(self):
        self.layout["camera_markers"][0]["fov_degrees"] = 130
        self.assertTrue(self.problems())

    def test_render_cannot_be_claimed_without_native_capture(self):
        self.layout["visual_review"]["render_status"] = "PASS"
        self.assertTrue(self.problems())

    def test_wrong_scale_rejected(self):
        self.layout["cm_per_meter"] = 1
        self.assertTrue(self.problems())

    def test_quest_identifier_mismatch_rejected(self):
        self.layout["quest_id"] = "unrelated_quest"
        self.assertTrue(self.problems())


if __name__ == "__main__":
    unittest.main()
