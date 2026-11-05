# Execution and debugging

## Batch execution

```sh
printf '%s\n' '[OP_ADD OP_7 OP_EQUAL]' | btcdeb 3 4
```

The first stdin line is the Script. Remaining argv items are initial stack entries, bottom to top. Raw stdout prints final stack entries bottom to top, one hex entry per line; an empty item prints a blank line. Capture stderr and exit status too. Parse/initialization/interpreter errors return nonzero, but a successfully completed ordinary Script can return zero with a false top item. The last output line is the top; preserve blank lines. An empty stack differs from one empty item.

Non-TTY stdin **overrides the positional Script argument**, which becomes a stack item instead. Avoid `btcdeb '[...]' </dev/null` and `printf 'step\n' | btcdeb '[...]'`. The latter tries to execute `step` as Script input. stdin reads one line into a 1024-byte buffer; keep each stdin Script line within 1023 bytes, or use a real TTY for longer positional input. Serialized hex is an alternative only if it fits that limit. Do not silently accept truncation.

For transaction auto-configuration under a non-TTY runner, send a blank line and omit positional arguments:

```sh
printf '\n' | btcdeb --tx="$spending_hex" --txin="$previous_hex" --select=0
```

This permits an empty explicit Script and lets transaction setup derive the actual Script and stack. Do not use empty EOF as a substitute: this revision's input-reading path expects a line.

For tests, exercise satisfying and failing inputs, branches, and meaningful boundaries. Distinguish:

- execution failure (e.g. stack underflow or `OP_VERIFY` failure),
- successful evaluation with false top (e.g. failed `OP_EQUAL`),
- true top with additional items (may violate clean-stack rules),
- a complete context-aware spend check.

Bitcoin Script truth is any nonzero byte except the final sign-bit-only negative-zero representation; `00`, `80`, and empty bytes are false. Do not compare arbitrary true values only to `01` unless the task requires that exact output.

## Interactive debugging

Start in a real terminal or an exec tool with `tty: true`:

```sh
btcdeb '[OP_3 OP_TOALTSTACK OP_4 OP_FROMALTSTACK OP_ADD]'
```

At `btcdeb>` use:

| Command | Purpose |
| --- | --- |
| `step` | Execute the next instruction; empty Enter repeats the previous command |
| `rewind` | Undo an instruction to compare the prior state |
| `stack` | Full main stack, top labeled `<01>` |
| `altstack` | Alternate stack |
| `vfexec` | Conditional execution state |
| `print` | Script listing and current position |
| `exec OP_DUP` | Execute an ad hoc operation, changing the current stack |
| `help` | Installed debugger command list |

The initial display is before execution. Capture states around the relevant instruction. Keep stepping through finalization; the last opcode display alone does not prove completion. There is no registered `run` or `continue` debugger command in this revision; for full execution use batch mode rather than inventing one. Exit with Ctrl-D.

After exploratory `exec` mutations or complex rewinds across branches/phases, rerun the original script from a fresh process to verify the proposed correction. Explain the first causal error and show the corrected execution, preserving the user's intended contract.

Sources: [debugger guide](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/doc/btcdeb.md), [stdin/batch implementation](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/btcdeb.cpp), [completion semantics](https://github.com/bitcoin-core/btcdeb/blob/e2c2e7b9fe2ecc0884129b53813a733f93a6e2c7/debugger/interpreter.cpp).
