import json
import os
import shutil
import tempfile
import unittest

from _load import ROOT
from replkit import gate, state

SKILL_ROOT = os.path.join(ROOT, ".opencode", "skills")
TOKENS = os.path.join(SKILL_ROOT, "replica-design", "references", "tokens.json")
LISTING = os.path.join(SKILL_ROOT, "replica-launch", "references", "listing.example.json")


def write(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)
    return path


def write_json(root, rel, data):
    return write(root, rel, json.dumps(data, indent=2) + "\n")


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def test_init_and_transitions(self):
        data = state.init(self.root, name="demo")
        self.assertTrue(os.path.isfile(os.path.join(self.root, "replica", "state.json")))
        self.assertEqual(state.next_phase(data), "recon")
        state.set_phase(data, "recon", "passed", notes="ok")
        self.assertEqual(state.next_phase(data), "architect")
        summary = state.summary(data)
        self.assertEqual(summary["phases"]["recon"], "passed")
        self.assertEqual(summary["current"], "architect")
        self.assertIn("recon", state.render(summary))

    def test_init_refuses_overwrite_without_force(self):
        state.init(self.root)
        with self.assertRaises(state.StateError):
            state.init(self.root)
        state.init(self.root, force=True)

    def test_load_without_state_raises(self):
        with self.assertRaises(state.StateError):
            state.load(self.root)


class ReconGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        state.init(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fails_without_artifacts(self):
        result = gate.run("recon", self.root)
        self.assertFalse(result["passed"])
        self.assertTrue(any("recon" in error["check"] for error in result["errors"]))

    def test_passes_with_map_and_matrix(self):
        write(self.root, "replica/recon.md", "# Recon\n\n" + ("Evidencia real. " * 30))
        write(
            self.root,
            "replica/features.csv",
            "feature,area,priority,original,clone,notes\n"
            "Login,auth,must,yes,yes,\n"
            "Pricing,billing,should,yes,no,\n",
        )
        result = gate.run("recon", self.root)
        self.assertTrue(result["passed"], gate.render(result))


class DesignGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        state.init(self.root)
        os.makedirs(os.path.join(self.root, "replica", "design"), exist_ok=True)
        shutil.copy(TOKENS, os.path.join(self.root, "replica", "design", "tokens.json"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_shipped_tokens_pass(self):
        result = gate.run("design", self.root)
        self.assertTrue(result["passed"], gate.render(result))

    def test_low_contrast_fails(self):
        path = os.path.join(self.root, "replica", "design", "tokens.json")
        with open(path, encoding="utf-8") as handle:
            tokens = json.load(handle)
        tokens["color"]["text"] = "#dddddd"
        write_json(self.root, "replica/design/tokens.json", tokens)
        result = gate.run("design", self.root)
        self.assertFalse(result["passed"])
        self.assertTrue(any("WCAG" in error["check"] for error in result["errors"]))


class DiffGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        state.init(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_threshold(self):
        write_json(self.root, "replica/parity.json", {"overall": 75})
        self.assertTrue(gate.run("diff", self.root)["passed"])
        write_json(self.root, "replica/parity.json", {"overall": 50})
        self.assertFalse(gate.run("diff", self.root)["passed"])


class BrandAndLaunchGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        state.init(self.root)
        write_json(
            self.root,
            "replica/brand.json",
            {"name": "Slotwise", "avoid": ["Calendly"], "domains": ["calendly.com"]},
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_brand_sweep_finds_and_then_clears(self):
        write(self.root, "app.py", "name = 'Calendly clone'\n")
        self.assertFalse(gate.run("brand", self.root)["passed"])
        write(self.root, "app.py", "name = 'Slotwise'\n")
        self.assertTrue(gate.run("brand", self.root)["passed"])

    def test_listing_lint(self):
        shutil.copy(LISTING, os.path.join(self.root, "replica", "listing.json"))
        self.assertTrue(gate.run("launch", self.root)["passed"])
        with open(LISTING, encoding="utf-8") as handle:
            listing = json.load(handle)
        listing["app_store"]["subtitle"] = "x" * 31
        write_json(self.root, "replica/listing.json", listing)
        self.assertFalse(gate.run("launch", self.root)["passed"])


class DeployGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        state.init(self.root)
        write(self.root, "replica/test-plan.md", "# Test plan\n\n" + ("Caso real. " * 20))
        write(self.root, "replica/bugs.md", "# Bugs\n\nSin S1 ni S2 abiertos.\n")
        write_json(self.root, "replica/parity.json", {"overall": 85})
        write_json(
            self.root,
            "replica/brand.json",
            {"name": "Slotwise", "avoid": ["Calendly"], "domains": ["calendly.com"]},
        )
        write(self.root, "app.py", "name = 'Slotwise'\n")
        preflight = [
            "# Preflight",
            "",
            "- [x] e2e suite green",
            "- [x] no open S1 or S2 bugs",
            "- [x] parity at least 80",
            "- [x] rebrand sweep clean",
            "- [x] production build passes",
            "- [x] privacy policy live",
            "- [x] account deletion works",
            "- [x] favicon and titles are ours",
            "",
            "Fecha y commit anotados.",
            "",
        ]
        write(self.root, "replica/preflight.md", "\n".join(preflight) * 3)

    def tearDown(self):
        self.tmp.cleanup()

    def test_complete_preflight_passes(self):
        result = gate.run("deploy", self.root)
        self.assertTrue(result["passed"], gate.render(result))

    def test_unchecked_item_blocks(self):
        path = os.path.join(self.root, "replica", "preflight.md")
        with open(path, "a", encoding="utf-8") as handle:
            handle.write("- [ ] pending item\n")
        result = gate.run("deploy", self.root)
        self.assertFalse(result["passed"])

    def test_open_s1_blocks(self):
        write(
            self.root,
            "replica/bugs.md",
            "# Bugs\n\n### BUG-001: crash on save\n\n"
            "- Severity: S1\n- Status: open\n",
        )
        result = gate.run("deploy", self.root)
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
