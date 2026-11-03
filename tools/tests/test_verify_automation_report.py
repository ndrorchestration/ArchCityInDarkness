import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_automation_report import TEST, verify


class Contract(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.report = Path(self.directory.name) / "index.json"
        self.log = Path(self.directory.name) / "editor.log"
        self.data = {"succeeded": 1, "failed": 0, "notRun": 0, "tests": [
            {"fullTestPath": TEST, "state": "Success"}]}
        self.text = f"Test Completed. Result={{Success}}. Name={{Contract}} Path={{{TEST}}}\n**** TEST COMPLETE. EXIT CODE: 0 ****\n"
        self.write()

    def write(self):
        self.report.write_text(json.dumps(self.data))
        self.log.write_text(self.text)

    def test_success(self):
        self.assertEqual(verify(self.report, self.log), [])

    def test_missing_report(self):
        self.report.unlink()
        self.assertTrue(verify(self.report, self.log))

    def test_failure(self):
        self.data["failed"] = 1
        self.data["tests"][0]["state"] = "Fail"
        self.write()
        self.assertTrue(verify(self.report, self.log))

    def test_missing_test(self):
        self.data["tests"] = []
        self.write()
        self.assertTrue(verify(self.report, self.log))

    def test_not_run(self):
        self.data["notRun"] = 1
        self.write()
        self.assertTrue(verify(self.report, self.log))

    def test_missing_log_marker(self):
        self.text = self.text.split("****")[0]
        self.write()
        self.assertTrue(verify(self.report, self.log))

    def test_failed_exit(self):
        self.text = self.text.replace("CODE: 0", "CODE: 2")
        self.write()
        self.assertTrue(verify(self.report, self.log))

    def test_missing_completion(self):
        self.text = "**** TEST COMPLETE. EXIT CODE: 0 ****"
        self.write()
        self.assertTrue(verify(self.report, self.log))

    def test_invalid_json(self):
        self.report.write_text("bad-json")
        self.assertTrue(verify(self.report, self.log))


if __name__ == "__main__":
    unittest.main()
