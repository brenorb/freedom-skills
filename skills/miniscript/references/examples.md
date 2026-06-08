# Sample Policies

Examples pulled from the shared `miniscript_policy_examples` sheet and cleaned for direct compiler use.

## 2FA fallback after 90 days

```text
and(pk(user),or(99@pk(service),older(12960)))
```

## Three-of-five plus treasurer

```text
and(pk(treasurer),thresh(3,pk(member_1),pk(member_2),pk(member_3),pk(member_4),pk(member_5)))
```

## Contest prize with puzzle preimage

```text
and(sha256(H),thresh(1,pk(participant_1),pk(participant_2),pk(participant_3),pk(participant_4),pk(participant_5),pk(participant_6)))
```

## Child account that unlocks solo spending at adulthood

```text
and(pk(child_key),thresh(1,pk(mother_key),pk(father_key),after(1856908800)))
```

## Business wallet with start date

```text
and(thresh(2,pk(key_1),pk(key_2),pk(key_3)),after(1704153600))
```

## Known bad policy: duplicate key across branches

```text
or(and(pk(A),pk(B)),and(pk(A),pk(C)))
```

The compiler should reject or mark this as insane; the skill must repair it before presenting a final answer.
