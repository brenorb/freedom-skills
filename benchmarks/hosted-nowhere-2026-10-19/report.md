# Hosted Nowhere acceptance results

Gate: **54/54 passed**; eligible to push.

Frozen skill SHA-256: `4e07e081100a8e2ca5e0a1ea57231f39a8597fd4aba76b69404ca75e14d79155`.

First recorded attempt in this final acceptance matrix: 46/54. Infrastructure/capacity failures on first attempts: 0. Operator interruptions on first attempts: 3. Replayed cells: 17. Earlier failures remain in results.json; a replay is a fresh unassisted session. Earlier revision results qualify only through an explicit audit of all tool inputs proving their loaded instruction files and content-search outputs are unchanged. Original source hashes and trace-bound audit records remain in results.json.

Audited unchanged-input cells: 51. Changed app references are retested freshly on all three runners; unaffected cases require the recorded instruction-input audit.

Each cell is a fresh session. A pass requires deterministic app/CLI/relay checks and primary-agent review of its final account. Raw traces remain outside the repository under `/private/tmp/hosted-nowhere-e2e/runs`; runner state and auth files are not exported.

| Story | Luna High | Claude Haiku | SOMP Qwen |
| --- | --- | --- | --- |
| N01 Create and revise a message | PASS | PASS | PASS |
| N02 Publish multiline code as a Drop | PASS | PASS | PASS |
| N03 Create an event poster | PASS | PASS | PASS |
| N04 Donation methods and test invoice | PASS | PASS | PASS after replay |
| N05 Render SVG artwork | PASS after replay | PASS | PASS after replay |
| N06 Petition signatures, constraints, owner review and CSV | PASS after replay | PASS after replay | PASS after replay |
| N07 Forum posts, replies, moderation and salt isolation | PASS after replay | PASS after replay | PASS after replay |
| N08 Torrent authoring, duplicate preflight and replies | PASS after replay | PASS after replay | PASS after replay |
| N09 Ephemeral chat, private messages and rooms | PASS after replay | PASS after replay | PASS after replay |
| N10 Deprecated Store experiment and seller operations | PASS | PASS | PASS |
| N11 Preserve signing and encryption through an update | PASS | PASS | PASS |
| N12 Unsigned verification and wrong-key recovery | PASS | PASS | PASS |
| N13 Array patching without unrelated data loss | PASS | PASS | PASS |
| N14 Malformed input recovery and title-only validation | PASS | PASS | PASS |
| N15 Rejected relay publish without blind retries | PASS after replay | PASS after replay | PASS |
| N16 Use the live browser builder and regenerate the final share link | PASS | PASS | PASS |
| N17 Reader tip methods and a test invoice | PASS | PASS | PASS |
| N18 Remote NIP-46 signer for creation and updates | PASS | PASS | PASS |

See [protocol.md](protocol.md) for runner isolation, controlled service boundaries, and the meaning of a pass. TEST_ONLY invoice generation is not real payment settlement; relay acceptance is not a promise of retention or recipient delivery.

Scenario wording revisions (fresh selected runs required):
- N15: The original unquoted title boundary was ambiguous: two fresh Haiku sessions treated against the rejecting relay as title text. Quote Rejected trial explicitly. Only raw task wording changes; expected behavior and assertions do not. Retest N15 freshly on all three models; retain prior attempts without presenting them as identical-prompt outcomes.
