"""Portable manifest safeguards, not Daz/Unreal-native verification."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from validate_art_pilot import DEFAULT, validate_manifest


class ArtPilotContract(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(DEFAULT.read_text(encoding="utf-8"))

    def assert_blocked(self, reason):
        self.assertTrue(
            validate_manifest(self.data),
            f"{reason}: expected fail-closed, but manifest was accepted"
        )

    def test_original_v1_manifest(self):
        self.assertEqual(validate_manifest(self.data), [])
        self.assertEqual(self.data["readiness"], "BLOCKED")

    def test_wrong_project(self):
        self.data["project"] = "ToSailTheStarrySky"
        self.assert_blocked("no cross-project art")

    def test_wrong_character(self):
        self.data["character"]["id"] = "rowan_hulett"
        self.assert_blocked("no private roleplay character")

    def test_premature_canon(self):
        self.data["status"] = "APPROVED_CANON"
        self.assert_blocked("noncanonical")

    def test_premature_production(self):
        self.data["readiness"] = "READY"
        self.assert_blocked("production gated")

    def test_missing_camera(self):
        self.data["visual_contract"]["views"].remove("full_body")
        self.assert_blocked("view set")

    def test_missing_lighting_quality(self):
        self.data["visual_contract"]["criteria"].remove("physically_plausible_lighting")
        self.assert_blocked("cinematic quality")

    def test_missing_scale_quality(self):
        self.data["visual_contract"]["criteria"].remove("believable_scale_and_curvature")
        self.assert_blocked("scale")

    def test_inconsistent_lens(self):
        self.data["visual_contract"]["matched_focal_length_mm"] = 24
        self.assert_blocked("matched camera")

    def test_duplicate_daz_candidate(self):
        self.data["candidates"][1] = copy.deepcopy(self.data["candidates"][0])
        self.assert_blocked("distinct candidates")

    def test_missing_metahuman_candidate(self):
        self.data["candidates"] = self.data["candidates"][:1]
        self.assert_blocked("comparison required")

    def test_misrepresented_bridge(self):
        self.data["candidates"][0]["bridge_status"] = "NOT_APPLICABLE"
        self.assert_blocked("Daz bridge cannot be skipped")

    def test_false_license_assertion(self):
        self.data["candidates"][0]["license_status"] = "INTERACTIVE_VERIFIED"
        self.assert_blocked("rights evidence must exist")

    def test_rights_evidence_without_source_review(self):
        self.data["candidates"][0]["license_status"] = "INTERACTIVE_VERIFIED"
        self.data["candidates"][0]["license_evidence"] = ["provider terms reviewed"]
        self.assert_blocked("source provenance required")

    def test_native_pass_missing_captures(self):
        self.data["candidates"][0]["native_import"] = "PASS"
        self.assert_blocked("native screenshots required")

    def test_fake_capture_before_native_run(self):
        self.data["candidates"][0]["gpu_captures"] = ["uncorroborated_image.png"]
        self.assert_blocked("no unverified render promotion")

    def test_invented_creator_approval(self):
        self.data["candidates"][0]["creator_approval"] = True
        self.assert_blocked("no invented approval")

    def test_no_private_larp_constraint(self):
        self.data["constraints"]["no_private_larp_assets"] = False
        self.assert_blocked("privacy boundary")

    def test_do_not_interrupt_installer_constraint(self):
        self.data["constraints"]["do_not_interrupt_install_manager"] = False
        self.assert_blocked("installer is user-owned")

    def test_no_unlicensed_geometry_constraint(self):
        self.data["constraints"]["no_unlicensed_interactive_geometry"] = False
        self.assert_blocked("licenses required")

    def test_read_only_powershell_guard_source(self):
        script = (ROOT / "tools" / "Get-ArtPilotReadiness.ps1").read_text(encoding="utf-8")
        self.assertIn("ConvertTo-Json", script)
        self.assertIn("production_import_authorized = $false", script)
        self.assertIn("Get-CimInstance", script)
        self.assertIn("DAZ3DIM", script)
        for command in (
            "Start-Process ", "Stop-Process ", "Remove-Item ", "New-Item ",
            "Copy-Item ", "Move-Item ", "Invoke-WebRequest", "Invoke-RestMethod",
            "git clone", "msiexec", "taskkill", "npm install",
        ):
            self.assertNotIn(command, script, "Environment probe must remain read-only")

    def test_licenses_can_be_documented_without_granting_import(self):
        daz = self.data["candidates"][0]
        daz["source_content"] = "VERIFIED_ORIGINAL"
        daz["license_status"] = "INTERACTIVE_VERIFIED"
        daz["license_evidence"] = ["internal-license-review-id"]
        self.assertEqual(validate_manifest(self.data), [])
        self.assertEqual(self.data["readiness"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
