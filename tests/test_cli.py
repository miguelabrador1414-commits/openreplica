import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

from _load import ROOT
from replkit import cli

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "site")


def call(args):
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = cli.main(args)
    return code, out.getvalue(), err.getvalue()


class Cli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_status_and_gate(self):
        code, output, _ = call(["init", self.root])
        self.assertEqual(code, 0)
        self.assertIn("Inicializado", output)

        code, output, _ = call(["status", "--root", self.root, "--json"])
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertEqual(data["current"], "recon")

        code, output, _ = call(["gate", "recon", "--root", self.root])
        self.assertEqual(code, 2)
        self.assertIn("BLOQUEADO", output)

        code, output, _ = call(["mark", "recon", "in_progress", "--root", self.root])
        self.assertEqual(code, 0)
        code, output, _ = call(["status", "--root", self.root, "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(output)["phases"]["recon"], "in_progress")

    def test_doctor_json(self):
        code, output, _ = call(["doctor", "--root", self.root, "--json"])
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertTrue(data["ok"])

    def test_extract_json(self):
        code, output, _ = call(["extract", os.path.join(FIXTURE, "index.html"), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertEqual(data["title"], "Slotwise: Booking Links")

    def test_capture_stub_json(self):
        out = os.path.join(self.root, "shots")
        code, output, _ = call(
            [
                "capture",
                "https://example.test",
                "--root",
                self.root,
                "--out",
                out,
                "--backend",
                "stub",
                "--fixture",
                FIXTURE,
            ]
        )
        self.assertEqual(code, 0)
        data = json.loads(output)
        self.assertEqual(data["backend"], "stub")
        self.assertTrue(os.path.isfile(os.path.join(out, "capture.json")))

    def test_forwarded_parity(self):
        matrix = os.path.join(self.root, "features.csv")
        with open(matrix, "w", encoding="utf-8") as handle:
            handle.write(
                "feature,area,priority,original,clone,notes\n"
                "Login,auth,must,yes,yes,\n"
            )
        code, output, _ = call(["parity", matrix, "--fail-under", "10"])
        self.assertEqual(code, 0)
        self.assertIn("Parity", output)

    def test_version(self):
        out = io.StringIO()
        with self.assertRaises(SystemExit) as ctx, redirect_stdout(out):
            cli.main(["--version"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("replkit", out.getvalue())


if __name__ == "__main__":
    unittest.main()
