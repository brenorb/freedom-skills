# Official Miniscript Reference

Primary sources used by this skill:

- Official Miniscript reference and demo compiler: https://bitcoin.sipa.be/miniscript/
- `@bitcoinerlab/miniscript-policies` README: the package exposes the reference C++ policy compiler from `sipa/miniscript` in JavaScript and preserves the upstream compiler behavior for P2WSH.
- `@bitcoinerlab/miniscript` README: analysis, ASM compilation, and satisfier support.

## Supported policy primitives

These are the policy functions documented on the official Miniscript site and expected by the skill's compiler flow:

- `pk(NAME)`: require a named public key to sign.
- `after(NUM)`: absolute timelock via `nLockTime`.
- `older(NUM)`: relative timelock via `nSequence`.
- `sha256(HEX)`, `hash256(HEX)`: require a 64-character hash preimage.
- `ripemd160(HEX)`, `hash160(HEX)`: require a 40-character hash preimage.
- `and(POL,POL)`: both subpolicies must be satisfied.
- `or([N@]POL,[N@]POL)`: one of two subpolicies must be satisfied, with optional relative likelihood weights.
- `thresh(NUM,POL,POL,...)`: require `NUM` satisfied subpolicies.

## Practical rules

- `older(NUM)` and `after(NUM)` must use positive integers.
- `after(NUM)` values below `500000000` are interpreted as block heights; larger values are interpreted as Unix timestamps.
- Duplicate keys across competing branches often produce insane or uncompilable policies, even when the boolean logic looks reasonable.
- `thresh(1, ...)` is logically equivalent to an `or(...)` over all branches.
- `thresh(N, ...)` where `N` equals the number of branches is logically equivalent to an `and(...)` of all branches.
