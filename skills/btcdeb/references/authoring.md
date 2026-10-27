# Authoring, compilation, and transforms

Write the stack contract first: initial values in bottom-to-top order, unlocking inputs, branch selector, intended final state, and Script version. Compile with `btcc` and execute with `btcdeb`; compilation alone does not check contract satisfaction.

```sh
script_hex=$(btcc OP_4 OP_5 OP_ADD OP_9 OP_EQUAL)
printf '0x%s\n' "$script_hex" | btcdeb
printf '%s\n' '[OP_SHA256 sha256(hello) OP_EQUAL]' | btcdeb hello
```

`0x` selects serialized-hex parsing; it adds no Script byte. Keep saved bare-hex files unchanged and prefix only debugger input.

For a hash lock, test a wrong preimage as well. For signatures see transactions.md rather than treating `OP_CHECKSIG` as a hash comparison.

## Parsing and byte fidelity

- A quoted bracket expression `'[OP_3 OP_ADD]'` is readable Script for btcdeb.
- A hex string such as `0x5393` is already serialized Script when used as the Script argument/stdin line, not a readable sequence of pushes.
- `btcc OP_3 OP_ADD` compiles instructions. Passing a whole bracket expression to btcc instead serializes that expression as one value; do not assume the two forms are interchangeable.
- Decimal `10` is a number, not byte `0x10`. Unknown words can become literal UTF-8 data rather than raising an unknown-opcode error. Inspect output when spelling opcodes.
- `Value::operator>>` normalizes data shorter than five bytes through Script-number encoding. Thus even `0x` inside a readable Script does not promise an identical byte push. When nonminimal encodings, leading zeroes, or signed-number bytes are the subject, supply exact raw Script hex; byte-sensitive input data can be passed as initial-stack arguments.

Keep shell quoting around brackets, whitespace, and inline function parentheses. Do not put private keys into examples or logs except explicit disposable test keys needed by the task.

## Transforms

`tf` is a debugger command, not a separate executable. In a PTY run `btcdeb`, then:

```text
tf -h
tf sha256 hello
tf hash160 hello
tf reverse 0x01020304
tf int 0x11
tf tagged-hash TapLeaf 0x1234
```

Exit with Ctrl-D; `quit` is not a registered debugger command.

The installed help gives exact argument order and separate inline names. Available families include `sha256`, `ripemd160`, `hash160`, `hash256`, `hex`, `int`, `reverse`, `base58chk-encode/decode`, `bech32-encode/decode`, `bech32m-encode`, `tagged-hash`, public-key operations, and signature verification over a supplied digest. Hashing `hello` uses text bytes. Hex-looking `cafe` is parsed as bytes even without `0x`; for its four ASCII characters use `0x63616665`, distinct from `0xcafe`. Shell/REPL quoting does not force text typing. Inline `sha256("cafe")` includes quote bytes; use explicit byte hex.

For noninteractive hashing, an inline expression can push the digest:

```sh
printf '%s\n' '[sha256(0x63616665)]' | btcdeb
```

Inline operator names may differ (`tagged_hash` versus `tagged-hash`) and multi-argument calls require a bracket expression, not comma syntax; consult `tf -h`. Signing/private-key transforms require a build configured with `--enable-dangerous`; absence is a build capability, not a contract bug. A digest-level `verify-sig` result does not itself prove the digest matches a transaction's sighash.

Sources: [compiler](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/btcc.cpp), [value parsing/serialization](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/value.h), [transform registry](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/functions.cpp).
