import json
import os
import re
import unittest

from _load import ROOT

SKILLS = [
    "replica-recon",
    "replica-architect",
    "replica-design",
    "replica-build",
    "replica-backend",
    "replica-test",
    "replica-diff",
    "replica-entrepreneur",
    "replica-brand",
    "replica-launch",
    "replica-deploy",
]
SKILL_ROOT = os.path.join(ROOT, ".opencode", "skills")
REFERENCES = {
    "replica-recon": ["references/features.csv", "references/recon-map.md"],
    "replica-architect": ["references/architecture.md"],
    "replica-design": ["references/tokens.json"],
    "replica-deploy": ["references/preflight.md"],
    "replica-entrepreneur": ["references/themes.json"],
    "replica-launch": ["references/listing.example.json"],
    "replica-test": [
        "references/test-plan.md",
        "references/bug-report.md",
        "references/e2e.example.spec.ts",
    ],
}


def frontmatter(path):
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (match.group(1) if match else ""), text


class Repo(unittest.TestCase):
    def test_eleven_skill_folders_under_opencode(self):
        found = sorted(
            name
            for name in os.listdir(SKILL_ROOT)
            if os.path.isfile(os.path.join(SKILL_ROOT, name, "SKILL.md"))
        )
        self.assertEqual(found, sorted(SKILLS))

    def test_no_legacy_skill_folders_at_root(self):
        legacy = [name for name in SKILLS if os.path.isdir(os.path.join(ROOT, name))]
        self.assertEqual(legacy, [])

    def test_frontmatter_name_and_description(self):
        for skill in SKILLS:
            fm, text = frontmatter(os.path.join(SKILL_ROOT, skill, "SKILL.md"))
            self.assertIn("name: %s\n" % skill, fm + "\n", skill)
            self.assertRegex(fm, r"description: ", skill)
            self.assertGreater(len(fm), 80, "%s description is too thin" % skill)
            self.assertGreater(len(text.splitlines()), 30, skill)

    def test_references_are_present(self):
        for skill, paths in REFERENCES.items():
            for rel in paths:
                path = os.path.join(SKILL_ROOT, skill, rel)
                self.assertTrue(os.path.isfile(path), path)

    def test_commands_and_agent_exist(self):
        command_root = os.path.join(ROOT, ".opencode", "commands")
        for skill in SKILLS:
            phase = skill.replace("replica-", "")
            path = os.path.join(command_root, skill + ".md")
            self.assertTrue(os.path.isfile(path), path)
            with open(path, encoding="utf-8") as handle:
                text = handle.read()
            self.assertIn("agent: replica", text)
            self.assertIn("replica gate " + phase, text)
        agent = os.path.join(ROOT, ".opencode", "agents", "replica.md")
        self.assertTrue(os.path.isfile(agent))
        with open(agent, encoding="utf-8") as handle:
            text = handle.read()
        self.assertIn("mode: primary", text)
        self.assertIn("opencode/deepseek-v4.1-flash-free", text)

    def test_project_config_points_to_the_agent(self):
        path = os.path.join(ROOT, ".opencode", "opencode.json")
        with open(path, encoding="utf-8") as handle:
            config = json.load(handle)
        self.assertEqual(config["$schema"], "https://opencode.ai/config.json")
        self.assertEqual(config["default_agent"], "replica")

    def test_plugin_manifest_points_at_opencode_skills(self):
        path = os.path.join(ROOT, ".claude-plugin", "plugin.json")
        with open(path, encoding="utf-8") as handle:
            manifest = json.load(handle)
        self.assertEqual(manifest["skills"], "./.opencode/skills/")
        target = os.path.normpath(os.path.join(ROOT, manifest["skills"]))
        self.assertTrue(os.path.isfile(os.path.join(target, "replica-recon", "SKILL.md")))

    def test_cli_and_installer_exist(self):
        expected = [
            "tools/replkit/cli.py",
            "tools/replkit/state.py",
            "tools/replkit/gate.py",
            "tools/replkit/browser.py",
            "tools/replkit/extract.py",
            "tools/replkit/doctor.py",
            "bin/replica",
            "scripts/install.sh",
        ]
        for rel in expected:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, rel)), rel)

    def test_installer_is_executable(self):
        path = os.path.join(ROOT, "scripts", "install.sh")
        self.assertTrue(os.access(path, os.X_OK))

    def test_license_and_notice(self):
        with open(os.path.join(ROOT, "LICENSE"), encoding="utf-8") as handle:
            license_text = handle.read()
        self.assertIn("MIT License", license_text)
        self.assertIn("Jake Schincariol", license_text)
        with open(os.path.join(ROOT, "NOTICE"), encoding="utf-8") as handle:
            notice = handle.read()
        self.assertIn("Jakeschincariol/replica-skill", notice)
        self.assertIn("MIT", notice)

    def test_makefile_runs_the_checks(self):
        with open(os.path.join(ROOT, "Makefile"), encoding="utf-8") as handle:
            makefile = handle.read()
        self.assertIn("check:", makefile)
        self.assertIn("unittest", makefile)

    def test_no_em_dashes(self):
        bad = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [
                name
                for name in dirnames
                if name not in (".git", "__pycache__", "node_modules", ".pytest_cache", ".ruff_cache")
            ]
            for filename in filenames:
                if filename.endswith((".md", ".py", ".json", ".ts", ".csv", ".sh")):
                    path = os.path.join(dirpath, filename)
                    with open(path, encoding="utf-8", errors="replace") as handle:
                        if chr(0x2014) in handle.read():
                            bad.append(os.path.relpath(path, ROOT))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
