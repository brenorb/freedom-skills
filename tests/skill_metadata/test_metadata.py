"""Test frontmatter rules and the actual pre-commit hook against Git snapshots."""

import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("metadata_check", ROOT / "scripts/check_skill_metadata.py")
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

VALID = "---\nname: example\ndescription: Example skill.\nmetadata:\n  repository: 'https://example.com/repo'\n---\n# Example\n"
MISSING = "---\nname: example\ndescription: Example skill.\n---\n# Example\n"


class MetadataRulesTests(unittest.TestCase):
    def test_requires_nonempty_string_mapping(self):
        self.assertIsNone(checker.metadata_error(VALID))
        for metadata in ("", "metadata: null\n", "metadata: {}\n", "metadata: text\n",
                         "metadata: []\n", "metadata:\n  version: 1.0\n",
                         "metadata:\n  repository: ''\n", "metadata:\n  enabled: true\n"):
            with self.subTest(metadata=metadata):
                text = "---\nname: example\ndescription: Example.\n" + metadata + "---\n# Example\n"
                self.assertIsNotNone(checker.metadata_error(text))
        self.assertIsNone(checker.metadata_error(VALID.replace("  repository:", "  author:")))

    def test_body_text_does_not_count_as_frontmatter_metadata(self):
        self.assertIsNotNone(checker.metadata_error(MISSING + "\nmetadata:\n  repository: text\n"))
        for text in ("# No header\n", "---\nname: example\n", "---\nmetadata: [\n---\n"):
            with self.subTest(text=text):
                self.assertIsNotNone(checker.metadata_error(text))


class GitSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skill-metadata-hook-")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.command("git", "init", "--quiet", check=True)
        self.command("git", "config", "user.name", "Metadata Test", check=True)
        self.command("git", "config", "user.email", "metadata-test@example.invalid", check=True)
        self.command("git", "config", "core.hooksPath", ".githooks", check=True)
        (self.repo / ".githooks").mkdir()
        (self.repo / "scripts").mkdir()
        shutil.copyfile(ROOT / ".githooks/pre-commit", self.repo / ".githooks/pre-commit")
        (self.repo / ".githooks/pre-commit").chmod(0o755)
        shutil.copyfile(ROOT / "scripts/check_skill_metadata.py", self.repo / "scripts/check_skill_metadata.py")
        # Other validators are outside this focused test; the actual hook and
        # metadata checker run unchanged, with no dependency download/network.
        reference = self.repo / "scripts/validate_skills_ref.sh"
        reference.write_text("#!/bin/sh\nexit 0\n"); reference.chmod(0o755)
        binaries = self.repo / "test-bin"; binaries.mkdir()
        uv = binaries / "uv"
        uv.write_text("#!/bin/sh\nwhile [ $# -gt 0 ]; do\n"
                      "  if [ \"$1\" = python ]; then\n    shift\n"
                      f"    exec '{sys.executable}' \"$@\"\n  fi\n  shift\ndone\nexit 2\n")
        uv.chmod(0o755)
        self.env = {**os.environ, "PATH": str(binaries) + os.pathsep + os.environ["PATH"]}

    def command(self, *args, check=False):
        result = subprocess.run(args, cwd=self.repo, env=getattr(self, "env", None),
                                text=True, capture_output=True)
        if check and result.returncode:
            raise AssertionError(result.stderr + result.stdout)
        return result

    def write(self, relative, text):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def stage(self, *paths):
        self.command("git", "add", "--", *paths, check=True)

    def test_hook_blocks_staged_missing_metadata_even_when_working_tree_is_fixed(self):
        path = "skills/example/SKILL.md"
        self.write(path, MISSING); self.stage(path)
        self.write(path, VALID)
        result = self.command("git", "commit", "--quiet", "-m", "Should be blocked")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metadata must be a non-empty mapping", result.stderr)
        self.assertNotEqual(self.command("git", "rev-parse", "--verify", "HEAD").returncode, 0)

    def test_hook_accepts_valid_staged_metadata_even_when_working_tree_differs(self):
        path = "skills/example/SKILL.md"
        self.write(path, VALID); self.stage(path)
        self.write(path, MISSING)
        self.command("git", "commit", "--quiet", "-m", "Valid staged skill", check=True)
        self.assertEqual(self.command("git", "show", f"HEAD:{path}", check=True).stdout, VALID)

    def test_staged_check_handles_spaces_unicode_and_multiple_files(self):
        paths = ("skills/path with spaces/SKILL.md", "nested/ç/SKILL.md")
        for path in paths:
            self.write(path, MISSING)
        self.stage(*paths)
        result = self.command(sys.executable, "scripts/check_skill_metadata.py", "--staged")
        self.assertEqual(result.returncode, 1)
        for path in paths:
            self.assertIn(path, result.stderr)

    def test_ci_checks_committed_head_instead_of_working_tree(self):
        self.write("README.md", "baseline\n"); self.stage("README.md")
        self.command("git", "commit", "--quiet", "-m", "Baseline", check=True)
        base = self.command("git", "rev-parse", "HEAD", check=True).stdout.strip()
        path = "skills/example/SKILL.md"
        self.write(path, MISSING); self.stage(path)
        # Create a deliberately invalid PR head only in this disposable fixture.
        self.command("git", "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Invalid head", check=True)
        head = self.command("git", "rev-parse", "HEAD", check=True).stdout.strip()
        self.write(path, VALID)
        result = self.command(sys.executable, "scripts/check_skill_metadata.py", "--base", base, "--head", head)
        self.assertEqual(result.returncode, 1)
        self.assertIn(path, result.stderr)

    def test_deleted_skills_and_untouched_legacy_skills_do_not_block(self):
        path = "skills/legacy/SKILL.md"
        self.write(path, MISSING); self.stage(path)
        self.command("git", "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "-m", "Legacy baseline", check=True)
        self.write("README.md", "unrelated change\n"); self.stage("README.md")
        self.command("git", "commit", "--quiet", "-m", "Unrelated change", check=True)
        self.command("git", "rm", path, check=True)
        self.command("git", "commit", "--quiet", "-m", "Remove legacy skill", check=True)


if __name__ == "__main__":
    unittest.main()
