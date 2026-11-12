import os
import unittest

from _load import ROOT
from replkit import extract

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "site", "index.html")


class Extract(unittest.TestCase):
    def setUp(self):
        self.data = extract.extract(FIXTURE)

    def test_title_and_text(self):
        self.assertEqual(self.data["title"], "Slotwise: Booking Links")
        self.assertIn("Share one link", self.data["text_sample"])

    def test_routes_controls_and_forms(self):
        self.assertIn("/pricing", self.data["routes"])
        self.assertIn("/login", self.data["routes"])
        self.assertTrue(any(item["name"] == "email" for item in self.data["inputs"]))
        self.assertTrue(any("Create my link" in item["text"] for item in self.data["buttons"]))
        self.assertEqual(self.data["forms"][0]["action"], "/book")

    def test_colours_and_fonts(self):
        colours = [colour.lower() for colour in self.data["colors"]]
        self.assertIn("#2f5bea", colours)
        self.assertIn("#14171c", colours)
        self.assertTrue(any("inter" in font.lower() for font in self.data["fonts"]))

    def test_render_mentions_the_page(self):
        text = extract.render(self.data)
        self.assertIn("Slotwise", text)
        self.assertIn("Rutas:", text)

    def test_directory_extraction_merges_files(self):
        data = extract.extract(os.path.dirname(FIXTURE))
        self.assertEqual(len(data["files"]), 1)
        self.assertIn("/pricing", data["routes"])

    def test_missing_path_is_an_error(self):
        with self.assertRaises(extract.ExtractError):
            extract.extract("/nope/nothing.html")


if __name__ == "__main__":
    unittest.main()
