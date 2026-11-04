import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_automation_report import TEST, verify

QUEST = "ArchCityInDarkness.Quest.Glassbend.Contract"
INTERACTION = "ArchCityInDarkness.Interaction.Glassbend.Contract"


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


    def test_quest_named_success(self):
        self.data["tests"][0]["fullTestPath"] = QUEST
        self.text = self.text.replace(TEST, QUEST)
        self.write()
        self.assertEqual(verify(self.report, self.log, expected=QUEST), [])

    def test_quest_report_cannot_be_hunger(self):
        self.text = self.text.replace(TEST, QUEST)
        self.write()
        self.assertTrue(verify(self.report, self.log, expected=QUEST))

    def test_quest_log_cannot_be_hunger(self):
        self.data["tests"][0]["fullTestPath"] = QUEST
        self.write()
        self.assertTrue(verify(self.report, self.log, expected=QUEST))

    def test_quest_duplicate_report_cannot_pass(self):
        self.data["tests"] = [
            {"fullTestPath": QUEST, "state": "Success"},
            {"fullTestPath": QUEST, "state": "Success"},
        ]
        self.data["succeeded"] = 2
        self.text = self.text.replace(TEST, QUEST)
        self.write()
        self.assertTrue(verify(self.report, self.log, expected=QUEST))

    def test_interaction_named_success(self):
        self.data["tests"][0]["fullTestPath"] = INTERACTION
        self.text = self.text.replace(TEST, INTERACTION)
        self.write()
        self.assertEqual(verify(self.report, self.log, expected=INTERACTION), [])

    def test_interaction_report_cannot_be_quest(self):
        self.data["tests"][0]["fullTestPath"] = QUEST
        self.text = self.text.replace(TEST, INTERACTION)
        self.write()
        self.assertTrue(verify(self.report, self.log, expected=INTERACTION))



if __name__ == "__main__":
    unittest.main()
