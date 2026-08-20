---
name: information-verifier
description: Verify a public claim or document by separating assertions, triangulating sources, checking dates and provenance, and reporting uncertainty.
---

# Information Verifier

Produce an evidence-led verification brief instead of a binary confidence
guess.

## Workflow

1. Split the input into atomic claims and mark what would make each claim true,
   false, or unresolved.
2. Prefer primary documents, direct statements, archived originals, and
   independently collected records over commentary or screenshots.
3. Check source identity, publication date, revision history, incentives,
   copied wording, and whether two sources actually depend on one another.
4. Record supporting and contradicting evidence for each claim, with links and
   capture dates. Use `mirror-finder` when the original is unavailable.
5. Label each result `supported`, `contradicted`, `mixed`, or `unresolved`, and
   state the next observation that would change the conclusion.

Do not call an item verified because several outlets repeat the same source.
Preserve the user's privacy when researching sensitive people, locations, or
documents.

## Minimal check

Every `supported` or `contradicted` claim must have a named source and a reason
it is independent or primary.
