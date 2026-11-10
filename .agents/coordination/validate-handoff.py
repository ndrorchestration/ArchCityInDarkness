"""ACID-HIP-002 pilot handoff validator (standard library only).

This is an explicit pilot policy subset, NOT a general JSON Schema validator,
a filesystem sandbox, a permission grant, or evidence of autonomous execution.
"""
import json
import re
import sys
from pathlib import Path, PurePosixPath

SHA_RE = re.compile(r"[0-9a-fA-F]{40}\Z")
TASK_RE = re.compile(r"ACID-HIP-[0-9]{3,}\Z")
REPO_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
STATES = {"TODO", "IN_PROGRESS", "DONE", "BLOCKED", "NEEDS_HERALD", "NEEDS_ENDER"}
ALLOWED_PREFIX = ".agents/coordination/"

def meaningful(value):
    return isinstance(value, str) and bool(value.strip())

def safe_pilot_path(value):
    if not meaningful(value) or value != value.strip():
        return False
    if "\\" in value or ":" in value or value.startswith("/") or "\x00" in value:
        return False
    if value == ALLOWED_PREFIX:
        return True
    if not value.startswith(ALLOWED_PREFIX):
        return False
    # Reject traversal, . segments, duplicate separators and inconsistent normalization.
    parts = value.split("/")
    if any(part in ("", ".", "..") for part in parts[:-1]):
        return False
    if parts[-1] in (".", ".."):
        return False
    return str(PurePosixPath(value)) == value.rstrip("/") and bool(parts[-1])

def validate(schema, obj):
    errors = []
    if not isinstance(schema, dict) or not isinstance(schema.get("properties"), dict):
        return ["invalid schema: expected properties object"]
    if not isinstance(obj, dict):
        return ["payload must be an object"]
    properties = schema["properties"]
    required = schema.get("required", [])
    for key in required:
        if key not in obj:
            errors.append(f"missing required field: {key}")
    for key in obj:
        if key not in properties:
            errors.append(f"unknown field: {key}")

    for key in ("task_id", "owner", "reviewer", "repository", "base_sha", "objective"):
        if key in obj and not meaningful(obj[key]):
            errors.append(f"{key}: must be a nonblank string")
    if meaningful(obj.get("task_id")) and not TASK_RE.fullmatch(obj["task_id"]):
        errors.append("task_id: invalid ACID-HIP namespace")
    if meaningful(obj.get("repository")) and not REPO_RE.fullmatch(obj["repository"]):
        errors.append("repository: malformed owner/name")
    for key in ("base_sha", "head_sha"):
        value = obj.get(key)
        if key == "head_sha" and value is None:
            continue
        if key in obj and (not isinstance(value, str) or not SHA_RE.fullmatch(value)):
            errors.append(f"{key}: must be a 40-character commit SHA")

    if "status" in obj and (not isinstance(obj["status"], str) or obj["status"] not in STATES):
        errors.append("status: invalid state")

    for key in ("allowed_paths", "acceptance_criteria"):
        if key not in obj:
            continue
        value = obj[key]
        if not isinstance(value, list) or not value:
            errors.append(f"{key}: must be a nonempty array")
            continue
        if key == "allowed_paths":
            if len(value) != len(set(map(json.dumps, value))):
                errors.append("allowed_paths: duplicate entries")
            for idx, item in enumerate(value):
                if not safe_pilot_path(item):
                    errors.append(f"allowed_paths[{idx}]: unsafe or out-of-scope path")
        else:
            for idx, item in enumerate(value):
                if not meaningful(item):
                    errors.append(f"acceptance_criteria[{idx}]: must be nonblank")

    if "max_cost_usd" in obj:
        cost = obj["max_cost_usd"]
        if type(cost) not in (int, float) or not 0 <= cost <= 0:
            errors.append("max_cost_usd: pilot permits exactly 0")

    evidence = obj.get("evidence", [])
    if "evidence" in obj and not isinstance(evidence, list):
        errors.append("evidence: must be an array")
        evidence = []
    if isinstance(evidence, list):
        for i, entry in enumerate(evidence):
            if not isinstance(entry, dict):
                errors.append(f"evidence[{i}]: must be object")
                continue
            for field in ("command", "exit_code", "output"):
                if field not in entry:
                    errors.append(f"evidence[{i}]: missing {field}")
            for field in entry:
                if field not in ("command", "exit_code", "output"):
                    errors.append(f"evidence[{i}]: unknown {field}")
            if "command" in entry and not meaningful(entry["command"]):
                errors.append(f"evidence[{i}].command: must be nonblank")
            if "output" in entry and not meaningful(entry["output"]):
                errors.append(f"evidence[{i}].output: must be nonblank")
            if "exit_code" in entry and type(entry["exit_code"]) is not int:
                errors.append(f"evidence[{i}].exit_code: must be integer")

    if obj.get("status") == "DONE":
        if not isinstance(obj.get("head_sha"), str) or not SHA_RE.fullmatch(obj["head_sha"]):
            errors.append("DONE requires valid pinned head_sha")
        if not isinstance(evidence, list) or not evidence:
            errors.append("DONE requires nonempty command evidence")
    return errors

def main():
    if len(sys.argv) != 3:
        print("usage: python validate-handoff.py SCHEMA PAYLOAD", file=sys.stderr)
        return 2
    try:
        schema = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        payload = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 2
    errors = validate(schema, payload)
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: ACID-HIP pilot handoff checks")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
