"""ACID-HIP-002 adversarial regression tests; run via python -m unittest discover."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("handoff_validator", ROOT / "validate-handoff.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
SCHEMA = json.loads((ROOT / "handoff-schema.json").read_text(encoding="utf-8"))
VALID = json.loads((ROOT / "examples" / "valid-payload.json").read_text(encoding="utf-8"))

class HandoffPolicyTests(unittest.TestCase):
    def check_case(self, changes, allowed=False):
        payload = copy.deepcopy(VALID)
        payload.update(changes)
        issues = module.validate(SCHEMA, payload)
        if allowed:
            self.assertEqual([], issues)
        else:
            self.assertTrue(issues, "expected policy rejection")
    def test_valid_pending(self):
        self.check_case({}, True)
    def test_valid_completed(self):
        self.check_case({"status":"DONE", "head_sha":"b"*40, "evidence":[{"command":"python -m unittest", "exit_code":0, "output":"Ran 10 tests OK"}]}, True)
    def test_traversal(self):
        self.check_case({"allowed_paths":["../../secrets/"]})
    def test_embedded_traversal(self):
        self.check_case({"allowed_paths":[".agents/coordination/../../secrets"]})
    def test_absolute(self):
        self.check_case({"allowed_paths":["C:/Users/Admin/.ssh/"]})
    def test_outside_scope(self):
        self.check_case({"allowed_paths":["src/gameplay/"]})
    def test_backslash(self):
        self.check_case({"allowed_paths":[".agents\\coordination\\secrets"]})
    def test_duplicate_separator(self):
        self.check_case({"allowed_paths":[".agents/coordination//test.json"]})
    def test_whitespace_objective(self):
        self.check_case({"objective":"   "})
    def test_completed_no_evidence(self):
        self.check_case({"status":"DONE"})
    def test_completed_no_head(self):
        self.check_case({"status":"DONE", "evidence":[{"command":"check", "exit_code":0, "output":"ok"}]})
    def test_empty_evidence_fields(self):
        self.check_case({"evidence":[{"command":"", "exit_code":0, "output":""}]})
    def test_invalid_id(self):
        self.check_case({"task_id":"ACP-PILOT-001"})
    def test_paid_budget(self):
        self.check_case({"max_cost_usd":1})
    def test_boolean_exit(self):
        self.check_case({"evidence":[{"command":"check","exit_code":True,"output":"ok"}]})
    def test_failing_exit_is_documentable(self):
        self.check_case({"evidence":[{"command":"negative test", "exit_code":1, "output":"expected failure"}]},True)
    def test_unexpected_property(self):
        self.check_case({"extra_key":"unsafe"})
    def test_blank_criterion(self):
        self.check_case({"acceptance_criteria":["  "]})

if __name__ == "__main__":
    unittest.main()
