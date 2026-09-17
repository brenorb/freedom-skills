---
name: miniscript
description: Use this skill when the user wants to write, explain, correct, compare, compile, or visualize Bitcoin Miniscript policies or related spending conditions.
---

# miniscript

Use this skill for Bitcoin Miniscript work. It is based on the original Code Satoshi / Minimaxis prompt direction, but it is stricter about verification: every candidate policy must be compiled before you present it as final.

## Default workflow

1. Read `references/system-prompt.md` and `references/official-reference.md` for the behavior and the allowed policy primitives.
2. If the user is describing a wallet or contract in plain English, draft the candidate policy using only:
   - `pk`, `after`, `older`, `sha256`, `hash256`, `ripemd160`, `hash160`, `and`, `or`, `thresh`
3. Always run the compiler before presenting the policy:

```bash
cd skills/miniscript
npm install
node scripts/compile_policy.mjs --policy 'and(pk(user),or(99@pk(service),older(12960)))'
```

4. If the user already supplied a Miniscript expression, validate and analyze it directly:

```bash
cd skills/miniscript
node scripts/compile_policy.mjs --miniscript 'and_v(v:pk(user),or_d(pk(service),older(12960)))'
```

5. If the compiler output is not sane or returns an error marker, repair the policy and re-run the compiler. Do not present a broken policy as final.
6. When the user wants to inspect the logic visually, render both a simplified and an audit view:

```bash
cd skills/miniscript
python3 scripts/minimermaid.py 'and(pk(user),or(99@pk(service),older(12960)))' --html /tmp/miniscript-simplified.html
python3 scripts/minimermaid.py 'and(pk(user),or(99@pk(service),older(12960)))' --audit --html /tmp/miniscript-audit.html
```

7. Tell the user where the preview files were written when you generate them.

## Output expectations

- Explain the policy in plain English.
- Include the compiled Miniscript and sane/insane status.
- Include ASM when available.
- Mention timelock units explicitly: `after` is absolute, `older` is relative.
- If the user asked for education or debugging, include the Mermaid preview path.

## Defaults

- Prefer `thresh` when it expresses the logic more directly than deeply nested `or(...)`.
- Prefer compiler-confirmed fixes over speculative fixes.
- Prefer showing both the high-level policy and the compiled Miniscript.
- Preserve the user’s key names and hash tokens exactly; do not silently lowercase them.

## Commands

- `node scripts/compile_policy.mjs --policy '<policy>'`
- `node scripts/compile_policy.mjs --policy '<policy>' --context taproot`
- `node scripts/compile_policy.mjs --miniscript '<miniscript>'`
- `python3 scripts/minimermaid.py '<policy>' --html /tmp/miniscript.html`
- `npm test`

## Gotchas

- Boolean equivalence does not guarantee compiler sanity. Duplicate keys across competing branches are a common failure mode.
- `after(NUM)` uses block height below `500000000` and Unix time at or above it.
- Weighted `or` branches like `99@pk(service)` are valid in policy compilation but the visualizer strips only the weight, not the branch itself.
- The visualizer is for policy-level Miniscript syntax, not low-level wrapper-rich Miniscript such as `and_v(...)`.
