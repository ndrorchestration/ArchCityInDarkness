#!/usr/bin/env python3
"""Portable, source-only quest contract for an original *proposal*.
Not an Unreal import, runtime simulator, gameplay assertion, or canonical story.
"""
import argparse
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "Prototypes" / "Glassbend" / "the_unclaimed_hour.json"
EXPECTED_ROUTES = {"dialogue", "stealth", "confrontation"}


def load_quest(path: Path = DEFAULT_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Quest root must be an object")
    return data


def validate_quest(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != 1 or data.get("status") != "PROTOTYPE_NOT_CANON":
        errors.append("Quest must be schema v1 and remain noncanonical")
    if data.get("quest_id") != "the_unclaimed_hour":
        errors.append("Unexpected quest id")
    if data.get("phases") != ["NotStarted", "Investigating", "Resolved"]:
        errors.append("Unknown quest state machine")
    if data.get("initial_phase") != "Investigating" or data.get("terminal_phase") != "Resolved":
        errors.append("Unexpected first-slice phase contract")
    actors = data.get("actors")
    if not isinstance(actors, list) or len(actors) != 3:
        errors.append("Exactly three original prototype actors required")
    else:
        ids = [a.get("id") for a in actors if isinstance(a, dict)]
        if len(ids) != 3 or len(set(ids)) != 3 or any(not x for x in ids):
            errors.append("Actor ids must be unique and nonempty")
    clues = data.get("clues")
    if not isinstance(clues, list) or not clues:
        errors.append("Clues must be a nonempty list")
        clues = []
    clue_ids = [c.get("id") for c in clues if isinstance(c, dict)]
    if len(clue_ids) != len(clues) or len(clue_ids) != len(set(clue_ids)):
        errors.append("Clue ids must be unique objects")
    for clue in clues:
        if not isinstance(clue, dict) or not clue.get("id") or clue.get("requires") != []:
            errors.append("All first-slice clues must have a no-prerequisite acquisition path")
    routes = data.get("routes")
    if not isinstance(routes, list):
        errors.append("Routes must be a list")
        routes = []
    routes_by_id = {}
    outcomes = set()
    for route in routes:
        if not isinstance(route, dict):
            errors.append("Invalid route object")
            continue
        route_id = route.get("id")
        if route_id in routes_by_id:
            errors.append("Route ids not unique")
        routes_by_id[route_id] = route
        required = route.get("requires")
        if not isinstance(required, list) or not set(required).issubset(set(clue_ids)):
            errors.append(f"Unknown required clue in {route_id}")
        if not route.get("evidence") or not isinstance(route.get("evidence"), str):
            errors.append(f"Missing evidence in {route_id}")
        outcome = (route.get("trust_delta"), route.get("exposure_delta"), route.get("evidence"))
        if outcome in outcomes:
            errors.append("Duplicate route consequences")
        outcomes.add(outcome)
        if route.get("requires_violence") is not False or route.get("forced_feeding") is not False:
            errors.append(f"Route {route_id} forces violence or feeding")
        for key in ("trust_delta", "exposure_delta", "hunger_delta"):
            if type(route.get(key)) is not int:
                errors.append(f"{route_id}: {key} must be an integer")
        if route.get("hunger_delta") != 0:
            errors.append(f"{route_id}: no automatic hunger mutation allowed")
    if set(routes_by_id) != EXPECTED_ROUTES or len(routes) != 3:
        errors.append("Prototype must provide exactly three different resolution routes")
    required_constraints = {
        "all_routes_nonlethal": True, "no_required_feeding": True,
        "repeated_resolution": "NO_OP", "failure_allows_retry": True
    }
    if data.get("constraints") != required_constraints:
        errors.append("Nonlethal, replay and retry safeguards missing")
    return errors


def resolve(data: dict, state: dict, route_id: str, obtained_clues: set[str]) -> dict:
    """Pure reference transition; Unreal state/save integration is NOT implemented."""
    result = dict(state)
    if result.get("phase") == "Resolved":
        return result
    if result.get("phase") != "Investigating":
        raise ValueError("Quest is not active")
    route = next((r for r in data["routes"] if r["id"] == route_id), None)
    if route is None:
        raise ValueError("Unknown route")
    if not set(route["requires"]).issubset(obtained_clues):
        return result  # Missing clues cannot soft-lock the player.
    result.update({
        "phase": "Resolved",
        "evidence_acquired": True,
        "resolution_method": route_id,
        "evidence": route["evidence"],
        "mara_trust": result.get("mara_trust", 0) + route["trust_delta"],
        "public_exposure": max(0, min(100, result.get("public_exposure", 0) + route["exposure_delta"])),
        "hunger": result.get("hunger", 25) + route["hunger_delta"],
    })
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path, nargs="?", default=DEFAULT_PATH)
    args = ap.parse_args()
    errors = validate_quest(load_quest(args.path))
    for problem in errors:
        print("FAIL:", problem)
    if errors:
        return 1
    print("PASS: original quest proposal schema, routes, and safe transitions (source only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
