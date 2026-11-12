import json
import os
import tempfile
import unittest

from _load import ROOT
from replkit import browser, imgdiff

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "site")


class Fixture(unittest.TestCase):
    def test_home_png_is_a_valid_screenshot(self):
        width, height, _ = imgdiff.read_png(
            os.path.join(FIXTURE, "screens", "home.png")
        )
        self.assertEqual((width, height), (240, 360))


class StubCapture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = os.path.join(self.tmp.name, "screens")

    def tearDown(self):
        self.tmp.cleanup()

    def test_capture_is_offline_and_copies_screens(self):
        data = browser.capture(
            "https://example.test", self.out, backend="stub", fixture=FIXTURE
        )
        self.assertEqual(data["backend"], "stub")
        self.assertFalse(data["network"])
        self.assertIn("Slotwise", data["html"])
        self.assertTrue(os.path.isfile(os.path.join(self.out, "capture.json")))
        self.assertTrue(os.path.isfile(os.path.join(self.out, "home.png")))
        with open(os.path.join(self.out, "capture.json"), encoding="utf-8") as handle:
            saved = json.load(handle)
        self.assertEqual(saved["backend"], "stub")

    def test_auto_with_fixture_uses_stub(self):
        data = browser.capture(
            "https://example.test", self.out, backend="auto", fixture=FIXTURE
        )
        self.assertEqual(data["backend"], "stub")

    def test_manual_writes_checklist(self):
        data = browser.capture("https://example.test", self.out, backend="manual")
        self.assertTrue(data["manual"])
        self.assertTrue(os.path.isfile(data["file"]))
        with open(data["file"], encoding="utf-8") as handle:
            self.assertIn("Captura manual", handle.read())

    def test_missing_fixture_is_an_error(self):
        with self.assertRaises(browser.BrowserError):
            browser.capture("https://example.test", self.out, backend="stub")


class Viewports(unittest.TestCase):
    def test_named_and_plain(self):
        views = browser.parse_viewports(["desktop=1440x900", "390x844"])
        self.assertEqual(views[0]["name"], "desktop")
        self.assertEqual((views[0]["width"], views[0]["height"]), (1440, 900))
        self.assertEqual((views[1]["width"], views[1]["height"]), (390, 844))

    def test_bad_viewport_is_an_error(self):
        for value in ("desktop", "0x900", "a x b"):
            with self.assertRaises(browser.BrowserError):
                browser.parse_viewports([value])


if __name__ == "__main__":
    unittest.main()
