---
name: btcdeb
description: Write, compile, execute, and debug Bitcoin Script with btcdeb, btcc, and tap; inspect stacks, hashes, signature context, verification flags, and experimental Taproot constructions. Use for Bitcoin Script tooling and lesson checks, not wallet management.
metadata:
  version: "0.1.0"
  repository: "https://github.com/bitcoin-core/btcdeb"
---

# Bitcoin Script with btcdeb

Start with the requested action. For example, execute an expression through completion:

```sh
printf '%s\n' '[OP_3 OP_DUP OP_ADD OP_6 OP_EQUAL]' | btcdeb
```

Or compile readable Script:

```sh
btcc OP_3 OP_DUP OP_ADD OP_6 OP_EQUAL
```

Run commands, inspect actual output, and report what was demonstrated. Preserve the user's Script version and verification assumptions. If the executable fails to launch, use the conditional setup guidance in [references/runtime.md](references/runtime.md); do not begin every task with installation checks.

## Select the task reference

Read only what the task needs:

- Run to completion, test positive/negative cases, explain an error, or inspect a branch with `step`, `rewind`, `stack`, `altstack`, and `vfexec`: [references/execution.md](references/execution.md).
- Write a contract, compile Script bytes, hash/encode data, or use `tf`: [references/authoring.md](references/authoring.md).
- Check real signatures, load transactions, select an input, inspect sighashes, or compare flags and Script versions: [references/transactions.md](references/transactions.md).
- Construct a Taproot tree, address, control block, or witness using experimental `tap`: [references/taproot.md](references/taproot.md).

## Essentials that change the result

**Non-TTY stdin is Script input.** In shell automation, pipe the single-line Script into `btcdeb`; positional arguments then supply the initial stack, bottom first. Do not pipe debugger commands like `step`. For interactive commands, allocate a PTY with both stdin and stdout attached. Either stream being non-TTY enables automatic execution. See the execution reference before mixing transaction options with pipes.

**Completion is not spend validity.** Record exit status, errors, final stack, and assumptions separately. An ordinary standalone Script can finish with exit status zero while leaving false or an empty stack. `01` is true; an empty byte vector and negative zero are false. A valid spend also depends on final-stack rules, transaction context, applicable consensus rules, and policy. btcdeb's copied interpreter is not a current Bitcoin Core consensus oracle.

**Bytes and numbers differ.** Use `OP_1`…`OP_16` for small opcodes, decimal tokens for Script numbers, and `0x` for hex data. btcc's compiler may normalize short byte pushes; use raw serialized Script when exact push encoding matters. See authoring.

**Mock signatures prove only the mocked path.** `--pretend-valid` skips cryptographic and encoding checks for the specified pairs. Never describe a mocked run as signature verification. Do not enable disabled opcodes or remove verification flags just to make a purported Bitcoin spend pass.

Examples were checked with btcdeb `5.0.24` from Nixpkgs (package label `0.3.20-unstable-2024-04-09`), source revision `e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7`. Prefer bundled references and installed help for offline tasks; use upstream links only when internet access is permitted.
