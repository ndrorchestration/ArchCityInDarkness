#!/usr/bin/env python3
"""Validate ACID-HIP-001 task payloads offline, using only the standard library.

Usage: python validate-handoff.py PAYLOAD [--schema SCHEMA]
Exit 0: conforms; exit 1: invalid payload; exit 2: input/schema/CLI error.
The default schema is resolved beside this script, not relative to the CWD.

This implements ONLY the schema keywords listed below, not general JSON Schema.
Unsupported schema keywords and malformed schemas fail closed, even in unused
branches. No network access, package installation, commands, or writes occur.
A passing document establishes shape/declared bounds only: not authorization,
actual permission enforcement, runtime readiness, or independent review.
"""

import argparse
import json
import math
from pathlib import Path
import re
import sys


ANNOTATIONS = {"$schema", "title", "description", "$comment"}
KEYWORDS = ANNOTATIONS | {
    "type", "properties", "required", "additionalProperties", "items",
    "minItems", "maxItems", "uniqueItems", "minLength", "pattern",
    "minimum", "maximum", "enum",
}
TYPES = {"object", "array", "string", "number", "integer", "boolean", "null"}


def reject_constant(value):
    raise ValueError("non-JSON numeric constant: " + value)


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("non-finite JSON number")
    significand = value.lower().split("e", 1)[0]
    if result == 0.0 and any(char in "123456789" for char in significand):
        raise ValueError("JSON number underflows floating point")
    return result


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key: " + key)
        result[key] = value
    return result


def load_json(path):
    with path.open(encoding="utf-8") as source:
        return json.load(source, object_pairs_hook=unique_object,
                         parse_constant=reject_constant, parse_float=finite_float)


def matches_type(value, kind):
    return {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": type(value) in (int, float),
        "integer": type(value) is int or (
            type(value) is float and value.is_integer()),
        "boolean": type(value) is bool,
        "null": value is None,
    }[kind]


def check_schema(schema, path="$schema"):
    if not isinstance(schema, dict):
        raise ValueError(path + ": schema must be an object")
    unknown = set(schema) - KEYWORDS
    if unknown:
        raise ValueError(path + ": unsupported keywords: " + ", ".join(sorted(unknown)))
    kind = schema.get("type")
    if not isinstance(kind, str) or kind not in TYPES:
        raise ValueError(path + ": one explicit supported type is required")
    for key in ANNOTATIONS & set(schema):
        if not isinstance(schema[key], str):
            raise ValueError(path + ": " + key + " must be a string")
    if "$schema" in schema and schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError(path + ": unsupported schema dialect")
    groups = {
        "object": {"properties", "required", "additionalProperties"},
        "array": {"items", "minItems", "maxItems", "uniqueItems"},
        "string": {"minLength", "pattern"},
        "number": {"minimum", "maximum"},
        "integer": {"minimum", "maximum"},
        "boolean": set(), "null": set(),
    }
    wrong = set(schema) - ANNOTATIONS - {"type", "enum"} - groups[kind]
    if wrong:
        raise ValueError(path + ": keywords incompatible with type: " + ", ".join(sorted(wrong)))
    for key in ("minItems", "maxItems", "minLength"):
        if key in schema and (type(schema[key]) is not int or schema[key] < 0):
            raise ValueError(path + ": " + key + " must be a nonnegative integer")
    for key in ("minimum", "maximum"):
        if key in schema and not matches_type(schema[key], "number"):
            raise ValueError(path + ": " + key + " must be a number")
    for low, high in (("minItems", "maxItems"), ("minimum", "maximum")):
        if low in schema and high in schema and schema[low] > schema[high]:
            raise ValueError(path + ": contradictory bounds")
    if "enum" in schema:
        if not isinstance(schema["enum"], list) or not schema["enum"]:
            raise ValueError(path + ": enum must be a nonempty array")
        if any(not matches_type(v, kind) for v in schema["enum"]):
            raise ValueError(path + ": enum values must match type")
    if "pattern" in schema:
        if not isinstance(schema["pattern"], str):
            raise ValueError(path + ": pattern must be a string")
        re.compile(schema["pattern"])
    if kind == "object":
        properties = schema.get("properties")
        required = schema.get("required")
        if not isinstance(properties, dict) or not isinstance(required, list):
            raise ValueError(path + ": properties and required are required")
        if any(not isinstance(key, str) for key in required):
            raise ValueError(path + ": required entries must be strings")
        if len(set(required)) != len(required) or not set(required) <= set(properties):
            raise ValueError(path + ": required entries must be unique declared properties")
        if schema.get("additionalProperties") is not False:
            raise ValueError(path + ": additionalProperties must explicitly be false")
        for key, child in properties.items():
            check_schema(child, path + ".properties." + key)
    if kind == "array":
        if type(schema.get("uniqueItems", False)) is not bool:
            raise ValueError(path + ": uniqueItems must be boolean")
        check_schema(schema.get("items"), path + ".items")


def validate(value, schema, path="$"):
    errors = []
    kind = schema["type"]
    if not matches_type(value, kind):
        return [path + ": expected " + kind]
    if "enum" in schema and value not in schema["enum"]:
        errors.append(path + ": value is not in enum")
    if kind == "object":
        for key in schema["required"]:
            if key not in value:
                errors.append(path + ": missing required property " + key)
        for key, item in value.items():
            if key not in schema["properties"]:
                errors.append(path + ": unexpected property " + key)
            else:
                errors.extend(validate(item, schema["properties"][key], path + "." + key))
    elif kind == "array":
        if len(value) < schema.get("minItems", 0):
            errors.append(path + ": too few items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(path + ": too many items")
        if schema.get("uniqueItems") and any(item in value[:i] for i, item in enumerate(value)):
            errors.append(path + ": duplicate array items")
        for i, item in enumerate(value):
            errors.extend(validate(item, schema["items"], path + "[" + str(i) + "]"))
    elif kind == "string":
        if len(value) < schema.get("minLength", 0):
            errors.append(path + ": string is too short")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(path + ": string does not match pattern")
    elif kind in ("number", "integer"):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(path + ": number below minimum")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(path + ": number above maximum")
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", type=Path)
    parser.add_argument("--schema", type=Path,
                        default=Path(__file__).resolve().with_name("handoff-schema.json"))
    args = parser.parse_args(argv)
    try:
        schema = load_json(args.schema)
        check_schema(schema)
        payload = load_json(args.payload)
        errors = validate(payload, schema)
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError, re.error) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print("INVALID: " + error, file=sys.stderr)
        return 1
    print("VALID: " + str(args.payload) + " (data contract only; not authorization)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
