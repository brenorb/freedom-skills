from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from contextlib import redirect_stdout
import io
import json
import subprocess
import tempfile
from unittest.mock import patch
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "query_addresses.py"
SPEC = spec_from_file_location("bitcoin_pir_query_addresses", MODULE_PATH)
MODULE = module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


SAMPLE_STDOUT = """=== Address → PIR script hash (HASH160(scriptPubKey)) ===
  1D4HSHPJxoPLqiBNFNarz34dcWPLvpiaeb
    scriptPubKey : 76a91484407a2fe50de7b97ef1a80613b41d06af8fa38788ac
    script_hash  : de2e69f96b7e622f6ad39609b6d8554b37e8aba3
  bc1q2292d7mz8txc7462hjy4prs2gtx727ut8mcanr
    scriptPubKey : 0014528aa6fb623acd8f574abc89508e0a42cde57b8b
    script_hash  : 1f4e88358fd778cde7f3aa8d1b257ceb7e800a3b

Connecting: wss://weikeng1.bitcoinpir.org / wss://weikeng2.bitcoinpir.org
Catalog: 2 database(s):
  [0] main Full height=948454 index_bins=567558 chunk_bins=1066928
  [1] delta_940611_948454 Delta { base_height: 940611 } height=948454 index_bins=53287 chunk_bins=112344

Synced to height 948454

=== 1D4HSHPJxoPLqiBNFNarz34dcWPLvpiaeb (de2e69f96b7e622f6ad39609b6d8554b37e8aba3) ===
  merkle_verified : true
  is_whale        : false
  UTXO count      : 1
  total balance   : 1600 sats
    951fb4c4c3d1dbb502c7cd0e7efcdd1ec371fed5fedfbcd3b443ad57b95bb43d:373 = 1600 sats

=== bc1q2292d7mz8txc7462hjy4prs2gtx727ut8mcanr (1f4e88358fd778cde7f3aa8d1b257ceb7e800a3b) ===
  merkle_verified : true
  is_whale        : false
  UTXO count      : 1
  total balance   : 12900 sats
    6a49bbed365ad8f46712710f9e334126304c7ff3d9116f27d029b7ef6ed735d6:1 = 12900 sats
"""


class QueryAddressesTests(unittest.TestCase):
    def test_parse_fetch_addresses_output(self):
        payload = MODULE.parse_fetch_addresses_output(SAMPLE_STDOUT)

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["synced_height"], 948454)
        self.assertEqual(payload["catalog_count"], 2)
        self.assertEqual(
            payload["servers"],
            [
                "wss://weikeng1.bitcoinpir.org",
                "wss://weikeng2.bitcoinpir.org",
            ],
        )
        self.assertEqual(
            payload["queries"][0]["address"],
            "1D4HSHPJxoPLqiBNFNarz34dcWPLvpiaeb",
        )
        self.assertTrue(payload["queries"][0]["merkle_verified"])
        self.assertEqual(payload["queries"][0]["utxos"][0]["vout"], 373)
        self.assertEqual(payload["queries"][1]["total_balance_sats"], 12900)

    def test_find_unsupported_queries_rejects_txids_outpoints_and_xpubs(self):
        unsupported = MODULE.find_unsupported_queries(
            [
                "951fb4c4c3d1dbb502c7cd0e7efcdd1ec371fed5fedfbcd3b443ad57b95bb43d",
                "951fb4c4c3d1dbb502c7cd0e7efcdd1ec371fed5fedfbcd3b443ad57b95bb43d:373",
                "xpub661MyMwAqRbcF7ExamplePayload",
                "bc1q2292d7mz8txc7462hjy4prs2gtx727ut8mcanr",
            ]
        )

        self.assertEqual(
            unsupported,
            [
                "951fb4c4c3d1dbb502c7cd0e7efcdd1ec371fed5fedfbcd3b443ad57b95bb43d",
                "951fb4c4c3d1dbb502c7cd0e7efcdd1ec371fed5fedfbcd3b443ad57b95bb43d:373",
                "xpub661MyMwAqRbcF7ExamplePayload",
            ],
        )


