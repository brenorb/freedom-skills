from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()
