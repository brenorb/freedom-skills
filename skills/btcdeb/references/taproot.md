# Experimental Taproot construction

`tap` is btcdeb's companion utility. Upstream explicitly calls it experimental and warns against real bitcoin. Keep constructions and spending experiments on regtest/disposable fixtures.

Create a two-leaf tree with an existing 32-byte x-only internal public key:

```sh
tap "$internal_xonly_pubkey" 2 '[OP_1]' '[OP_2]'
```

The syntax is `tap [options] INTERNAL_KEY SCRIPT_COUNT SCRIPT1 ... [SPEND_INDEX [ARG1 ...]]`. Each Script is a quoted bracket expression or raw Script hex. Without spending arguments/transactions it generates the commitment: leaf hashes, branch/root, tweak, output key, and Bech32m address. Use a PTY for explanatory output: this revision quiets logs when stdin or stdout is non-TTY. `--addrprefix=bcrt` selects regtest explicitly; use the network requested by the user.

To construct the witness for leaf 0, append `0` and that leaf's satisfaction items in stack order. It outputs the selected script, control block, and witness construction. With `--tx=HEX --txin=HEX`, tap can insert that witness into the supplied spending transaction. Inspect `tap -h` for installed syntax before the transaction mutation path. `--sig=HEX` provides a signature; `--privkey=KEY` generates one only when the build supports dangerous key operations. Use only disposable keys and do not log secrets.

Do not confuse the internal key with the tweaked output key or a leaf key. Distinguish leaf index, spending transaction vin, and previous transaction vout. Preserve exact tree order and scripts when reproducing a control block; changing either can change the commitment.

Use `btcdeb` with both transactions to investigate commitment/sighash failures and then Core regtest for full transaction acceptance. A generated address/control block or successful mocked script does not prove a real spend. For multi-input Taproot context limitations read transactions.md.

Sources: [tap syntax/implementation](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/tap.cpp), [upstream regtest walkthrough](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/doc/tapscript-example-with-tap.md).
