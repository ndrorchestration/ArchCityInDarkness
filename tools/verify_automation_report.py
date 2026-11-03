#!/usr/bin/env python3
"""Fail-closed verification of a real Unreal native automation report."""
import argparse
import json
import re
import sys
from pathlib import Path

TEST = "ArchCityInDarkness.Survival.Hunger.Contract"


def verify(report: Path, log: Path, expected: str = TEST) -> list[str]:
    errors = []
    if not report.is_file() or not log.is_file():
        return ["Missing Unreal report index.json or native Editor log"]
    try:
        data = json.loads(report.read_text(encoding="utf-8-sig"))
        text = log.read_text(encoding="utf-8-sig", errors="replace")
    except (OSError, UnicodeError, ValueError) as exc:
        return [f"Cannot read evidence: {exc}"]
    if not isinstance(data, dict):
        return ["Report must be a JSON object"]
    for key in ("succeeded", "failed", "notRun"):
        value = data.get(key)
        if type(value) is not int or value < 0:
            errors.append(f"Missing or invalid count: {key}")
    for key in ("failed", "notRun", "inProcess"):
        value = data.get(key, 0)
        if type(value) is int and value:
            errors.append(f"{key}={value}")
    if type(data.get("succeeded")) is int and data["succeeded"] < 1:
        errors.append("No successful tests")
    tests = data.get("tests")
    if not isinstance(tests, list):
        errors.append("Missing tests array")
        tests = []
    matched = [t for t in tests if isinstance(t, dict) and t.get("fullTestPath") == expected]
    if len(matched) != 1 or matched[0].get("state") != "Success":
        errors.append("Expected exactly one successful named native test")
    markers = re.findall(r"\*{4}\s*TEST COMPLETE\.\s*EXIT CODE:\s*(-?\d+)\s*\*{4}", text)
    if markers != ["0"]:
        errors.append(f"Missing/failed TEST COMPLETE marker: {markers}")
    completions = re.findall(r"Test Completed\.\s*Result=\{?(\w+)\}?.*?Path=\{?([^\s}]+)", text)
    match_states = [state for state, path in completions if path == expected]
    if match_states != ["Success"]:
        errors.append(f"Missing/failed target Test Completed event: {match_states}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--test", default=TEST)
    args = ap.parse_args()
    problems = verify(args.report, args.log, args.test)
    for problem in problems:
        print("FAIL_CLOSED:", problem, file=sys.stderr)
    if problems:
        return 1
    print("PASS: named Unreal test demonstrated by report and native log")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
