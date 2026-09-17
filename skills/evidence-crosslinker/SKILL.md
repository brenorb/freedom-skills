---
name: evidence-crosslinker
description: Link related evidence items, claims, people, places, and events with provenance and confidence while avoiding unsupported identity matches.
---

# Evidence Crosslinker

Build a reviewable relationship map, not a database of guesses.

## Workflow

1. Define the case scope and allowed entities; assign stable IDs instead of
   copying sensitive names into every note.
2. Extract explicit relationships from evidence: same URL, quoted document,
   matching timestamp, stated location, or direct reference.
3. Label each link as direct, corroborated, inferred, or unresolved and attach
   the exact source item and page/frame/time offset.
4. Surface contradictions and alternative explanations. Do not merge people or
   events solely on a name, face, username, or approximate location.
5. Export a human-readable link table and keep the underlying evidence access-
   controlled.

Avoid unnecessary graph enrichment and do not expose a sensitive relationship
map to a broader audience than the evidence owner approved.

## Minimal check

Every exported edge can be traced back to a specific source span or is clearly
marked as an inference.
