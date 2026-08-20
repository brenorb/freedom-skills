---
name: abuse-pattern-mapper
description: Group documented incidents by time, place, method, unit, or actor while separating observed patterns from inference and protecting sensitive identities.
---

# Abuse Pattern Mapper

Find repeated features in documented incidents without turning correlation into
accusation.

## Workflow

1. Define case scope, safe identifiers, time/location precision, and the minimum
   attributes needed for the question.
2. Normalize incident records and attach source IDs, confidence, consent, and
   uncertainty; preserve original wording and raw records separately.
3. Group by explicit features such as date range, method, location, reported
   unit, or recurring description. Mark inferred links separately.
4. Test alternative explanations, missing-data bias, duplicate reports, and
   geographic or survivor-access distortions.
5. Export an anonymized pattern summary with counts, gaps, source links, and a
   warning that it is not a legal finding of responsibility.

Do not expose exact survivor locations or identify people from weak clusters.

## Minimal check

Every reported pattern includes its inclusion rule, denominator, source count,
and uncertainty/alternative explanation.
