#!/usr/bin/env python3
"""Fail-closed, opt-in local save file for the noncanonical Python text preview.

This is NOT a UE USaveGame, a cryptographic authentication system, or proof
of in-engine persistence. SHA-256 detects accidental file changes only.
"""
import hashlib
import hmac
import json
import os
from pathlib import Path
import tempfile

from validate_quest_prototype import validate_quest

SCHEMA_VERSION = 1
MAX_SAVE_BYTES = 16 * 1024
STATE_FIELDS = frozenset({
    "phase", "clues", "route", "evidence", "mara_trust", "public_exposure", "hunger"
})
ENVELOPE_FIELDS = frozenset({"schema_version", "quest_id", "state", "sha256"})


def default_save_path() -> Path:
    """A private user-data location, never in the public development repository."""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME") or (Path.home() / ".local" / "share"))
    return base / "ArchCityInDarkness" / "GlassbendPreview" / "save_v1.json"


def _canonical(data: dict) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=False,
                      allow_nan=False, separators=(",", ":")).encode("utf-8")


def _exact_integer(value: object, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


def validate_state(state: object, quest: dict) -> list[str]:
    """Reject impossible states rather than silently repairing or migrating them."""
    errors: list[str] = []
    if validate_quest(quest):
        return ["Reference quest contract is invalid"]
    if not isinstance(state, dict) or set(state) != STATE_FIELDS:
        return ["State must be an exact version-1 object"]
    clue_ids = [c["id"] for c in quest["clues"]]
    clues = state["clues"]
    if not isinstance(clues, list) or any(not isinstance(x, str) for x in clues):
        return ["Clues must be an array of known string IDs"]
    if len(clues) != len(set(clues)) or any(x not in clue_ids for x in clues):
        errors.append("Unknown or duplicate clue ID")
    if clues != [x for x in clue_ids if x in clues]:
        errors.append("Clue order must match the stable quest contract")
    if not _exact_integer(state["hunger"], 0, 100):
        errors.append("Hunger must be an integer in [0,100]")
    if not _exact_integer(state["mara_trust"], -1, 1):
        errors.append("Mara trust outside supported quest outcomes")
    if not _exact_integer(state["public_exposure"], 0, 100):
        errors.append("Exposure outside [0,100]")
    phase = state["phase"]
    if phase == "Investigating":
        if any((
            state["route"] is not None,
            state["evidence"] is not None,
            state["mara_trust"] != 0,
            state["public_exposure"] != 0,
        )):
            errors.append("Investigating save contains resolved outcomes")
    elif phase == "Resolved":
        route = next((r for r in quest["routes"] if r["id"] == state["route"]), None)
        if route is None:
            errors.append("Unknown final route")
        elif not all((
            set(route["requires"]).issubset(set(clues)),
            state["evidence"] == route["evidence"],
            state["mara_trust"] == route["trust_delta"],
            state["public_exposure"] == route["exposure_delta"],
        )):
            errors.append("Resolved save contradicts exact route prerequisites/consequences")
    else:
        errors.append("Unsupported phase")
    return errors


def state_to_payload(state: object, quest: dict) -> dict:
    """Export a preview dataclass without serializing dialogue widgets or actors."""
    clues = getattr(state, "clues", None)
    if not isinstance(clues, set):
        raise ValueError("Preview state must contain a clue set")
    order = [c["id"] for c in quest["clues"]]
    result = {
        "phase": getattr(state, "phase", None),
        "clues": [name for name in order if name in clues],
        "route": getattr(state, "route", None),
        "evidence": getattr(state, "evidence", None),
        "mara_trust": getattr(state, "mara_trust", None),
        "public_exposure": getattr(state, "public_exposure", None),
        "hunger": getattr(state, "hunger", None),
    }
    if len(clues) != len(result["clues"]):
        raise ValueError("Refusing unknown clue in live preview state")
    problems = validate_state(result, quest)
    if problems:
        raise ValueError("Refusing invalid live preview state: " + "; ".join(problems))
    return result


def _envelope(payload: dict, quest: dict) -> dict:
    body = {"schema_version": SCHEMA_VERSION, "quest_id": quest["quest_id"],
            "state": payload}
    return {**body, "sha256": hashlib.sha256(_canonical(body)).hexdigest()}


def save_preview_state(path: Path, state: object, quest: dict) -> None:
    """Write only on explicit user request. Atomic replace; no implicit autosave."""
    payload = state_to_payload(state, quest)
    encoded = _canonical(_envelope(payload, quest)) + b"\n"
    if len(encoded) > MAX_SAVE_BYTES:
        raise ValueError("Save file exceeds size limit")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=path.parent, prefix=".glassbend-save-", suffix=".tmp",
            delete=False,
        ) as stream:
            temporary = Path(stream.name)
            os.chmod(temporary, 0o600)
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _reject_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON object key")
        result[key] = value
    return result


def _reject_constant(value: str):
    raise ValueError(f"Forbidden numeric value: {value}")


def load_preview_state(path: Path, quest: dict) -> dict:
    """Parse and validate, returning a new payload without changing the live game."""
    path = Path(path)
    with path.open("rb") as stream:
        content = stream.read(MAX_SAVE_BYTES + 1)
    if len(content) > MAX_SAVE_BYTES:
        raise ValueError("Save file exceeds size limit")
    try:
        envelope = json.loads(content.decode("utf-8"), object_pairs_hook=_reject_duplicates,
                              parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Unreadable local preview save") from exc
    if not isinstance(envelope, dict) or set(envelope) != ENVELOPE_FIELDS:
        raise ValueError("Unexpected save envelope fields")
    if type(envelope["schema_version"]) is not int or envelope["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Unsupported local preview schema")
    if envelope["quest_id"] != quest.get("quest_id"):
        raise ValueError("Save belongs to a different quest")
    digest = envelope["sha256"]
    if (not isinstance(digest, str) or len(digest) != 64
            or any(char not in "0123456789abcdef" for char in digest)):
        raise ValueError("Invalid save checksum")
    body = {key: envelope[key] for key in ("schema_version", "quest_id", "state")}
    if not hmac.compare_digest(digest, hashlib.sha256(_canonical(body)).hexdigest()):
        raise ValueError("Save checksum mismatch (corrupted/changed file)")
    problems = validate_state(envelope["state"], quest)
    if problems:
        raise ValueError("Save state rejected: " + "; ".join(problems))
    return envelope["state"]