class RepositoryLayoutTests(unittest.TestCase):
    def make_repo(self, root, layout="crates/sdk/client"):
        root.mkdir(parents=True, exist_ok=True)
        (root / "Cargo.toml").write_text('[workspace]\nmembers = ["' + layout + '"]\n')
        example = root / layout / "examples" / "fetch_addresses.rs"
        example.parent.mkdir(parents=True)
        example.write_text("fn main() {}\n")
        return root

    def test_supplied_current_and_legacy_checkouts_are_reused_without_changes(self):
        for layout in ["crates/sdk/client", "pir-sdk-client"]:
            with self.subTest(layout=layout), tempfile.TemporaryDirectory() as d:
                root = self.make_repo(Path(d) / "user-checkout", layout)
                marker = root / "user-work.txt"
                marker.write_text("keep this work")
                with patch.object(MODULE, "run") as run:
                    self.assertEqual(MODULE.ensure_repo(root), root)
                    run.assert_not_called()
                self.assertEqual(marker.read_text(), "keep this work")

    def test_fresh_current_clone_and_second_cached_invocation_share_validation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "cache" / "upstream"

            def clone(cmd, **kwargs):
                self.assertEqual(cmd[:4], ["git", "clone", "--depth", "1"])
                self.assertEqual(cmd[-2:], [MODULE.UPSTREAM_REPO_URL, str(root)])
                self.make_repo(root)
                return subprocess.CompletedProcess(cmd, 0, "", "")

            with patch.object(MODULE, "run", side_effect=clone) as run:
                self.assertEqual(MODULE.ensure_repo(root), root)
                self.assertEqual(MODULE.ensure_repo(root), root)
                self.assertEqual(run.call_count, 1)

    def test_invalid_existing_directory_is_preserved_and_not_cloned_over(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            marker = root / "user-work.txt"
            marker.write_text("keep this work")
            with patch.object(MODULE, "run") as run:
                with self.assertRaisesRegex(MODULE.QueryAddressesError, "does not look like Bitcoin-PIR"):
                    MODULE.ensure_repo(root)
                run.assert_not_called()
            self.assertEqual(marker.read_text(), "keep this work")

    def test_invalid_new_clone_is_rejected_on_its_first_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve() / "upstream"

            def clone(cmd, **kwargs):
                root.mkdir()
                (root / "Cargo.toml").write_text("[workspace]\n")
                return subprocess.CompletedProcess(cmd, 0, "", "")

            with patch.object(MODULE, "run", side_effect=clone):
                with self.assertRaisesRegex(MODULE.QueryAddressesError, "expected Cargo.toml and fetch_addresses.rs"):
                    MODULE.ensure_repo(root)
            self.assertTrue((root / "Cargo.toml").is_file())

    def test_directories_cannot_masquerade_as_required_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "Cargo.toml").mkdir()
            (root / "crates/sdk/client/examples/fetch_addresses.rs").mkdir(parents=True)
            with self.assertRaises(MODULE.QueryAddressesError):
                MODULE.ensure_repo(root)

    def test_main_fresh_and_cached_runs_keep_the_cargo_and_json_contract(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d).resolve() / "upstream"
            commands = []
            # Host names are not fixed by the parser. This second endpoint is
            # the default in upstream fetch_addresses.rs at 0f57b114.
            current_output = SAMPLE_STDOUT.replace(
                "wss://weikeng2.bitcoinpir.org",
                "wss://bitcoin-pir-weikeng-laptop.chenweikeng.com",
            )

            def run(cmd, **kwargs):
                commands.append(cmd)
                if cmd[0] == "git":
                    self.make_repo(root)
                    return subprocess.CompletedProcess(cmd, 0, "", "")
                self.assertEqual(cmd[:7], ["cargo", "run", "--release", "-p", "pir-sdk-client", "--example", "fetch_addresses"])
                self.assertEqual(kwargs["cwd"], root)
                return subprocess.CompletedProcess(cmd, 0, current_output, "")

            argv = [str(MODULE_PATH), "--upstream-dir", str(root), "1D4HSHPJxoPLqiBNFNarz34dcWPLvpiaeb"]
            with patch.object(MODULE, "run", side_effect=run), patch("sys.argv", argv):
                results = []
                for _ in range(2):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        self.assertEqual(MODULE.main(), 0)
                    results.append(json.loads(output.getvalue()))
            self.assertEqual([c[0] for c in commands], ["git", "cargo", "cargo"])
            self.assertEqual(results[0], results[1])
            self.assertEqual(results[1]["repo_dir"], str(root))
            self.assertTrue(results[1]["queries"][0]["merkle_verified"])
            self.assertEqual(results[1]["queries"][0]["utxos"][0]["amount_sats"], 1600)
            self.assertEqual(results[1]["servers"][1], "wss://bitcoin-pir-weikeng-laptop.chenweikeng.com")

    def test_current_output_shape_preserves_not_found_results(self):
        header = "=== bc1q2292d7mz8txc7462hjy4prs2gtx727ut8mcanr (1f4e88358fd778cde7f3aa8d1b257ceb7e800a3b) ==="
        output = SAMPLE_STDOUT.split(header)[0] + header + "\n  (not found)\n"
        payload = MODULE.parse_fetch_addresses_output(output)
        self.assertTrue(payload["queries"][0]["found"])
        self.assertFalse(payload["queries"][1]["found"])
        self.assertEqual(payload["queries"][1]["utxos"], [])


if __name__ == "__main__":
    unittest.main()
