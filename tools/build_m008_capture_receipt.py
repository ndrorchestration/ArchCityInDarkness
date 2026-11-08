#!/usr/bin/env python3
"""Create a local M008 PNG evidence receipt. Never asserts native gameplay success.

Validates bytes/metadata and records a human attestation. A PNG plus metadata
cannot independently prove it came from Unreal, or that a game interaction
worked. This tool does not launch Unreal or access the network.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[1]
SAVED = Path("Saved/ArchCityVerification/M008")
MAP = "/Game/ArchCity/Review/Glassbend_Prelude_Greybox"
ROLES = ("arrival", "receipt_before", "receipt_after", "out_of_range", "occluded")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 50 * 1024 * 1024


def inspect_png(data: bytes) -> tuple[int, int]:
    """Validate PNG chunk structure/CRC and dimensions; not an image decoder."""
    if len(data) < 60 or data[:8] != PNG_MAGIC:
        raise ValueError("Missing PNG signature or file too short")
    cursor = 8
    width = height = 0
    saw_idat = False
    saw_iend = False
    chunks = 0
    while cursor + 12 <= len(data):
        size = struct.unpack_from(">I", data, cursor)[0]
        end = cursor + size + 12
        if end > len(data):
            raise ValueError("Truncated PNG chunk")
        kind = data[cursor + 4:cursor + 8]
        payload = data[cursor + 8:cursor + 8 + size]
        crc_expected = struct.unpack_from(">I", data, cursor + 8 + size)[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc_expected:
            raise ValueError("PNG chunk CRC mismatch")
        if chunks == 0:
            if kind != b"IHDR" or size != 13:
                raise ValueError("First PNG chunk must be 13-byte IHDR")
            width, height = struct.unpack_from(">II", payload, 0)
            if width < 1280 or height < 720 or width > 16384 or height > 16384:
                raise ValueError("Screenshot resolution outside 1280x720–16384x16384")
        elif kind == b"IHDR":
            raise ValueError("Duplicate PNG IHDR")
        if kind == b"IDAT":
            saw_idat = True
        if kind == b"IEND":
            if size != 0 or end != len(data):
                raise ValueError("Invalid IEND or trailing PNG bytes")
            saw_iend = True
            break
        chunks += 1
        cursor = end
    if not saw_idat or not saw_iend:
        raise ValueError("PNG must contain IDAT and final IEND")
    return width, height


def within_saved(project_root: Path, candidate: Path) -> tuple[Path, str]:
    """Restrict inspected files to an isolated checkout's ignored Saved folder."""
    root = (project_root / "Saved").resolve()
    path = candidate.resolve()
    try:
        rel = path.relative_to(root)
    except ValueError as exc:
        raise ValueError("Evidence file must be located under project Saved/") from exc
    if not rel.parts:
        raise ValueError("Evidence path cannot be the Saved directory")
    return path, str(Path("Saved") / rel).replace("\\", "/")


def collect_image(project_root: Path, role: str, candidate: Path) -> dict:
    if role not in ROLES:
        raise ValueError(f"Unexpected screenshot role: {role}")
    path, rel = within_saved(project_root, candidate)
    if path.suffix.lower() != ".png" or not path.is_file():
        raise ValueError(f"Missing PNG evidence for {role}")
    size = path.stat().st_size
    if size > MAX_BYTES:
        raise ValueError(f"PNG larger than {MAX_BYTES} bytes: {role}")
    data = path.read_bytes()
    width, height = inspect_png(data)
    return {
        "role": role, "path": rel,
        "bytes": len(data), "width": width, "height": height,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def build_receipt(project_root: Path, shots: dict[str, Path],
                  engine_version: dict, head: str, branch: str,
                  attested: bool, log: Path | None = None) -> dict:
    if not attested:
        raise ValueError("Human must explicitly attest to native PIE screenshot origin")
    version = tuple(engine_version.get(k) for k in ("MajorVersion", "MinorVersion", "PatchVersion"))
    if version != (5, 8, 4):
        raise ValueError(f"Expected Unreal 5.8.4, found {version!r}")
    if len(head) != 40 or any(c not in "0123456789abcdef" for c in head.lower()):
        raise ValueError("Expected full 40-character Git SHA")
    if not branch or branch == "main":
        raise ValueError("Only an isolated named review branch is allowed")
    if not shots or len(shots) != len(set(shots)) or any(k not in ROLES for k in shots):
        raise ValueError("Provide distinct known screenshot roles")
    captures = [collect_image(project_root, role, shots[role]) for role in ROLES if role in shots]
    if len({entry["sha256"] for entry in captures}) != len(captures):
        raise ValueError("Identical image bytes used for multiple roles")
    log_entry = None
    if log is not None:
        path, rel = within_saved(project_root, log)
        if not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError("Missing or oversized log")
        log_entry = {"path": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    return {
        "schema": 1,
        "evidence_type": "M008_NATIVE_PIE_OPERATOR_ATTESTED_NOT_INDEPENDENTLY_VERIFIED",
        "review_status": "CAPTURE_SET_COMPLETE_UNREVIEWED"
                         if len(captures) == len(ROLES) else "CAPTURE_SET_INCOMPLETE",
        "not_a_gameplay_pass": True,
        "generated_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_head": head, "branch": branch, "engine_version": "5.8.4", "map": MAP,
        "operator_attested_native_pie": True,
        "captures": captures,
        "missing_roles": [r for r in ROLES if r not in shots],
        "log": log_entry,
        "limitations": (
            "PNG structure/bytes/hash plus human attestation only. Does not independently "
            "prove GPU/PIE origin, controls, line-of-sight, quest state, or milestone pass."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--engine-build-version", type=Path, required=True,
                        help="Real UE Engine/Build/Build.version JSON file")
    parser.add_argument("--shot", action="append", required=True, metavar="ROLE=PNG",
                        help="Repeat with roles: " + ", ".join(ROLES))
    parser.add_argument("--log", type=Path, help="Optional local native Editor log under Saved/")
    parser.add_argument("--output", type=Path, help="New JSON file under project Saved/")
    parser.add_argument("--attest-native-pie", action="store_true",
                        help="Human attests captures came from actual native GPU PIE")
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    shots = {}
    for item in args.shot:
        if "=" not in item:
            parser.error("--shot expects ROLE=PNG")
        role, value = item.split("=", 1)
        if role in shots:
            parser.error(f"Duplicate role: {role}")
        shots[role] = Path(value)
    try:
        head = subprocess.check_output(["git", "-C", str(project_root), "rev-parse", "HEAD"],
                                       text=True).strip()
        branch = subprocess.check_output(["git", "-C", str(project_root), "branch",
                                          "--show-current"], text=True).strip()
        version = json.loads(args.engine_build_version.read_text(encoding="utf-8-sig"))
        receipt = build_receipt(project_root, shots, version, head, branch,
                                args.attest_native_pie, args.log)
        output = args.output or (project_root / SAVED / "capture_receipt.json")
        path, _ = within_saved(project_root, output)
        if path.exists():
            raise ValueError("Receipt already exists; choose a new output to preserve evidence")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print("EVIDENCE_RECEIPT_WRITTEN_NOT_PIE_PASS:", path)
        print("STATUS:", receipt["review_status"], "MISSING:", receipt["missing_roles"])
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print("EVIDENCE_RECEIPT_FAIL_CLOSED:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
