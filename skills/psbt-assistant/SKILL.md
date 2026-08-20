---
name: psbt-assistant
description: Inspect, explain, and safely prepare Bitcoin PSBT workflows while keeping signing decisions with the authorized human or hardware wallet.
---

# PSBT Assistant

Make a proposed transaction legible before anyone signs it.

## Workflow

1. Decode the PSBT with a trusted local tool and identify inputs, outputs,
   amounts, fees, change, locktime, sequence, scripts, and required signers.
2. Match each input to its known wallet policy and verify output addresses and
   amounts through an independent channel when possible.
3. Explain fee rate, change detection, privacy impact, RBF/locktime behavior,
   and missing or partial signatures in plain language.
4. Ask for confirmation immediately before exporting, signing, broadcasting,
   or modifying the PSBT. Do not infer approval from an earlier discussion.
5. After signing/broadcast, verify the resulting txid and preserve the final
   PSBT/transaction relationship without collecting private keys.

Never sign a PSBT merely because it parses or has enough signatures.

## Minimal check

The human-readable summary matches the decoded PSBT's inputs, outputs, fee,
and signer requirements.
