# Signatures, transaction context, and flags

## Load the actual spend

With hex provided by the user or local fixtures, use a PTY:

```sh
btcdeb --tx="$spending_hex" --txin="$previous_hex" --select=0
```

`--tx` is the entire spending transaction hex. `--txin` is the entire previous transaction whose output is being spent, not its txid, input index, or isolated scriptPubKey. Omit explicit Script/stack arguments to let btcdeb derive them from the transactions. `--select` is the zero-based **vin index in the spending transaction**; its outpoint supplies the previous vout index. Without `--select`, btcdeb takes the first input matching that previous txid. For batch execution see execution.md's blank-stdin recipe.

For a manually supplied Script and stack, `--tx=amount1,amount2:HEX` supplies input amounts in **BTC decimal units**, in vin order, for witness signature hashing. Legacy signature checks do not require the witness amounts. When both transactions are provided, the selected previous output supplies its amount automatically. A missing context or wrong amount can explain signature failure; do not replace it with a mock and call the original fixed.

Multi-input Taproot deserves special care: this revision only initializes the complete spent-output vector when the spending transaction has one input. Supplying a comma list of amounts alone does not provide all Taproot prevout scripts. Report unsupported/missing context instead of claiming arbitrary multi-input Taproot verification.

To inspect signing/sighash details with TTY stdin:

```sh
btcdeb --debug=sighash,signing --tx="$spending_hex" --txin="$previous_hex" --select=0
```

Stepping reveals hashing and signature decisions. This revision configures debug channels only when stdin is a TTY. To run through automatically while keeping debug, use a terminal with stdout redirected to a file (and capture stderr separately). Piping a Script into stdin suppresses that debug setup; do not infer absence of hashing from missing logs.

## Deliberately mocked exercises

```sh
printf '%s\n' '[sig1 pub1 OP_CHECKSIG]' | btcdeb --pretend-valid=sig1:pub1
```

Multiple permitted pairs are comma-separated. Mocks skip signature cryptography and encoding checks; identify them explicitly in the result. Use them to isolate spending logic only when that is the intended question.

## Rules and versions

```sh
btcdeb --default-flags
printf '%s\n' '[OP_1]' | btcdeb --modify-flags='+MINIMALIF,-NULLDUMMY'
```

The latter demonstrates flag syntax, not a recommended rule set. Changes start from btcdeb's standard defaults, take comma-separated `+FLAG`/`-FLAG` names, and should be justified by the task. Record the change and compare the same script/inputs. `--allow-disabled-opcodes` enables experimental operations; it does not make them valid Bitcoin operations.

Verification flags do not select the signature version. A standalone readable script defaults to the base execution context; it is not automatically Tapscript because it contains an x-only key. Transaction-derived context configures witness/Taproot phases. Specify legacy, SegWit v0, or Taproot and distinguish consensus from relay policy when explaining outcomes.

For a complete spend acceptance claim, use a suitable Bitcoin Core regtest environment and `testmempoolaccept` without broadcasting. Explain missing/spent inputs or policy rejection separately from Script failure. Do not claim network acceptance from btcdeb's exit code or true stack alone.

Sources: [signature guide](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/doc/btcdeb.md), [transaction/context implementation](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/instance.cpp), [mock behavior](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/doc/mock-values.md).
