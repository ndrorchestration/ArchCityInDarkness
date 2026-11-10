"""ACID-HIP v0.1 offline subset validator; Python standard library only.
Validates the specific schema constraints used by the handoff fixture.
This is NOT a general-purpose JSON Schema implementation.
Usage: python validate-handoff.py schema.json payload.json
"""
import json
import re
import sys
from pathlib import Path

def validate(schema, obj):
    errors = []
    if not isinstance(obj, dict):
        return ["payload must be an object"]
    props = schema["properties"]
    for key in schema["required"]:
        if key not in obj:
            errors.append(f"missing required field: {key}")
    for key, value in obj.items():
        if key not in props:
            errors.append(f"unknown field: {key}")
            continue
        rule = props[key]
        if "enum" in rule and value not in rule["enum"]:
            errors.append(f"{key}: invalid enumeration")
        typ = rule.get("type")
        if typ == "string" and not isinstance(value, str):
            errors.append(f"{key}: expected string")
            continue
        if typ == "array" and not isinstance(value, list):
            errors.append(f"{key}: expected array")
            continue
        if typ == "number" and (isinstance(value, bool) or not isinstance(value, (int, float))):
            errors.append(f"{key}: expected number")
            continue
        if isinstance(typ, list) and not (value is None or isinstance(value, str)):
            errors.append(f"{key}: expected string or null")
            continue
        if isinstance(value, str):
            if len(value) < rule.get("minLength", 0):
                errors.append(f"{key}: too short")
            if rule.get("pattern") and re.fullmatch(rule["pattern"], value) is None:
                errors.append(f"{key}: format mismatch")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if value < rule.get("minimum", float("-inf")):
                errors.append(f"{key}: below minimum")
        if isinstance(value, list):
            if len(value) < rule.get("minItems", 0):
                errors.append(f"{key}: too few items")
            if rule.get("uniqueItems") and len(set(map(json.dumps, value))) != len(value):
                errors.append(f"{key}: duplicate items")
            itemrule = rule.get("items", {})
            for idx, item in enumerate(value):
                itemtype = itemrule.get("type")
                if itemtype == "string" and (not isinstance(item, str) or len(item) < itemrule.get("minLength", 0)):
                    errors.append(f"{key}[{idx}]: invalid string")
                if itemtype == "object":
                    if not isinstance(item, dict):
                        errors.append(f"{key}[{idx}]: expected object")
                        continue
                    for req in itemrule.get("required", []):
                        if req not in item:
                            errors.append(f"{key}[{idx}]: missing {req}")
                    for field, data in item.items():
                        spec = itemrule.get("properties", {}).get(field)
                        if spec is None:
                            errors.append(f"{key}[{idx}]: unknown field {field}")
                        elif spec["type"] == "integer" and (type(data) is not int):
                            errors.append(f"{key}[{idx}].{field}: expected integer")
                        elif spec["type"] == "string" and not isinstance(data, str):
                            errors.append(f"{key}[{idx}].{field}: expected string")
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
    errs = validate(schema, payload)
    for err in errs:
        print("FAIL:", err)
    if errs:
        return 1
    print("PASS: ACID-HIP handoff subset constraints validated")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
