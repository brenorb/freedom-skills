"""Run the shipped examples against real nowhere-cli 0.3.0 through npx.

Relay commands target an in-memory loopback fixture, never public relays. A
missing npx is an error, not a skipped suite. No global CLI install is required.
"""

from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import re
import selectors
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit
from urllib.request import urlopen


REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skills" / "hosted-nowhere"
EXAMPLES = SKILL / "examples"
APPS = ("message", "drop", "event", "fundraiser", "petition", "forum", "art", "store")
BASELINE = "0.3.0"


class SkillResources(unittest.TestCase):
    def test_progressive_references_resolve_inside_the_skill(self):
        """Broken routing/fixture links make an installed skill unusable."""
        for document in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", document.read_text()):
                link = urlsplit(target)
                if link.scheme or not link.path:
                    continue
                resolved = (document.parent / link.path).resolve()
                with self.subTest(document=document.name, link=target):
                    self.assertTrue(resolved.is_relative_to(SKILL.resolve()))
                    self.assertTrue(resolved.is_file(), f"Missing resource: {resolved}")


class NowhereWorkflows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.command = json.loads(os.environ.get(
            "NOWHERE_CLI_COMMAND",
            '["npx", "--yes", "--package=nowhere-cli@0.3.0", "--", "nowhere"]',
        ))
        if not isinstance(cls.command, list) or not cls.command or not all(
            isinstance(arg, str) and arg for arg in cls.command
        ):
            raise ValueError("NOWHERE_CLI_COMMAND must be a nonempty JSON argv array")
        try:
            version = subprocess.run(
                [*cls.command, "--version"], capture_output=True, text=True,
                timeout=120, check=True,
            ).stdout.strip()
        except FileNotFoundError as error:
            raise RuntimeError(
                "Node.js 20+ with npx is required, or set NOWHERE_CLI_COMMAND to an existing build"
            ) from error
        if version != BASELINE:
            raise RuntimeError(f"Behavioral baseline is nowhere-cli {BASELINE}; found {version}")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="hosted-nowhere-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        # Prevent accidental use/modification of the user's persisted signer state.
        self.env = {**os.environ, "XDG_CONFIG_HOME": str(self.work / "config")}
        self.counter = 0

    def raw(self, *args):
        return subprocess.run(
            [*self.command, *args], cwd=self.work, env=self.env,
            capture_output=True, text=True, timeout=30,
        )

    def cli(self, *args):
        result = self.raw(*args, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def json_file(self, payload):
        self.counter += 1
        path = self.work / f"input-{self.counter}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False))
        return str(path)

    def create(self, app, payload=None, *options):
        path = str(EXAMPLES / f"{app}.json") if payload is None else self.json_file(payload)
        return self.cli("create", app, "--input", path, *options)

    def update(self, url, patch, *options):
        return self.cli("update", url, "--patch", self.json_file(patch), *options)

    def relay(self, reject=False):
        fixture = str(Path(__file__).with_name("relay.mjs"))
        if Path(self.command[0]).name in ("npx", "npx.cmd") and self.command[-1] == "nowhere":
            # Launch in the same npx environment so the relay fixture can reuse
            # that package's ws dependency without a separate npm installation.
            relay_command = [*self.command[:-1], "node", fixture]
        else:
            entrypoint = (
                Path(self.command[-1]).resolve() if len(self.command) > 1
                else Path(shutil.which(self.command[0]) or self.command[0]).resolve()
            )
            relay_command = ["node", fixture, str(entrypoint)]
        process = subprocess.Popen(
            [*relay_command, *(["--reject"] if reject else [])],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )

        def close():
            if process.poll() is None:
                process.terminate()
            try:
                return process.communicate(timeout=5)[1]
            except subprocess.TimeoutExpired:
                process.kill()
                return process.communicate()[1]

        self.addCleanup(close)
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            self.assertTrue(selector.select(timeout=10), "Loopback relay did not start")
        ready = process.stdout.readline()
        if not ready:
            stderr = close()
            self.fail(f"Loopback relay exited with code {process.returncode}: {stderr}")
        return json.loads(ready)["url"]

    def relay_events(self, relay):
        with urlopen(relay.replace("ws://", "http://") + "/events", timeout=5) as response:
            return json.load(response)

    def test_all_app_examples_create_inspect_and_update_without_losing_content(self):
        for app in APPS:
            with self.subTest(app=app):
                fixture = json.loads((EXAMPLES / f"{app}.json").read_text())
                created = self.create(app)
                expected_type = "discussion" if app == "forum" else app
                self.assertEqual(created["siteType"], expected_type)
                self.assertEqual(urlsplit(created["url"]).fragment, created["fragment"])

                inspected = self.cli("inspect", created["url"])
                self.assertEqual(inspected["site"]["siteType"], expected_type)
                self.assertEqual(inspected["site"]["name"], fixture["name"])
                self.assertEqual(inspected["verification"], created["verification"])
                self.assertFalse(inspected["signed"])

                # Unlike inspect's summary, no-op update exposes the full decoded
                # editable payload. This crosses the actual codec boundary.
                decoded = self.update(created["url"], {})
                # The forum codec canonicalizes tag order. Compare tags as a
                # multiset while keeping other arrays (notably items) ordered.
                self.assertCountEqual(decoded["siteData"]["tags"], created["siteData"]["tags"])
                self.assertEqual(
                    {k: v for k, v in decoded["siteData"].items() if k != "tags"},
                    {k: v for k, v in created["siteData"].items() if k != "tags"},
                )
                for key in ("description", "svg", "items"):
                    if key in fixture:
                        self.assertEqual(decoded["siteData"][key], fixture[key])
                for tag in fixture["tags"]:
                    self.assertTrue(any(
                        actual["key"] == tag["key"] and actual.get("value") == tag.get("value")
                        for actual in decoded["siteData"]["tags"]
                    ))

                updated = self.update(created["url"], {"name": "Revised " + fixture["name"]})
                expected = {**decoded["siteData"], "name": "Revised " + fixture["name"]}
                self.assertEqual(updated["siteData"], expected)
                final = self.cli("inspect", updated["url"])
                self.assertEqual(final["site"]["name"], expected["name"])
                self.assertEqual(final["site"]["siteType"], expected_type)
                self.assertNotEqual(updated["url"], created["url"])
                self.assertNotEqual(final["verification"]["sitePhrase"], inspected["verification"]["sitePhrase"])
                # Distributed links remain snapshots of the original content.
                original = self.cli("inspect", created["url"])
                self.assertEqual(original["site"]["name"], fixture["name"])

    def test_patch_replaces_arrays_removes_null_fields_and_keeps_other_fields(self):
        created = self.create("store")
        patch = {
            "description": None,
            "tags": [{"key": "$", "value": "EUR"}, {"key": "k", "value": "0"}],
            "items": [{"name": "Replacement", "price": 2.25, "tags": []}],
        }
        updated = self.update(created["url"], patch)
        decoded = self.update(updated["url"], {})["siteData"]
        self.assertEqual(decoded["items"], patch["items"])
        self.assertEqual(decoded["tags"], patch["tags"])
        self.assertNotIn("description", decoded)
        self.assertEqual(decoded["pubkey"], created["siteData"]["pubkey"])
        self.assertEqual(decoded["name"], created["siteData"]["name"])

    def test_message_requires_body_or_title_and_accepts_title_only(self):
        for payload in ({"name": "Sender"}, {"name": "Sender", "tags": [{"key": "t", "value": ""}]}):
            with self.subTest(payload=payload):
                failure = self.raw("create", "message", "--input", self.json_file(payload), "--json")
                self.assertNotEqual(failure.returncode, 0)
                self.assertTrue(failure.stderr.strip())
        created = self.create("message", {"name": "Sender", "tags": [{"key": "t", "value": "Title only"}]})
        self.assertEqual(self.cli("inspect", created["url"])["site"]["siteType"], "message")

    def test_message_and_fundraiser_share_lightning_and_custom_methods_in_one_tag(self):
        payload = {"name": "Method test", "description": "Test only", "tags": [
            {"key": "l", "value": "reader@wallet.example,*PayPal:example.com/alice"}
        ]}
        for app, scope in (("message", "tip"), ("fundraiser", "donate")):
            with self.subTest(app=app):
                created = self.create(app, payload)
                result = self.cli(app, scope, "methods", created["url"])
                methods = {method["id"]: method for method in result["methods"]}
                self.assertEqual(methods["lightning"]["value"], "reader@wallet.example")
                self.assertEqual(methods["custom_0"]["label"], "PayPal")
                self.assertEqual(methods["custom_0"]["value"], "example.com/alice")
                self.assertEqual(methods["custom_0"]["type"], "custom")

    def test_malformed_json_and_fragment_fail_without_a_success_payload(self):
        malformed = self.work / "broken.json"
        malformed.write_text('{"name":')
        for args in (
            ("create", "event", "--input", str(malformed)),
            ("inspect", "https://hostednowhere.com/s#not-a-valid-fragment"),
        ):
            with self.subTest(args=args):
                failure = self.raw(*args, "--json")
                self.assertNotEqual(failure.returncode, 0)
                self.assertTrue(failure.stderr.strip())
                self.assertFalse(failure.stdout.strip())

    def signing_fixture(self):
        # Publicly known disposable test secrets. Never use these for real data.
        secret = "1" * 64
        owner = self.cli("pubkey", "--secret", secret)
        payload = {"name": "Signed dispatch", "description": "Original body", "pubkey": owner["npub"], "tags": []}
        return secret, owner, payload

    def test_signature_verification_checks_identity_and_unsigned_is_not_success(self):
        secret, owner, payload = self.signing_fixture()
        created = self.create("message", payload)
        self.assertFalse(self.cli("verify", created["url"])["signed"])
        signed = self.cli("sign", created["url"], "--secret", secret)
        verified = self.cli("verify", signed["signedUrl"])
        self.assertTrue(verified["signed"])
        self.assertEqual(verified["signaturePubkeyHex"], owner["pubkeyHex"])
        failure = self.raw("sign", created["url"], "--secret", "2" * 64, "--json")
        self.assertNotEqual(failure.returncode, 0)

    def test_editing_a_signed_link_requires_resigning(self):
        secret, owner, payload = self.signing_fixture()
        created = self.create("message", payload, "--sign-secret", secret)
        updated = self.update(created["url"], {"name": "Edited unsigned"})
        self.assertFalse(updated["signed"])
        self.assertFalse(self.cli("verify", updated["url"])["signed"])
        protected = self.update(created["url"], {"name": "Edited signed"}, "--sign-secret", secret)
        verified = self.cli("verify", protected["url"])
        self.assertTrue(verified["signed"])
        self.assertEqual(verified["signaturePubkeyHex"], owner["pubkeyHex"])

    def test_encryption_roundtrip_and_wrong_password(self):
        created = self.create("drop")
        password = "disposable test password"
        encrypted = self.cli("encrypt", created["url"], "--password", password)
        self.assertNotEqual(encrypted["encryptedUrl"], created["url"])
        decrypted = self.cli("decrypt", encrypted["encryptedUrl"], "--password", password)
        self.assertEqual(decrypted["fragment"], created["fragment"])
        self.assertEqual(self.cli("inspect", encrypted["encryptedUrl"], "--password", password)["site"]["siteType"], "drop")
        for options in ((), ("--password", "wrong password")):
            failure = self.raw("inspect", encrypted["encryptedUrl"], *options, "--json")
            self.assertNotEqual(failure.returncode, 0)

    def test_protected_update_requires_both_output_protection_options(self):
        secret, owner, payload = self.signing_fixture()
        password = "disposable test password"
        created = self.create("message", payload, "--sign-secret", secret, "--encrypt-password", password)
        unprotected = self.update(created["url"], {"name": "Plain draft"}, "--password", password)
        self.assertFalse(unprotected["encrypted"])
        self.assertFalse(unprotected["signed"])
        updated = self.update(
            created["url"], {"name": "Protected revision"}, "--password", password,
            "--sign-secret", secret, "--encrypt-password", password,
        )
        self.assertTrue(updated["encrypted"])
        verified = self.cli("verify", updated["url"], "--password", password)
        self.assertTrue(verified["signed"])
        self.assertEqual(verified["signaturePubkeyHex"], owner["pubkeyHex"])
        inspected = self.cli("inspect", updated["url"], "--password", password)
        self.assertEqual(inspected["site"]["name"], "Protected revision")
        failure = self.raw("inspect", updated["url"], "--json")
        self.assertNotEqual(failure.returncode, 0)

    def test_forum_publish_readback_and_salt_namespace_on_loopback_relay(self):
        relay = self.relay()
        forum = self.create("forum")
        post = {"title": "Loopback dispatch", "body": "Private test body — ação"}
        published = self.cli(
            "forum", "post", forum["url"], "--input", self.json_file(post),
            "--secret", "1" * 64, "--salt", "test-salt", "--relay", relay,
        )
        listed = self.cli("forum", "posts", forum["url"], "--salt", "test-salt", "--relay", relay)
        self.assertEqual(len(listed["posts"]), 1)
        entry = listed["posts"][0]
        self.assertEqual(entry["payload"]["t"], post["title"])
        self.assertEqual(entry["payload"]["b"], post["body"])
        self.assertEqual(entry["eventId"], published["event"]["id"])
        isolated = self.cli("forum", "posts", forum["url"], "--salt", "different-salt", "--relay", relay)
        self.assertEqual(isolated["posts"], [])
        events = self.relay_events(relay)
        self.assertEqual(len(events), 1)
        self.assertNotIn(post["body"], events[0]["content"])

    def test_rejected_publish_reports_failure_and_has_no_readback(self):
        relay = self.relay(reject=True)
        forum = self.create("forum")
        failure = self.raw(
            "forum", "post", forum["url"], "--input", self.json_file({"title": "Rejected"}),
            "--secret", "1" * 64, "--relay", relay, "--json",
        )
        self.assertNotEqual(failure.returncode, 0)
        self.assertTrue(failure.stderr.strip())
        self.assertEqual(self.cli("forum", "posts", forum["url"], "--relay", relay)["posts"], [])
        self.assertEqual(self.relay_events(relay), [])

    def test_private_recipient_requires_hex_and_rejects_other_public_encodings_before_publish(self):
        recipient = self.cli("pubkey", "--secret", "3" * 64)
        payload = json.loads((EXAMPLES / "forum.json").read_text())
        payload.update(name="Recipient formats", pubkey=recipient["pubkeyHex"])
        board = self.create("forum", payload)
        relay = self.relay()
        message = self.json_file({"message": "Private format check"})

        for encoding in ["npub", "nowherePubkey"]:
            with self.subTest(encoding=encoding):
                rejected = self.raw(
                    "forum", "private", "send", board["url"],
                    "--recipient-session-pubkey", recipient[encoding],
                    "--input", message, "--relay", relay, "--json",
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertEqual(self.relay_events(relay), [])

        sent = self.cli(
            "forum", "private", "send", board["url"],
            "--recipient-session-pubkey", recipient["pubkeyHex"],
            "--input", message, "--relay", relay,
        )
        # The fixture accepts only valid signatures; require the actual bytes,
        # not just an exit status or an event-shaped local response.
        self.assertEqual(self.relay_events(relay), [sent["event"]])
        self.assertEqual(sent["event"]["kind"], 21423)
        self.assertNotIn("Private format check", sent["event"]["content"])

    def test_torrent_recipe_enables_preflight_publication_and_duplicate_detection(self):
        relay = self.relay()
        payload = json.loads((EXAMPLES / 'forum-torrents.json').read_text())
        forum = self.create('forum', payload)
        content = b'public test document\n'
        torrent = self.work / 'archive.torrent'
        info = (b'd6:lengthi' + str(len(content)).encode() +
                b'e4:name11:archive.txt12:piece lengthi16384e6:pieces20:' +
                hashlib.sha1(content).digest() + b'e')
        torrent.write_bytes(b'd4:info' + info + b'e')
        options = ['--torrent-file', str(torrent), '--category', 'docs', '--relay', relay]
        checked = self.cli('forum', 'torrent', 'check', forum['url'], *options)
        self.assertTrue(checked['settings']['enabled'])
        self.assertIsNone(checked['duplicate'])
        published = self.cli('forum', 'torrent', 'publish', forum['url'], *options, '--secret', '1' * 64)
        duplicate = self.cli('forum', 'torrent', 'check', forum['url'], *options)
        self.assertEqual(duplicate['duplicate']['eventId'], published['event']['id'])
        self.assertEqual(len(self.relay_events(relay)), 1)

    def test_store_inventory_is_enabled_by_tag_presence_even_when_value_is_zero(self):
        relay = self.relay()
        payload = json.loads((EXAMPLES / 'store.json').read_text())
        payload['tags'] = [{'key': '$', 'value': 'AUD'},
                           {'key': 'j', 'value': 'seller@example.com'}]
        cart = self.json_file({'items': [{'i': 0, 'qty': 1}]})
        store = self.create('store', payload)
        quote = self.cli('store', 'checkout', 'quote', store['url'],
                         '--cart', cart, '--relay', relay)
        self.assertEqual(quote['inventory']['gate'], 'missing_status')
        self.assertTrue(quote['inventory']['enabled'])
        self.assertIn({'key': 'k', 'value': '1'}, store['siteData']['tags'])
        self.assertEqual(quote['methods'][0]['method']['id'], 'payid')
        gated = self.update(store['url'], {'tags': [*payload['tags'], {'key': 'k', 'value': '0'}]})
        quote = self.cli('store', 'checkout', 'quote', gated['url'],
                         '--cart', cart, '--relay', relay)
        self.assertTrue(quote['inventory']['enabled'])
        self.assertEqual(quote['inventory']['gate'], 'missing_status')
        self.assertEqual(self.relay_events(relay), [])

    def test_petition_required_fields_fail_before_relay_publication(self):
        relay = self.relay()
        petition = self.create("petition")
        failure = self.raw(
            "petition", "sign", petition["url"], "--input", self.json_file({"name": "Alex"}),
            "--secret", "1" * 64, "--relay", relay, "--json",
        )
        self.assertNotEqual(failure.returncode, 0)
        self.assertTrue(failure.stderr.strip())
        self.assertEqual(self.relay_events(relay), [])


if __name__ == "__main__":
    unittest.main()
