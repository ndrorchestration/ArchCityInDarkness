#!/usr/bin/env python3
"""Validate an original character pilot; never claim a native render or license from metadata."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "ArtPipeline" / "MaraVale" / "art_pilot_v1.json"
VIEWS = {
    "front_portrait", "three_quarter_portrait", "profile_portrait",
    "full_body", "neutral_expression"
}
CRITERIA = {
    "believable_scale_and_curvature", "physically_plausible_lighting",
    "intentional_cinematic_framing", "atmospheric_depth",
    "readable_visual_contrast", "hair_and_clothing_articulation",
    "animation_and_skeleton_readiness", "frame_time_and_memory_budget"
}
CANDIDATES = {"daz": "DAZ_STUDIO_6", "metahuman": "METAHUMAN"}
REQUIRED_LIMITS = {
    "no_private_larp_assets", "no_unlicensed_interactive_geometry",
    "no_production_asset_import", "do_not_interrupt_install_manager",
    "require_native_unreal_visual_evidence"
}


def _strings(seq):
    return isinstance(seq, list) and all(isinstance(s, str) for s in seq)


def validate_manifest(data: object) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["The pilot manifest must be a JSON object"]
    if (type(data.get("schema_version")) is not int or
            data.get("schema_version") != 1):
        errors.append("Schema version must be integer 1")
    if data.get("project") != "ArchCityInDarkness" or data.get("pilot_id") != "ART-PILOT-001":
        errors.append("Wrong project or art pilot identity")
    if data.get("status") != "PROTOTYPE_NOT_CANON":
        errors.append("Unreviewed original pilot may not be marked canon")
    if data.get("readiness") != "BLOCKED":
        errors.append("No source-only manifest may authorize production import")
    character = data.get("character")
    if not isinstance(character, dict) or any([
        character.get("id") != "mara_vale",
        character.get("name") != "Mara Vale",
        character.get("kind") != "ORIGINAL_FICTIONAL_NPC",
        character.get("visual_review") not in {"PENDING", "REJECTED", "APPROVED_FOR_REVIEW_ONLY"},
        character.get("reference_art") not in {"NOT_APPROVED", "CREATOR_APPROVED"}
    ]):
        errors.append("Original Mara Vale identity or review status invalid")
    visual = data.get("visual_contract")
    if not isinstance(visual, dict) or any([
        visual.get("engine_target") != "Unreal Engine 5.8",
        visual.get("resolution_px") != [1920, 1080],
        type(visual.get("matched_focal_length_mm")) is not int,
        visual.get("matched_focal_length_mm") != 50,
        not _strings(visual.get("views")),
        not _strings(visual.get("criteria"))
    ]):
        errors.append("Missing matched 1080p / 50 mm visual contract")
    else:
        if set(visual["views"]) != VIEWS or len(visual["views"]) != len(VIEWS):
            errors.append("Cinematic reference shots must include all five exact views")
        if set(visual["criteria"]) != CRITERIA or len(visual["criteria"]) != len(CRITERIA):
            errors.append("Realism, cinematic and performance criteria must all be represented")
    constraints = data.get("constraints")
    if not isinstance(constraints, dict) or set(constraints) != REQUIRED_LIMITS or any(
        constraints[k] is not True for k in REQUIRED_LIMITS if k in constraints
    ):
        errors.append("Safety, licensing, privacy or installer safeguards missing")
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 2:
        return errors + ["Both Daz and MetaHuman candidate slots required"]
    if {c.get("id") for c in candidates if isinstance(c, dict)} != set(CANDIDATES):
        errors.append("Exactly one Daz and one MetaHuman candidate required")
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("Invalid candidate object")
            continue
        name = candidate.get("id")
        if name not in CANDIDATES or candidate.get("pipeline") != CANDIDATES.get(name):
            errors.append("Pipeline ID/label mismatch")
        if candidate.get("source_content") not in {"NONE_SELECTED", "VERIFIED_ORIGINAL"}:
            errors.append("Source character assets must be absent or explicitly reviewed")
        rights = candidate.get("license_status")
        if rights not in {"UNVERIFIED", "RENDER_ONLY", "INTERACTIVE_VERIFIED"}:
            errors.append("Invalid asset rights scope")
        evidence = candidate.get("license_evidence")
        if not _strings(evidence):
            errors.append("License evidence must be a list of references")
            evidence = []
        if rights == "INTERACTIVE_VERIFIED" and (
            not evidence or candidate.get("source_content") != "VERIFIED_ORIGINAL"
        ):
            errors.append("Interactive rights cannot be claimed without provenance")
        if candidate.get("bridge_status") not in {
            "NOT_VERIFIED", "CHECKED_COMPATIBLE", "INCOMPATIBLE", "NOT_APPLICABLE"
        }:
            errors.append("Bridge status must be explicit")
        if name == "daz" and candidate.get("bridge_status") == "NOT_APPLICABLE":
            errors.append("Daz bridge must be investigated, not skipped")
        if name == "metahuman" and candidate.get("bridge_status") != "NOT_APPLICABLE":
            errors.append("MetaHuman slot does not use Daz bridge")
        state = candidate.get("native_import")
        captures = candidate.get("gpu_captures")
        if state not in {"NOT_RUN", "FAIL", "PASS"} or not _strings(captures):
            errors.append("Native verification state/capture manifest invalid")
            captures = []
        if state == "PASS" and len(captures) < len(VIEWS):
            errors.append("Native PASS requires five actually recorded camera captures")
        if state != "PASS" and captures:
            errors.append("Do not present GPU captures as verified before native PASS")
        if type(candidate.get("creator_approval")) is not bool:
            errors.append("Creator approval must be a boolean")
        elif candidate["creator_approval"] and (
            state != "PASS" or rights != "INTERACTIVE_VERIFIED" or
            len(captures) < len(VIEWS)
        ):
            errors.append("Creator approval cannot bypass native or rights gates")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", nargs="?", type=Path, default=DEFAULT)
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print("FAIL: could not read art pilot contract:", exc)
        return 1
    errors = validate_manifest(data)
    for e in errors:
        print("FAIL:", e)
    if errors:
        return 1
    print("PASS: original noncanonical art pilot manifest; Daz and MetaHuman import remain BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
