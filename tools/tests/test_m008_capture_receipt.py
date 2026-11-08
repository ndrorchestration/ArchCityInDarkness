"""Synthetic PNG receipt tests. Nothing here proves native Unreal screenshots."""
import struct
import sys
import tempfile
import unittest
from pathlib import Path
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build_m008_capture_receipt import (
    MAP, PNG_MAGIC, ROLES, build_receipt, collect_image, inspect_png, within_saved,
)


def chunk(kind, payload):
    return (struct.pack(">I", len(payload)) + kind + payload +
            struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff))


def make_png(width=1280, height=720, value=0):
    # Real syntactically valid PNG with zero filters and simple RGBA scanlines.
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    row = b"\x00" + bytes((value, 0, 0, 255)) * width
    return (PNG_MAGIC + chunk(b"IHDR", header) +
            chunk(b"IDAT", zlib.compress(row * height)) +
            chunk(b"IEND", b""))


class M008CaptureReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / "Saved" / "ArchCityVerification" / "M008"
        self.folder.mkdir(parents=True)
        self.shots = {}

    def add_shot(self, role, value=1, width=1280, height=720):
        p = self.folder / f"{role}.png"
        p.write_bytes(make_png(width, height, value))
        self.shots[role] = p
        return p

    def receipt(self, shots=None, attested=True, version=None):
        return build_receipt(
            self.root, self.shots if shots is None else shots,
            {"MajorVersion": 5, "MinorVersion": 8, "PatchVersion": 4}
            if version is None else version,
            "a" * 40, "review/m008-evidence", attested,
        )

    def test_png_structure_and_dimensions(self):
        self.assertEqual(inspect_png(make_png()), (1280, 720))

    def test_corrupt_crc_rejected(self):
        corrupt = bytearray(make_png())
        corrupt[20] ^= 1
        with self.assertRaisesRegex(ValueError, "CRC"):
            inspect_png(bytes(corrupt))

    def test_truncated_png_rejected(self):
        with self.assertRaises(ValueError):
            inspect_png(make_png()[:-12])

    def test_low_resolution_rejected(self):
        with self.assertRaisesRegex(ValueError, "resolution"):
            inspect_png(make_png(640, 480))

    def test_single_capture_remains_incomplete(self):
        self.add_shot("arrival")
        r = self.receipt()
        self.assertEqual(r["review_status"], "CAPTURE_SET_INCOMPLETE")
        self.assertTrue(r["not_a_gameplay_pass"])
        self.assertIn("receipt_after", r["missing_roles"])

    def test_distinct_five_capture_set_still_unreviewed(self):
        for i, role in enumerate(ROLES):
            self.add_shot(role, i + 1)
        r = self.receipt()
        self.assertEqual(r["review_status"], "CAPTURE_SET_COMPLETE_UNREVIEWED")
        self.assertTrue(r["not_a_gameplay_pass"])
        self.assertEqual(len(r["captures"]), 5)
        self.assertEqual(r["missing_roles"], [])
        self.assertEqual(r["map"], MAP)
        self.assertTrue(all(len(item["sha256"]) == 64 for item in r["captures"]))

    def test_duplicate_image_bytes_rejected(self):
        self.add_shot("arrival", 1)
        self.add_shot("receipt_before", 1)
        with self.assertRaisesRegex(ValueError, "Identical image"):
            self.receipt()

    def test_attestation_required(self):
        self.add_shot("arrival")
        with self.assertRaisesRegex(ValueError, "attest"):
            self.receipt(attested=False)

    def test_wrong_engine_rejected(self):
        self.add_shot("arrival")
        with self.assertRaisesRegex(ValueError, "Expected Unreal 5.8.4"):
            self.receipt(version={"MajorVersion": 5, "MinorVersion": 7, "PatchVersion": 0})

    def test_escape_saved_directory_rejected(self):
        outside = self.root / "outside.png"
        outside.write_bytes(make_png())
        with self.assertRaisesRegex(ValueError, "under project Saved"):
            within_saved(self.root, outside)
        with self.assertRaisesRegex(ValueError, "under project Saved"):
            collect_image(self.root, "arrival", outside)

    def test_unknown_role_rejected(self):
        path = self.add_shot("arrival")
        with self.assertRaisesRegex(ValueError, "Unexpected screenshot role"):
            collect_image(self.root, "arbitrary", path)

    def test_missing_source_rejected(self):
        with self.assertRaisesRegex(ValueError, "Missing PNG"):
            collect_image(self.root, "arrival", self.folder / "missing.png")


if __name__ == "__main__":
    unittest.main()
