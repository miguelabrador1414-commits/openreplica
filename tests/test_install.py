import json
import os
import subprocess
import tempfile
import unittest

from _load import ROOT

SCRIPT = os.path.join(ROOT, "scripts", "install.sh")


class Install(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = self.tmp.name
        self.env = os.environ.copy()
        self.env["HOME"] = self.home
        self.env["XDG_DATA_HOME"] = os.path.join(self.home, "data")
        self.env["XDG_CONFIG_HOME"] = os.path.join(self.home, "config")
        self.env["XDG_BIN_HOME"] = os.path.join(self.home, "bin")
        self.env["PATH"] = os.path.join(self.home, "bin") + os.pathsep + self.env.get("PATH", "")

    def tearDown(self):
        self.tmp.cleanup()

    def run_install(self, *args):
        return subprocess.run(
            ["sh", SCRIPT] + list(args),
            cwd=ROOT,
            env=self.env,
            capture_output=True,
            text=True,
        )

    def test_global_install_is_idempotent(self):
        first = self.run_install("--global")
        self.assertEqual(first.returncode, 0, first.stderr)
        for _ in range(2):
            result = self.run_install("--global")
            self.assertEqual(result.returncode, 0, result.stderr)

        share = os.path.join(self.home, "data", "openreplica")
        wrapper = os.path.join(self.home, "bin", "replica")
        config = os.path.join(self.home, "config", "opencode")
        self.assertTrue(os.path.isfile(wrapper))
        self.assertTrue(os.access(wrapper, os.X_OK))
        self.assertTrue(os.path.isfile(os.path.join(share, "tools", "replkit", "cli.py")))
        self.assertFalse(os.path.exists(os.path.join(share, "tools", "tools")))
        self.assertTrue(
            os.path.isfile(os.path.join(config, "skills", "replica-recon", "SKILL.md"))
        )
        self.assertTrue(os.path.isfile(os.path.join(config, "commands", "replica-recon.md")))
        self.assertTrue(os.path.isfile(os.path.join(config, "agents", "replica.md")))

        version = subprocess.run(
            [wrapper, "--version"],
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("replkit", version.stdout)

    def test_project_install_does_not_touch_global_config(self):
        project = os.path.join(self.home, "app")
        os.makedirs(project)
        result = self.run_install("--project", project)
        self.assertEqual(result.returncode, 0, result.stderr)
        local = os.path.join(project, ".opencode")
        self.assertTrue(os.path.isfile(os.path.join(local, "skills", "replica-recon", "SKILL.md")))
        self.assertTrue(os.path.isfile(os.path.join(local, "commands", "replica-recon.md")))
        self.assertTrue(os.path.isfile(os.path.join(local, "agents", "replica.md")))
        with open(os.path.join(local, "opencode.json"), encoding="utf-8") as handle:
            self.assertEqual(json.load(handle)["default_agent"], "replica")
        local_cli = os.path.join(local, "bin", "replica")
        self.assertTrue(os.access(local_cli, os.X_OK))
        version = subprocess.run(
            [local_cli, "--version"],
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("replkit", version.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.home, "config", "opencode")))

        other = os.path.join(self.home, "other")
        os.makedirs(os.path.join(other, ".opencode"))
        existing = os.path.join(other, ".opencode", "opencode.json")
        with open(existing, "w", encoding="utf-8") as handle:
            json.dump({"default_agent": "custom"}, handle)
        result = self.run_install("--project", other)
        self.assertEqual(result.returncode, 0, result.stderr)
        with open(existing, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), {"default_agent": "custom"})
        self.assertIn("no lo sobrescribo", result.stdout)

    def test_missing_project_fails(self):
        result = self.run_install("--project", os.path.join(self.home, "nope"))
        self.assertEqual(result.returncode, 1)
        self.assertIn("No existe", result.stderr)


if __name__ == "__main__":
    unittest.main()
