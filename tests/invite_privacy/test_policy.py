"""Check the editable SKILL.md text and the real helper's invite-output boundary."""

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
PREFIX = "Model may handle transfer links and codes: "


class InvitePrivacyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="croc-text-config-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.installed = self.root / "croc"
        shutil.copytree(ROOT / "skills/croc", self.installed,
                        ignore=shutil.ignore_patterns(".local", "__pycache__"))
        self.skill = self.installed / "SKILL.md"
        self.initial = self.skill.read_bytes()
        self.observation = self.root / "observation.json"
        self.env = {**os.environ, "PRIVATE_OBSERVATION": str(self.observation)}
        for key in ("CROC_SECRET", "CROC_STORE_TOKEN"):
            self.env.pop(key, None)
        self.fake_croc = self.root / "fake-croc"
        self.fake_croc.write_text(f"#!{sys.executable}\n" + '''import hashlib, json, os, pathlib, sys
secret = os.environ.get('CROC_SECRET', '')
pathlib.Path(os.environ['PRIVATE_OBSERVATION']).write_text(json.dumps({'secret_sha256': hashlib.sha256(secret.encode()).hexdigest()}))
print(secret, flush=True)
print(secret, file=sys.stderr, flush=True)
''')
        self.fake_croc.chmod(0o700)
        self.payload = self.root / "payload.txt"
        self.payload.write_text("disposable test data\n")

    def command(self, script, *args, env=None):
        return subprocess.run([sys.executable, str(self.installed / "scripts" / script), *args],
                              env=env or self.env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True, timeout=10, start_new_session=True)

    def policy(self):
        result = self.command("invite_policy.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def edit_choice(self, choice):
        lines = self.skill.read_text().splitlines(keepends=True)
        self.skill.write_text("".join(PREFIX+choice+"\n" if line.startswith(PREFIX) else line for line in lines))

    def test_published_skill_starts_unconfigured_and_reading_does_not_write(self):
        self.assertIn(PREFIX+"not configured", self.skill.read_text())
        self.assertEqual(self.policy()["model_access"], "ask")
        self.assertEqual(self.skill.read_bytes(), self.initial)
        self.assertFalse((self.installed / ".local").exists())

    def test_editing_the_skill_persists_across_new_processes(self):
        self.edit_choice("allowed")
        saved = self.skill.read_bytes()
        self.assertNotEqual(saved, self.initial)
        for _ in range(3):
            self.assertEqual(self.policy()["model_access"], "allow")
            self.assertEqual(self.skill.read_bytes(), saved)
        self.edit_choice("private")
        self.assertEqual(self.policy()["model_access"], "deny")
        self.edit_choice("not configured")
        self.assertEqual(self.skill.read_bytes(), self.initial)
        self.assertEqual(self.policy()["model_access"], "ask")

    def test_missing_ambiguous_or_unknown_text_never_allows(self):
        original = self.skill.read_text()
        for text in (original.replace("<!-- croc-config:start -->", ""),
                     original+"\n<!-- croc-config:start -->\n",
                     original.replace(PREFIX+"not configured", PREFIX+"maybe"),
                     "<!-- croc-config:end -->\n<!-- croc-config:start -->\n"+PREFIX+"allowed\n"):
            with self.subTest(text_length=len(text)):
                self.skill.write_text(text)
                self.assertEqual(self.policy()["model_access"], "ask")

    def test_unconfigured_helper_fails_before_starting_croc(self):
        result = self.command("transfer.py", "--croc", str(self.fake_croc), "send", str(self.payload))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"], "configuration_required")
        self.assertFalse(self.observation.exists())

    def test_allowed_generates_invite_and_private_suppresses_it(self):
        self.edit_choice("allowed")
        result = self.command("transfer.py", "--croc", str(self.fake_croc), "send", str(self.payload))
        self.assertEqual(result.returncode, 0)
        events = [json.loads(line) for line in result.stdout.splitlines()]
        code = events[0]["code"]
        self.assertEqual(len(code), 48)
        self.assertEqual(json.loads(self.observation.read_text())["secret_sha256"], hashlib.sha256(code.encode()).hexdigest())
        self.assertEqual(result.stderr, "")
        self.edit_choice("private")
        saved = self.skill.read_bytes()
        secret = "synthetic-private-canary"
        result = self.command("transfer.py", "--croc", str(self.fake_croc), "send", str(self.payload),
                              env={**self.env, "CROC_SECRET": secret})
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(secret, result.stdout + result.stderr)
        self.assertTrue(all("code" not in event for event in map(json.loads, result.stdout.splitlines())))
        self.assertEqual(self.skill.read_bytes(), saved)

    def test_private_requires_local_secret_without_changing_choice(self):
        self.edit_choice("private")
        saved = self.skill.read_bytes()
        result = self.command("transfer.py", "--croc", str(self.fake_croc), "send", str(self.payload))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error"], "missing_secret")
        self.assertFalse(self.observation.exists())
        self.assertEqual(self.skill.read_bytes(), saved)


if __name__ == "__main__":
    unittest.main()
