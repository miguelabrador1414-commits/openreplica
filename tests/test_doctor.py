import os
import tempfile
import unittest

from _load import ROOT
from replkit import doctor


class Doctor(unittest.TestCase):
    def test_required_checks_pass(self):
        result = doctor.run(ROOT)
        self.assertTrue(result["ok"])
        names = {check["name"] for check in result["checks"]}
        self.assertIn("python", names)
        self.assertIn("git", names)
        self.assertIn("escritura en replica/", names)

    def test_local_cli_counts_as_installed(self):
        with tempfile.TemporaryDirectory() as tmp:
            bin_dir = os.path.join(tmp, ".opencode", "bin")
            os.makedirs(bin_dir)
            local_cli = os.path.join(bin_dir, "replica")
            with open(local_cli, "w", encoding="utf-8") as handle:
                handle.write("#!/bin/sh\n")
            os.chmod(local_cli, 0o755)
            result = doctor.run(tmp)
            check = next(
                item for item in result["checks"] if item["name"] == "CLI en PATH"
            )
            self.assertTrue(check["ok"])
            self.assertTrue(check["detail"].endswith(os.path.join(".opencode", "bin", "replica")))

    def test_optional_playwright_is_reported(self):
        result = doctor.run(ROOT)
        playwright = next(check for check in result["checks"] if check["name"] == "playwright")
        self.assertFalse(playwright["required"])
        self.assertIn("opcional", doctor.render(result))


if __name__ == "__main__":
    unittest.main()
